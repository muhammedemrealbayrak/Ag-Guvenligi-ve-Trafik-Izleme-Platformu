import json
import os
import sys
import time
import urllib.request

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def run_monitor(host: str = "127.0.0.1", port: int = 8080):
    url = f"http://{host}:{port}/api/traffic"
    print(f"[*] Canlı Ağ Trafiği ve IDS İzleyicisi Başlatılıyor -> {url}...")
    time.sleep(0.5)

    last_error_time = 0

    while True:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "NOC-Terminal-Monitor"})
            with urllib.request.urlopen(req, timeout=1.5) as res:
                data = json.loads(res.read().decode("utf-8"))

            m = data["metrics"]
            t = data["threat"]
            d = data["defense"]
            events = data.get("events", [])

            clear_screen()

            print("=" * 85)
            print("       CANLI AĞ GÜVENLİĞİ VE TRAFİK İZLEME MERKEZİ (TERMINAL NOC CONSOLE)")
            print("       Trakya Üniversitesi Bilgisayar Mühendisliği Mezuniyet Projesi")
            print("=" * 85)

            threat_color_prefix = ""
            if t["severity"] == "KRITIK_TEHDIT":
                status_box = f" [!] {t['title']} "
                print(f"\n>>> DURUM: {status_box}")
                print(f"    Detay   : {t['description']}")
                print(f"    Öneri   : {t['recommendation']}")
            elif t["severity"] == "UYARI":
                status_box = f" [~] {t['title']} "
                print(f"\n>>> DURUM: {status_box}")
                print(f"    Detay   : {t['description']}")
            else:
                print(f"\n>>> DURUM: [OK] SİSTEM ÇEVRİMİÇİ VE KARARLI (Tehdit Saptanmadı)")

            print("-" * 85)

            conn_bar = "#" * int((m["active_connections"] / max(1, m["max_connections"])) * 20)
            conn_bar_str = f"|{conn_bar:<20}|"

            def_str = "AKTİF (Anti-Slowloris Devrede)" if d["enabled"] else "KAPALI (Saldırıya Açık)"

            print(f"  • Açık TCP Bağlantısı (Slowloris): {m['active_connections']:2d} / {m['max_connections']:2d}  {conn_bar_str}")
            print(f"  • Aktif Worker Havuzu (Katman 7) : {m['active_workers']:2d} / {m['max_workers']:2d}")
            print(f"  • Anlık Trafik Hızı (Throughput) : {m['current_rps']:5.1f} req/s   (Toplam: {m['total_requests']})")
            print(f"  • Hizmet Kesintisi (503 DoS)     : {m['dropped_503']:<5d}      (WAF Engeli 429: {m['rate_limited_429']})")
            print(f"  • Siber Savunma Koruması         : {def_str}")
            print("=" * 85)

            print("📡 CANLI AĞ TRAFİĞİ AKIŞI (Son Gelen Paketler ve Soket Olayları):")
            print(f"{'Zaman':<10} | {'İstemci':<18} | {'Olay':<16} | {'Paket / Başlık Detayı'}")
            print("-" * 85)

            if not events:
                print("  Henüz kaydedilmiş bir paket trafiği yok...")
            else:
                for ev in events[:12]:
                    details = ev['details'][:45] + "..." if len(ev['details']) > 45 else ev['details']
                    print(f"{ev['timestamp']:<10} | {ev['client']:<18} | {ev['event_type']:<16} | {details}")

            print("-" * 85)
            print("İzleme Modu Aktif (800ms) | Durdurmak için CTRL+C | Savunmayı aç/kapa: Web Dashboard")

        except Exception as e:
            clear_screen()
            print("=" * 85)
            print("       CANLI AĞ GÜVENLİĞİ VE TRAFİK İZLEME MERKEZİ (TERMINAL NOC CONSOLE)")
            print("=" * 85)
            print(f"\n[!] Sunucuya bağlanılamıyor: http://{host}:{port}/api/traffic")
            print(f"    Hata: {e}")
            print("    Lütfen sunucunun çalıştığından emin olun (python src/server.py).")
            print("-" * 85)

        time.sleep(0.8)

if __name__ == "__main__":
    try:
        run_monitor()
    except KeyboardInterrupt:
        print("\n[*] İzleyici kapatıldı.")
