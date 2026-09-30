import datetime
import json
import os
import socket
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Dict, List, Optional

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

try:
    from src.anomaly_engine import anomaly_detector
    from src.traffic_logger import traffic_logger
except ImportError:
    from anomaly_engine import anomaly_detector
    from traffic_logger import traffic_logger

class TokenBucketRateLimiter:
    def __init__(self, capacity: int = 40, refill_rate_per_sec: float = 20.0):
        self.capacity = capacity
        self.refill_rate = refill_rate_per_sec
        self.tokens = float(capacity)
        self.last_refill = time.time()
        self.lock = threading.Lock()
        self.enabled = False

    def allow_request(self) -> bool:
        if not self.enabled:
            return True
        with self.lock:
            now = time.time()
            elapsed = now - self.last_refill
            self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
            self.last_refill = now

            if self.tokens >= 1.0:
                self.tokens -= 1.0
                return True
            return False

class ServerState:
    def __init__(self):
        self.lock = threading.Lock()
        self.active_connections = 0
        self.max_connections = 25
        self.active_workers = 0
        self.max_workers = 10
        self.total_requests = 0
        self.dropped_503 = 0
        self.rate_limited_429 = 0
        self.slowloris_suspects = 0
        self.start_time = time.time()
        self.requests_last_sec = 0
        self.current_rps = 0.0

    def try_acquire_worker(self, timeout_sec: float = 0.08) -> bool:
        start = time.time()
        while time.time() - start < timeout_sec:
            with self.lock:
                if self.active_workers < self.max_workers:
                    self.active_workers += 1
                    self.total_requests += 1
                    self.requests_last_sec += 1
                    return True
            time.sleep(0.01)
        with self.lock:
            self.dropped_503 += 1
            self.total_requests += 1
            self.requests_last_sec += 1
        return False

    def release_worker(self):
        with self.lock:
            if self.active_workers > 0:
                self.active_workers -= 1

server_state = ServerState()
rate_limiter = TokenBucketRateLimiter(capacity=40, refill_rate_per_sec=20.0)

def _rps_calculator_worker():
    while True:
        time.sleep(1.0)
        with server_state.lock:
            server_state.current_rps = float(server_state.requests_last_sec)
            server_state.requests_last_sec = 0

threading.Thread(target=_rps_calculator_worker, daemon=True).start()

HTML_DASHBOARD = r"""<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ağ Güvenliği ve Trafik İzleme Merkezi (SOC Dashboard)</title>
    <style>
        :root {
            --bg: #090d16;
            --card: #111827;
            --border: #1f2937;
            --primary: #0284c7;
            --accent: #38bdf8;
            --text: #f3f4f6;
            --muted: #9ca3af;
            --success: #22c55e;
            --warning: #f59e0b;
            --danger: #ef4444;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background: var(--bg); color: var(--text); padding: 20px; line-height: 1.5; }
        .container { max-width: 1200px; margin: 0 auto; }
        header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; border-bottom: 1px solid var(--border); padding-bottom: 15px; }
        h1 { font-size: 1.6rem; color: var(--accent); display: flex; align-items: center; gap: 10px; }
        .subtitle { color: var(--muted); font-size: 0.9rem; margin-top: 4px; }
        .badge { padding: 6px 14px; border-radius: 9999px; font-weight: 700; font-size: 0.85rem; letter-spacing: 0.05em; display: inline-flex; align-items: center; gap: 6px; }
        .badge-normal { background: rgba(34,197,94,0.15); color: var(--success); border: 1px solid var(--success); }
        .badge-warning { background: rgba(245,158,11,0.15); color: var(--warning); border: 1px solid var(--warning); }
        .badge-danger { background: rgba(239,68,68,0.2); color: var(--danger); border: 1px solid var(--danger); animation: pulse 1.5s infinite; }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.6; } }

        /* Tehdit Bildirim Banner'ı */
        .threat-banner { background: var(--card); border: 1px solid var(--border); border-radius: 10px; padding: 16px 20px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; }
        .threat-title { font-size: 1.1rem; font-weight: 700; display: flex; align-items: center; gap: 8px; }
        .threat-desc { color: var(--muted); font-size: 0.9rem; margin-top: 4px; }

        /* Metrik Kartları */
        .grid-stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 15px; margin-bottom: 20px; }
        .stat-card { background: var(--card); border: 1px solid var(--border); border-radius: 10px; padding: 18px; }
        .stat-label { color: var(--muted); font-size: 0.82rem; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px; }
        .stat-value { font-size: 1.8rem; font-weight: 800; color: #fff; }
        .stat-bar-bg { width: 100%; height: 6px; background: #1f2937; border-radius: 3px; margin-top: 10px; overflow: hidden; }
        .stat-bar-fill { height: 100%; background: var(--primary); width: 0%; transition: width 0.3s ease; }

        /* Kontrol ve Savunma Alanı */
        .defense-panel { background: var(--card); border: 1px solid var(--border); border-radius: 10px; padding: 16px 20px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; }
        .btn { padding: 10px 22px; border-radius: 8px; font-weight: 700; font-size: 0.95rem; cursor: pointer; border: none; transition: 0.2s; display: inline-flex; align-items: center; gap: 8px; }
        .btn-primary { background: #0284c7; color: #fff; }
        .btn-primary:hover { background: #0369a1; }
        .btn-danger { background: #dc2626; color: #fff; }
        .btn-danger:hover { background: #b91c1c; }
        .btn-success { background: #16a34a; color: #fff; }
        .btn-success:hover { background: #15803d; }

        /* Canlı Ağ Trafiği Akış Tablosu */
        .table-card { background: var(--card); border: 1px solid var(--border); border-radius: 10px; padding: 20px; }
        .table-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
        .table-header h2 { font-size: 1.15rem; color: var(--accent); }
        .table-wrapper { max-height: 400px; overflow-y: auto; }
        table { width: 100%; border-collapse: collapse; font-size: 0.88rem; text-align: left; }
        th { padding: 10px 12px; background: #1e293b; color: var(--muted); font-weight: 600; position: sticky; top: 0; }
        td { padding: 9px 12px; border-bottom: 1px solid #1f2937; font-family: 'Consolas', monospace; }
        tr:hover { background: rgba(255,255,255,0.02); }
        .tag-info { color: #38bdf8; }
        .tag-warning { color: #f59e0b; }
        .tag-critical { color: #ef4444; font-weight: bold; }
        .tag-blocked { color: #a855f7; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div>
                <h1>🛡️ Ağ Güvenliği ve Trafik İzleme Merkezi</h1>
                <div class="subtitle">Trakya Üniversitesi Bilgisayar Mühendisliği Laboratuvarı - Anomali ve DoS İzleme Konsolu</div>
            </div>
            <div>
                <span id="system-badge" class="badge badge-normal">● SİSTEM İZLENİYOR</span>
            </div>
        </header>

        <!-- Anomali / Saldırı Durumu Banner'ı -->
        <div id="threat-banner" class="threat-banner">
            <div>
                <div id="threat-title" class="threat-title" style="color: var(--success);">
                    <span>✔</span> Sistem Çevrimiçi ve Kararlı
                </div>
                <div id="threat-desc" class="threat-desc">Ağ trafiği normal sınırlar içinde seyrediyor. Anomali tespit edilmedi.</div>
            </div>
            <div id="threat-layer" style="font-size: 0.85rem; font-weight: 600; color: var(--muted); text-align: right;">
                Katman: Tüm Katmanlar
            </div>
        </div>

        <!-- Canlı İstatistik Metrikleri -->
        <div class="grid-stats">
            <div class="stat-card">
                <div class="stat-label">Açık TCP Bağlantısı (Slowloris Hedefi)</div>
                <div id="val-conn" class="stat-value">0 / 25</div>
                <div class="stat-bar-bg"><div id="bar-conn" class="stat-bar-fill"></div></div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Aktif Worker Havuzu (İş Parçacığı)</div>
                <div id="val-workers" class="stat-value">0 / 10</div>
                <div class="stat-bar-bg"><div id="bar-workers" class="stat-bar-fill" style="background: #8b5cf6;"></div></div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Trafik Hızı (Throughput)</div>
                <div id="val-rps" class="stat-value">0.0 req/s</div>
                <div style="font-size: 0.8rem; color: var(--muted); margin-top: 8px;">Toplam İstek: <span id="val-total">0</span></div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Hizmet Verilemeyen (503 DoS)</div>
                <div id="val-dropped" class="stat-value" style="color: var(--danger);">0</div>
                <div style="font-size: 0.8rem; color: var(--muted); margin-top: 8px;">Rate Limited (429): <span id="val-limited">0</span></div>
            </div>
        </div>

        <!-- Siber Savunma Kontrol Paneli -->
        <div class="defense-panel">
            <div>
                <h3 style="font-size: 1rem; margin-bottom: 4px;">Siber Savunma Koruması (Anti-Slowloris + WAF Token Bucket)</h3>
                <p style="color: var(--muted); font-size: 0.85rem;">
                    Durum: <b id="defense-text" style="color: var(--danger);">KAPALI (Korumasız - Saldırıya Açık)</b>
                </p>
            </div>
            <button id="btn-defense" class="btn btn-success" onclick="toggleDefense()">
                🛡️ Savunmayı Devreye Al
            </button>
        </div>

        <!-- Canlı Ağ Trafiği Akış Tablosu -->
        <div class="table-card">
            <div class="table-header">
                <h2>📡 Canlı Ağ Trafiği ve Olay Akışı (Real-Time Packet Stream)</h2>
                <span id="packet-status" style="font-size: 0.8rem; color: var(--muted);">Akış Aktif (800ms)</span>
            </div>
            <div class="table-wrapper">
                <table>
                    <thead>
                        <tr>
                            <th style="width: 100px;">Zaman</th>
                            <th style="width: 160px;">İstemci</th>
                            <th style="width: 160px;">Olay Türü</th>
                            <th>Paket / Başlık Detayları</th>
                            <th style="width: 110px;">Durum</th>
                        </tr>
                    </thead>
                    <tbody id="traffic-table-body">
                        <tr><td colspan="5" style="text-align: center; color: var(--muted);">Trafik verileri yükleniyor...</td></tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        let defenseActive = false;

        async function fetchMetrics() {
            try {
                const res = await fetch('/api/traffic');
                if (!res.ok) return;
                const data = await res.json();

                // 1. Metrikleri Güncelle
                document.getElementById('val-conn').innerText = `${data.metrics.active_connections} / ${data.metrics.max_connections}`;
                const connPct = Math.min(100, (data.metrics.active_connections / data.metrics.max_connections) * 100);
                const barConn = document.getElementById('bar-conn');
                barConn.style.width = connPct + '%';
                barConn.style.background = connPct > 80 ? '#ef4444' : (connPct > 50 ? '#f59e0b' : '#0284c7');

                document.getElementById('val-workers').innerText = `${data.metrics.active_workers} / ${data.metrics.max_workers}`;
                const workerPct = Math.min(100, (data.metrics.active_workers / data.metrics.max_workers) * 100);
                document.getElementById('bar-workers').style.width = workerPct + '%';

                document.getElementById('val-rps').innerText = `${data.metrics.current_rps.toFixed(1)} req/s`;
                document.getElementById('val-total').innerText = data.metrics.total_requests;
                document.getElementById('val-dropped').innerText = data.metrics.dropped_503;
                document.getElementById('val-limited').innerText = data.metrics.rate_limited_429;

                // 2. Savunma Durumu
                defenseActive = data.defense.enabled;
                const btn = document.getElementById('btn-defense');
                const defText = document.getElementById('defense-text');
                if (defenseActive) {
                    defText.innerText = "AKTİF (Anti-Slowloris + WAF Devrede)";
                    defText.style.color = "var(--success)";
                    btn.innerText = "⛔ Savunmayı Kapat";
                    btn.className = "btn btn-danger";
                } else {
                    defText.innerText = "KAPALI (Korumasız - Saldırıya Açık)";
                    defText.style.color = "var(--danger)";
                    btn.innerText = "🛡️ Savunmayı Devreye Al";
                    btn.className = "btn btn-success";
                }

                // 3. Tehdit / Anomali Banner'ı
                const th = data.threat;
                const bannerTitle = document.getElementById('threat-title');
                const bannerDesc = document.getElementById('threat-desc');
                const bannerLayer = document.getElementById('threat-layer');
                const badge = document.getElementById('system-badge');

                bannerTitle.innerText = th.title;
                bannerDesc.innerText = th.description;
                bannerLayer.innerText = "Katman: " + th.osi_layer;

                if (th.severity === "KRITIK_TEHDIT") {
                    bannerTitle.style.color = "var(--danger)";
                    badge.className = "badge badge-danger";
                    badge.innerText = "● SALDIRI / DOYGUNLUK TESPİT EDİLDİ";
                } else if (th.severity === "UYARI") {
                    bannerTitle.style.color = "var(--warning)";
                    badge.className = "badge badge-warning";
                    badge.innerText = "● ANOMALİ / YÜKSEK TRAFİK";
                } else {
                    bannerTitle.style.color = "var(--success)";
                    badge.className = "badge badge-normal";
                    badge.innerText = "● SİSTEM ÇEVRİMİÇİ";
                }

                // 4. Canlı Trafik Tablosu
                const tbody = document.getElementById('traffic-table-body');
                if (data.events && data.events.length > 0) {
                    let html = '';
                    for (const ev of data.events) {
                        let tagClass = 'tag-info';
                        if (ev.threat_level === 'CRITICAL') tagClass = 'tag-critical';
                        else if (ev.threat_level === 'WARNING') tagClass = 'tag-warning';
                        else if (ev.threat_level === 'BLOCKED') tagClass = 'tag-blocked';

                        html += `<tr>
                            <td>${ev.timestamp}</td>
                            <td>${ev.client}</td>
                            <td><span class="${tagClass}">${ev.event_type}</span></td>
                            <td>${ev.details}</td>
                            <td><span class="${tagClass}">${ev.threat_level}</span></td>
                        </tr>`;
                    }
                    tbody.innerHTML = html;
                }
            } catch (err) {
                console.error("Metrikler alınamadı:", err);
            }
        }

        async function toggleDefense() {
            try {
                await fetch('/api/defense/toggle');
                fetchMetrics();
            } catch (e) {
                alert("Savunma durumu değiştirilemedi: " + e);
            }
        }

        // 800 milisaniyede bir canlı güncelle
        setInterval(fetchMetrics, 800);
        fetchMetrics();
    </script>
</body>
</html>
"""

class CapacityTestHTTPHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def setup(self):
        super().setup()
        client_addr = f"{self.client_address[0]}:{self.client_address[1]}"

        if rate_limiter.enabled:
            self.connection.settimeout(2.5)
        else:
            self.connection.settimeout(60.0)

    def handle(self):
        client_addr = f"{self.client_address[0]}:{self.client_address[1]}"
        try:
            super().handle()
        except (TimeoutError, socket.timeout):
            with server_state.lock:
                server_state.slowloris_suspects = max(0, server_state.slowloris_suspects - 1)
            traffic_logger.log(
                client=client_addr,
                event_type="TIMEOUT_DROP",
                details="Yavaş başlık zaman aşımı (2.5s aşıldı). Soket düşürüldü.",
                threat_level="BLOCKED" if rate_limiter.enabled else "WARNING"
            )
        except Exception:
            pass

    def finish(self):
        try:
            super().finish()
        finally:
            with server_state.lock:
                if server_state.active_connections > 0:
                    server_state.active_connections -= 1
                if server_state.slowloris_suspects > 0:
                    server_state.slowloris_suspects -= 1

    def do_GET(self):
        global server_state, rate_limiter
        client_addr = f"{self.client_address[0]}:{self.client_address[1]}"

        if self.path == "/api/traffic":
            with server_state.lock:
                active_c = server_state.active_connections
                max_c = server_state.max_connections
                active_w = server_state.active_workers
                max_w = server_state.max_workers
                total_r = server_state.total_requests
                drop_503 = server_state.dropped_503
                limit_429 = server_state.rate_limited_429
                suspects = server_state.slowloris_suspects
                cur_rps = server_state.current_rps

            anomaly_info = anomaly_detector.evaluate(
                active_conn=active_c,
                max_conn=max_c,
                active_workers=active_w,
                max_workers=max_w,
                slowloris_suspects=suspects,
                dropped_503=drop_503,
                rps=cur_rps,
                defense_enabled=rate_limiter.enabled
            )

            payload = {
                "metrics": {
                    "active_connections": active_c,
                    "max_connections": max_c,
                    "active_workers": active_w,
                    "max_workers": max_w,
                    "total_requests": total_r,
                    "dropped_503": drop_503,
                    "rate_limited_429": limit_429,
                    "slowloris_suspects": suspects,
                    "current_rps": cur_rps
                },
                "defense": {
                    "enabled": rate_limiter.enabled
                },
                "threat": {
                    "status_code": anomaly_info.status_code,
                    "severity": anomaly_info.severity.value,
                    "title": anomaly_info.title,
                    "osi_layer": anomaly_info.osi_layer,
                    "description": anomaly_info.description,
                    "recommendation": anomaly_info.recommendation
                },
                "events": traffic_logger.get_recent_events(limit=25)
            }

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(payload, ensure_ascii=False).encode("utf-8"))
            return

        if self.path in ("/api/defense/toggle", "/toggle-defense", "/defense/enable", "/defense/disable"):
            if "enable" in self.path:
                rate_limiter.enabled = True
            elif "disable" in self.path:
                rate_limiter.enabled = False
            else:
                rate_limiter.enabled = not rate_limiter.enabled

            traffic_logger.log(
                client=client_addr,
                event_type="DEFENSE_TOGGLE",
                details=f"Siber Savunma {'AKTİF EDİLDİ' if rate_limiter.enabled else 'KAPATILDI'}",
                threat_level="INFO"
            )

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"defense": rate_limiter.enabled}).encode("utf-8"))
            return

        if rate_limiter.enabled and self.path in ("/heavy", "/search", "/login", "/protected") and not rate_limiter.allow_request():
            with server_state.lock:
                server_state.rate_limited_429 += 1
            traffic_logger.log(
                client=client_addr,
                event_type="HTTP_429_BLOCKED",
                details=f"Aşırı istek WAF/RateLimiter tarafından engellendi: {self.path}",
                threat_level="BLOCKED"
            )
            self.send_response(429)
            self.send_header("Content-Type", "application/json")
            self.send_header("Retry-After", "1")
            self.end_headers()
            self.wfile.write(b'{"error": "Too Many Requests - Rate Limited", "status": 429}')
            return

        if not server_state.try_acquire_worker(timeout_sec=0.08):
            traffic_logger.log(
                client=client_addr,
                event_type="HTTP_503_OUTAGE",
                details=f"Hizmet Kesintisi! Sunucu kuyruğu doldu: {self.path}",
                threat_level="CRITICAL"
            )
            self.send_response(503)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            err_html = (
                "<html><body style='background:#1e1e2f;color:#ff5555;font-family:sans-serif;padding:40px;text-align:center;'>"
                "<h1>[503 SERVICE UNAVAILABLE]</h1>"
                "<h2>Hizmet Kesintisi Gerceklesti (Denial of Service)</h2>"
                "<p>Sunucu is parcacigi havuzu tamamen doldu. Kaynak tuketimi nedeniyle yeni baglantilar kabul edilemiyor.</p>"
                "</body></html>"
            )
            self.wfile.write(err_html.encode("utf-8"))
            return

        try:
            if self.path in ("/", "/index.html", "/dashboard"):
                traffic_logger.log(
                    client=client_addr,
                    event_type="HTTP_GET",
                    details="Web Dashboard Sayfası Ziyaret Edildi (200 OK)",
                    threat_level="INFO"
                )
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(HTML_DASHBOARD.encode("utf-8"))
                return

            if self.path in ("/heavy", "/search"):
                time.sleep(0.20)
                traffic_logger.log(
                    client=client_addr,
                    event_type="HEAVY_QUERY",
                    details="Ağır CPU/Veritabanı İşlemi Tamamlandı (200 OK)",
                    threat_level="INFO"
                )
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(b'{"status": "success", "operation": "Heavy Computation Completed"}')
                return

            traffic_logger.log(
                client=client_addr,
                event_type="HTTP_200",
                details=f"GET {self.path} başarılı (200 OK)",
                threat_level="INFO"
            )
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status": "success", "message": "API Standard Response"}')

        finally:
            server_state.release_worker()

class ConnectionLimitingThreadingHTTPServer(ThreadingHTTPServer):
    daemon_threads = True

    def process_request(self, request, client_address):
        client_addr = f"{client_address[0]}:{client_address[1]}"

        with server_state.lock:
            if server_state.active_connections >= server_state.max_connections:
                server_state.dropped_503 += 1
                traffic_logger.log(
                    client=client_addr,
                    event_type="CONN_POOL_FULL",
                    details=f"TCP Bağlantı Havuzu DOLDU ({server_state.max_connections}/{server_state.max_connections})! Yeni bağlantı reddedildi (503).",
                    threat_level="CRITICAL"
                )
                try:
                    request.sendall(
                        b"HTTP/1.1 503 Service Unavailable\r\n"
                        b"Content-Type: text/html; charset=utf-8\r\n"
                        b"Connection: close\r\n\r\n"
                        b"<html><body><h1>503 Service Unavailable</h1>"
                        b"<p>Baglanti havuzu tamamen doldu (Slowloris DoS).</p>"
                        b"</body></html>\r\n"
                    )
                    request.close()
                except Exception:
                    pass
                return

            server_state.active_connections += 1
            server_state.slowloris_suspects += 1

        traffic_logger.log(
            client=client_addr,
            event_type="TCP_CONNECT",
            details=f"Yeni TCP Soketi Açıldı [Aktif Bağlantı: {server_state.active_connections}/{server_state.max_connections}]",
            threat_level="WARNING" if server_state.active_connections > 15 else "INFO"
        )

        super().process_request(request, client_address)

def is_port_open(host: str = "127.0.0.1", port: int = 8080) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.4)
        return s.connect_ex((host, port)) == 0

def run_test_server(host: str = "127.0.0.1", port: int = 8080):
    server = ConnectionLimitingThreadingHTTPServer((host, port), CapacityTestHTTPHandler)
    print(f"\n[OK] Ağ Güvenliği ve Trafik İzleme Sunucusu Başlatıldı -> http://{host}:{port}")
    print("[*] Canlı Web Dashboard : http://127.0.0.1:8080/")
    print("[*] Gerçek Zamanlı API   : http://127.0.0.1:8080/api/traffic")
    print("[*] Kapatmak için CTRL+C tuşlarına basabilirsiniz.\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] Sunucu güvenle kapatılıyor...")
    finally:
        server.server_close()

def ensure_server_running(host: str = "127.0.0.1", port: int = 8080) -> bool:
    if is_port_open(host, port):
        return True

    thread = threading.Thread(
        target=run_test_server,
        kwargs={"host": host, "port": port},
        daemon=True
    )
    thread.start()

    for _ in range(12):
        time.sleep(0.15)
        if is_port_open(host, port):
            return True
    return False

if __name__ == "__main__":
    run_test_server()
