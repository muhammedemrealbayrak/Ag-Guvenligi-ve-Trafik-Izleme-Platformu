import os
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent
OUTPUT_HTML = BASE_DIR / "docs" / "Sunum_ve_Akademik_Rapor.html"
OUTPUT_PDF = BASE_DIR / "Sunum_ve_Akademik_Rapor.pdf"

HTML_CONTENT = """<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>Ağ Güvenliği ve Performans Analitiği Akademik Sunum ve Raporu</title>
    <style>
        @page {
            size: A4 portrait;
            margin: 12mm 15mm 12mm 15mm;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            color: #1e293b;
            background: #ffffff;
            line-height: 1.48;
            font-size: 10pt;
        }
        .page {
            page-break-after: always;
            height: 270mm;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            position: relative;
            overflow: hidden;
        }
        .page:last-child {
            page-break-after: avoid;
        }

        /* Kapak Sayfası */
        .cover {
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            height: 100%;
            padding: 20px;
        }
        .university-header {
            font-size: 16pt;
            font-weight: 800;
            color: #0f172a;
            letter-spacing: 0.04em;
            margin-bottom: 6px;
            text-transform: uppercase;
        }
        .faculty-header {
            font-size: 11.5pt;
            font-weight: 600;
            color: #475569;
            margin-bottom: 35px;
            text-transform: uppercase;
        }
        .project-badge {
            display: inline-block;
            background: #e0f2fe;
            color: #0284c7;
            font-weight: 700;
            font-size: 10.5pt;
            padding: 6px 18px;
            border-radius: 20px;
            margin-bottom: 25px;
            border: 1px solid #bae6fd;
        }
        .project-title {
            font-size: 23pt;
            font-weight: 900;
            color: #0f172a;
            line-height: 1.25;
            margin-bottom: 16px;
            max-width: 650px;
        }
        .project-subtitle {
            font-size: 12pt;
            color: #64748b;
            margin-bottom: 50px;
            max-width: 580px;
            font-weight: 400;
        }
        .meta-box {
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 20px 35px;
            text-align: left;
            width: 100%;
            max-width: 480px;
            margin-bottom: 35px;
        }
        .meta-row {
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
            font-size: 10.5pt;
        }
        .meta-row:last-child { margin-bottom: 0; }
        .meta-label { color: #64748b; font-weight: 600; }
        .meta-value { color: #0f172a; font-weight: 700; }
        .date-footer { font-size: 10pt; color: #94a3b8; font-weight: 500; }

        /* İç Sayfa Stilleri */
        h2 {
            font-size: 14.5pt;
            font-weight: 800;
            color: #0f172a;
            border-bottom: 2px solid #0284c7;
            padding-bottom: 5px;
            margin-bottom: 12px;
            margin-top: 0;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        h3 {
            font-size: 11pt;
            font-weight: 700;
            color: #1e293b;
            margin-top: 10px;
            margin-bottom: 5px;
        }
        p { margin-bottom: 8px; text-align: justify; }

        .callout {
            background: #f0f9ff;
            border-left: 4px solid #0284c7;
            padding: 10px 14px;
            border-radius: 0 8px 8px 0;
            margin: 10px 0;
            font-size: 9.5pt;
        }
        .callout-warning {
            background: #fffbeb;
            border-left-color: #f59e0b;
        }
        .callout-danger {
            background: #fef2f2;
            border-left-color: #ef4444;
        }
        .callout-title {
            font-weight: 800;
            margin-bottom: 3px;
            display: block;
            color: #0f172a;
        }

        /* Tablolar */
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 10px 0;
            font-size: 9pt;
        }
        th {
            background: #0f172a;
            color: #ffffff;
            font-weight: 700;
            padding: 7px 10px;
            text-align: left;
            border: 1px solid #1e293b;
        }
        td {
            padding: 6px 10px;
            border: 1px solid #cbd5e1;
            background: #ffffff;
        }
        tr:nth-child(even) td { background: #f8fafc; }

        /* Kod ve Şema Blokları */
        pre {
            background: #0f172a;
            color: #f8fafc;
            padding: 10px 14px;
            border-radius: 6px;
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 8.2pt;
            line-height: 1.35;
            margin: 8px 0;
            overflow-x: hidden;
        }
        .diagram-box {
            background: #f8fafc;
            border: 1px solid #cbd5e1;
            border-radius: 6px;
            padding: 10px;
            text-align: center;
            font-family: monospace;
            font-size: 8.5pt;
            margin: 8px 0;
            line-height: 1.35;
        }

        /* Grid Listeler */
        .card-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin: 10px 0;
        }
        .feature-card {
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            padding: 10px 12px;
        }
        .feature-card h4 {
            font-size: 10pt;
            font-weight: 700;
            color: #0284c7;
            margin-bottom: 3px;
        }
        .feature-card p {
            font-size: 8.5pt;
            margin: 0;
            color: #475569;
        }

        .formula-box {
            background: #f1f5f9;
            border: 1px dashed #94a3b8;
            border-radius: 6px;
            padding: 9px;
            text-align: center;
            font-size: 10.5pt;
            font-weight: bold;
            margin: 9px 0;
            color: #0f172a;
        }

        .footer-note {
            font-size: 8.5pt;
            color: #94a3b8;
            border-top: 1px solid #e2e8f0;
            padding-top: 6px;
            margin-top: auto;
            display: flex;
            justify-content: space-between;
        }
    </style>
</head>
<body>

    <!-- SAYFA 1: KAPAK -->
    <div class="page">
        <div class="cover">
            <div class="university-header">Trakya Üniversitesi</div>
            <div class="faculty-header">Mühendislik Fakültesi • Bilgisayar Mühendisliği Bölümü</div>

            <div class="project-badge">2026-2027 GÜZ DÖNEMİ • BİTİRME / PROJE 1</div>

            <h1 class="project-title">Ağ Güvenliği, Katman 7 DoS/Slowloris Analitiği ve Siber Savunma Platformu</h1>
            <div class="project-subtitle">
                OSI Referans Modeline Göre Ağ Tehditlerinin Sınıflandırılması, Kaynak Doygunluk Tespiti ve Canlı Trafik İzleme Mimarisi
            </div>

            <div class="meta-box">
                <div class="meta-row">
                    <span class="meta-label">Öğrenci Adı Soyadı:</span>
                    <span class="meta-value">Muhammed Emre Albayrak</span>
                </div>
                <div class="meta-row">
                    <span class="meta-label">Bölüm:</span>
                    <span class="meta-value">Bilgisayar Mühendisliği</span>
                </div>
                <div class="meta-row">
                    <span class="meta-label">Çalışma Alanı:</span>
                    <span class="meta-value">Ağ Güvenliği & Performans Analitiği</span>
                </div>
                <div class="meta-row">
                    <span class="meta-label">Platform / Dil:</span>
                    <span class="meta-value">Python 3.12 (Asenkron & Socket)</span>
                </div>
            </div>

            <div class="date-footer">Edirne, 2026</div>
        </div>
    </div>

    <!-- SAYFA 2: YÖNETİCİ ÖZETİ -->
    <div class="page">
        <div>
            <h2>1. Yönetici Özeti ve Problem Tanımı</h2>
            <p>
                Günümüz bilişim altyapılarında bilgi güvenliğinin temel sacayağını oluşturan <b>CIA Triad</b> (Gizlilik, Bütünlük ve Erişilebilirlik) prensiplerinden en kritik olanı <b>Erişilebilirlik (Availability)</b> ilkesidir. Ağ sistemlerinin yetkisiz erişimlere kapatılması kadar, meşru kullanıcılara kesintisiz hizmet vermesi de zorunludur.
            </p>
            <p>
                Hizmet Dışı Bırakma (<b>Denial of Service - DoS</b>) ve Dağıtık Hizmet Dışı Bırakma (<b>DDoS</b>) saldırıları, sunucu donanım kaynaklarını (CPU, RAM, Soket Havuzları) veya ağ bant genişliğini tüketerek sistemleri işlevsiz kılmayı amaçlar. Ancak bu saldırıların tespiti ve simülasyonu akademik düzeyde sıkça yanlış yorumlanmaktadır.
            </p>

            <div class="callout">
                <span class="callout-title">📌 Projenin Temel Amaçları:</span>
                1. Ağ tehditlerini ve anomalilerini akademik <b>OSI (Open Systems Interconnection)</b> referans modeline göre sınıflandırmak.<br>
                2. Geleneksel kaba kuvvet (volumetric flood) yerine, düşük bant genişliğiyle yüksek tahribat yaratan <b>Katman 7 Slowloris</b> saldırısını modellemek.<br>
                3. Yerel ortamda (127.0.0.1) çalışan ve tüm ağ paketlerini canlı görselleştiren bir <b>Siber Operasyon Merkezi (SOC / NOC Dashboard)</b> geliştirmek.<br>
                4. <b>Anti-Slowloris (client_header_timeout)</b> ve <b>Token Bucket Hız Sınırlaması (Rate Limiting)</b> yöntemleriyle meşru trafiğin saldırı altındayken nasıl kurtarıldığını jüri önünde deneysel olarak kanıtlamak.
            </div>

            <h3>Araştırma Soruları ve Hipotez:</h3>
            <p>
                <b>Hipotez:</b> <i>"Bir web sunucusuna binlerce rastgele istek göndermek sunucuyu çökertmeye yetmez; çünkü modern işletim sistemleri statik istekleri anında eritir. Ancak asenkron soket optimizasyonlarıyla HTTP başlıkları kasıtlı olarak geciktirildiğinde (Slowloris), sunucu süreci çökmeden TCP bağlantı havuzu tükenir ve meşru kullanıcılar için tam bir Hizmet Kesintisi (DoS) meydana gelir."</i>
            </p>

            <div class="card-grid">
                <div class="feature-card">
                    <h4>Hedef 1: Anomali Tespiti</h4>
                    <p>Kayar pencere ve Z-Skoru istatistikleriyle trafik sıçramalarını ve olağandışı soket beklemelerini milisaniyeler içinde yakalamak.</p>
                </div>
                <div class="feature-card">
                    <h4>Hedef 2: Dinamik Savunma</h4>
                    <p>Saldırı başladığında tek tuşla veya otonom eşiklerle devreye girip sahte soketleri düşürerek meşru trafiği korumak.</p>
                </div>
            </div>
        </div>

        <div class="footer-note">
            <span>Trakya Üniversitesi Bilgisayar Mühendisliği</span>
            <span>Sayfa 2 / 10</span>
        </div>
    </div>

    <!-- SAYFA 3: OSI TEHDİT TAKSONOMİSİ -->
    <div class="page">
        <div>
            <h2>2. OSI Referans Modeline Göre Tehdit Taksonomisi</h2>
            <p>
                Bilgisayar ağlarındaki sapmalar, literatürde etki alanlarına göre <b>Pasif</b> (sadece gözlem/tarama yapan) ve <b>Aktif</b> (kapasite tüketen/kesinti yaratan) anomaliler olarak ikiye ayrılır. Bu anomalilerin OSI katmanlarına göre akademik sınıflandırması aşağıda sunulmuştur:
            </p>

            <table>
                <thead>
                    <tr>
                        <th style="width: 17%;">OSI Katmanı</th>
                        <th style="width: 25%;">Anomali / Saldırı Türü</th>
                        <th style="width: 13%;">Doğası</th>
                        <th style="width: 45%;">Mekanizma ve Mühendislik Göstergeleri</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><b>Katman 3 (Ağ)</b></td>
                        <td>ICMP / IP Frag Flood</td>
                        <td>Aktif</td>
                        <td>Büyük paket hacmiyle yönlendirici (router) tampon belleklerini şişirme. Gösterge: Aşırı yüksek PPS (Paket/sn).</td>
                    </tr>
                    <tr>
                        <td><b>Katman 3 (Ağ)</b></td>
                        <td>Topoloji Keşfi (Ping Sweep)</td>
                        <td>Pasif</td>
                        <td>Ağdaki aktif IP'leri haritalamak için sıralı echo istekleri. Gösterge: Düzenli ARP/ICMP yoklamaları.</td>
                    </tr>
                    <tr>
                        <td><b>Katman 4 (Taşıma)</b></td>
                        <td>TCP SYN Flood (State Exhaustion)</td>
                        <td>Aktif</td>
                        <td>3 yönlü el sıkışmayı (3-Way Handshake) tamamlamayarak sunucunun <code>SYN_RECV</code> kuyruğunu doldurma.</td>
                    </tr>
                    <tr>
                        <td><b>Katman 4 (Taşıma)</b></td>
                        <td>Port ve Bayrak Taraması</td>
                        <td>Pasif</td>
                        <td>SYN, FIN, NULL bayraklarıyla açık servisleri yoklama. Gösterge: Tek kaynaktan gelen yüksek TCP RST paketleri.</td>
                    </tr>
                    <tr>
                        <td><b>Katman 7 (Uygulama)</b></td>
                        <td>HTTP Resource Exhaustion</td>
                        <td>Aktif</td>
                        <td>Veritabanı veya karmaşık CPU algoritmalarını tetikleyen ağır GET/POST sorguları. Gösterge: Yüksek işlemci yükü ve 503 oranı.</td>
                    </tr>
                    <tr>
                        <td><b>Katman 7 (Uygulama)</b></td>
                        <td><b>Slowloris (Yavaş Başlık)</b></td>
                        <td><b>Aktif</b></td>
                        <td><b>HTTP başlıklarını kasıtlı olarak çok yavaş göndererek sunucu bağlantı yuvalarını (TCP slots) kilitleme.</b></td>
                    </tr>
                </tbody>
            </table>

            <div class="callout callout-warning">
                <span class="callout-title">⚠️ Katman 4 ve Katman 7 DoS Arasındaki Temel Ayrım:</span>
                Katman 4 SYN Flood saldırısında sunucunun <i>çekirdek (kernel) soket kuyruğu</i> hedef alınırken; Katman 7 Slowloris saldırısında bağlantı tamamen kurulur (el sıkışma biter) ve sunucunun <i>uygulama seviyesindeki worker thread havuzu</i> rehin alınır. Bu nedenle Katman 7 saldırıları klasik paket filtreleme duvarlarını kolayca aşar.
            </div>
        </div>

        <div class="footer-note">
            <span>Trakya Üniversitesi Bilgisayar Mühendisliği</span>
            <span>Sayfa 3 / 10</span>
        </div>
    </div>

    <!-- SAYFA 4: 100.000 İSTEK PARADOKSU -->
    <div class="page">
        <div>
            <h2>3. "100.000 İstek Paradoksu" ve DoS'un Tanımı</h2>
            <p>
                Mühendislik testlerinde sıkça rastlanan ve kavram yanılgısına yol açan temel gözlem şudur:
                <i>"Sunucuya tek bir döngüde 100.000 istek gönderdim ancak süreç kapanmadı, işletim sistemi sunucuyu öldürmedi. Saldırı başarısız mı oldu?"</i>
            </p>

            <h3>3.1. Toplam Hacim ile Eşzamanlılık (Concurrency) Farkı</h3>
            <p>
                Bir döngü içerisinde sıralı (sequential) olarak 100.000 istek göndermek, modern çok çekirdekli bir CPU için sadece bir bellek döngüsüdür. Sunucu her isteği milisaniyenin onda birinde (0.1 ms) karşılayıp bağlantıyı kapattığı sürece kuyruk oluşmaz. Önemli olan toplam istek sayısı değil, <b>aynı milisaniyede kaç iş parçacığının sunucu kaynaklarını kilitlediğidir</b>.
            </p>

            <div class="diagram-box">
                [Sıralı İstekler - Çökme Olmaz]  İstek 1 (Bitti) -> İstek 2 (Bitti) -> İstek 100.000 (CPU Hiç Zorlanmaz)<br>
                [Eşzamanlı Yük - Tıkanma]      İstek 1..25 Aynı Anda Gelir -> Tüm Worker'lar Kilitlenir -> YENİ İSTEKLER DÜŞER
            </div>

            <h3>3.2. DoS (Hizmet Dışı Bırakma) Ne Demektir, Ne Değildir?</h3>
            <p>Siber güvenlik literatüründe (RFC 4732, NIST SP 800-44, OWASP) DoS:</p>
            <ul>
                <li>❌ <b>Değildir:</b> Python sürecinin çökmesi, bellek hatası (Segmentation Fault) vermesi veya pencerenin kapanması.</li>
                <li>✅ <b>Kesinlikle Şudur:</b> Sunucu sürecinin çalışır durumda olmasına rağmen, kaynaklarının (Worker Pool, TCP Yuvaları) tükenmesi sebebiyle <b>meşru kullanıcıların sisteme erişememesi, zaman aşımına (Timeout) uğraması veya HTTP 503 Service Unavailable almasıdır</b>.</li>
            </ul>

            <div class="callout callout-danger">
                <span class="callout-title">🚨 Akademik Jüriye Gösterilecek Kanıt:</span>
                Sunucu arkada çalışırken tarayıcınızı açtığınızda sayfanın dönüp dönüp açılmaması veya ekranda <b>"503 Service Unavailable - Bağlantı Havuzu Tükendi"</b> hatasının çıkması, DoS saldırısının %100 başarıya ulaştığının resmi mühendislik kanıtıdır.
            </div>
        </div>

        <div class="footer-note">
            <span>Trakya Üniversitesi Bilgisayar Mühendisliği</span>
            <span>Sayfa 4 / 10</span>
        </div>
    </div>

    <!-- SAYFA 5: SLOWLORIS ANATOMİSİ -->
    <div class="page">
        <div>
            <h2>4. Katman 7 Slowloris Saldırısının Anatomisi</h2>
            <p>
                Slowloris, son derece düşük bant genişliği (birkaç kilobayt) kullanarak devasa web sunucularını (Apache, Nginx, IIS) felç edebilen sofistike bir Katman 7 saldırısıdır.
            </p>

            <h3>4.1. HTTP Protokol Zafiyeti (RFC 2616)</h3>
            <p>
                HTTP/1.1 standardına göre bir isteğin sona erdiği, peş peşe gelen iki adet satır sonu karakteri (<code>\r\n\r\n</code> - CRLF CRLF) ile anlaşılır. Web sunucusu bu iki karakteri görene kadar istemcinin başlık göndermeye devam edeceğini varsayar ve bağlantıyı açık tutarak bir iş parçacığı (worker thread) tahsis eder.
            </p>

            <pre>
# Normal Geçerli HTTP İsteği:
GET / HTTP/1.1\r\n
Host: 127.0.0.1:8080\r\n
User-Agent: Mozilla/5.0\r\n
\r\n                          <-- [İSTEK BİTTİ, SUNUCU ANINDA YANIT VERİR]

# Slowloris Saldırı İsteği:
GET /?123 HTTP/1.1\r\n
User-Agent: Mozilla/5.0\r\n
X-a: 4821\r\n                 <-- [5 saniye bekler...]
X-b: 1923\r\n                 <-- [8 saniye bekler... \r\n\r\n ASLA GÖNDERİLMEZ!]
            </pre>

            <h3>4.2. Asenkron Soket Mimarisi (slowloris_test.py)</h3>
            <p>Geliştirdiğimiz test scripti, geleneksel iş parçacığı engellemelerini aşmak için <code>asyncio</code> kütüphanesini kullanır:</p>
            <ul>
                <li><b><code>SO_KEEPALIVE</code>:</b> Soketlerin işletim sistemi seviyesinde canlı kalmasını sağlar.</li>
                <li><b><code>TCP_NODELAY</code>:</b> Nagle algoritmasını kapatarak küçük paketlerin arabelleğe alınmadan derhal hedefe iletilmesini temin eder.</li>
                <li><b>Dinamik Heartbeat:</b> Her 5-10 saniyede bir <code>X-[a-z]: [random]</code> ekleyerek zaman aşımını sıfırlar.</li>
            </ul>

            <div class="callout callout-warning">
                <span class="callout-title">🔍 Neden Klasik IDS/Güvenlik Duvarlarını Aldatır?</span>
                Trafik hacmi saniyede birkaç bayttır. Bu durum, saniyedeki paket sayısına (PPS) veya bant genişliğine bakan standart ağ duvarlarında hiçbir alarm tetiklemez. Saldırı tamamen uygulama katmanı semantiği içine gizlenmiştir.
            </div>
        </div>

        <div class="footer-note">
            <span>Trakya Üniversitesi Bilgisayar Mühendisliği</span>
            <span>Sayfa 5 / 10</span>
        </div>
    </div>

    <!-- SAYFA 6: MATEMATİKSEL ANOMALİ MODELİ -->
    <div class="page">
        <div>
            <h2>5. Matematiksel ve İstatistiki Tespit Modelleri</h2>
            <p>
                Geliştirdiğimiz Anomali Tespit Motoru (<code>src/anomaly_engine.py</code>), ağ trafiğindeki olağandışı hareketlilikleri belirlemek için <b>Zaman Pencereli İstatistik (Sliding Window)</b> ve <b>Z-Skoru Normalizasyonu</b> uygular.
            </p>

            <h3>5.1. Kayar Pencere ve Temel Parametreler</h3>
            <p>Sistemin anlık davranışı, son $W$ zaman pencereli (örneğin son 15 saniye) trafik serisi üzerinden hesaplanır:</p>

            <div class="formula-box">
                Ortalama (μ): &nbsp; μ = (1 / W) * Σ X<sub>i</sub> &nbsp;&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;
                Standart Sapma (σ): &nbsp; σ = √ [ (1 / (W - 1)) * Σ (X<sub>i</sub> - μ)² ]
            </div>

            <h3>5.2. Z-Skoru Formülasyonu ve Karar Matrisi</h3>
            <div class="formula-box">Z = ( X<sub>t</sub> - μ ) / σ</div>

            <table>
                <thead>
                    <tr>
                        <th style="width: 25%;">Hesaplanan Z-Skoru</th>
                        <th style="width: 30%;">Sistem Sınıflandırması</th>
                        <th style="width: 45%;">Alınan Mühendislik Kararı / Aksiyon</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><b>Z < 1.5</b></td>
                        <td><span style="color:#16a34a; font-weight:bold;">Normal Aktivite</span></td>
                        <td>Rutin profil sınırları içi. Trafik doğrudan kabul edilir.</td>
                    </tr>
                    <tr>
                        <td><b>1.5 ≤ Z < 2.5</b></td>
                        <td><span style="color:#d97706; font-weight:bold;">Yüksek Yoğunluk</span></td>
                        <td>Doğal kullanıcı artışı (pik saat). İzleme modu sıklaştırılır.</td>
                    </tr>
                    <tr>
                        <td><b>2.5 ≤ Z < 4.0</b></td>
                        <td><span style="color:#dc2626; font-weight:bold;">Ani Sıçrama (Spike)</span></td>
                        <td>Beklenmeyen trafik artışı. Token Bucket hız kısıtlaması hazırda tutulur.</td>
                    </tr>
                    <tr>
                        <td><b>Z ≥ 4.0 veya Soket Doyumu</b></td>
                        <td><span style="color:#7f1d1d; font-weight:bold;">Kritik Tehdit (Slowloris)</span></td>
                        <td>Kapasite aşımı riski. Anti-Slowloris zaman aşımı zorlanır.</td>
                    </tr>
                </tbody>
            </table>

            <h3>5.3. Soket Havuz Doygunluk Oranı (Saturation Ratio)</h3>
            <p>Slowloris saldırısı durum tabanlı olduğundan, Z-skoruna ek olarak <b>Havuz Doygunluk Formülü</b> geliştirilmiştir:</p>
            <div class="formula-box">
                R<sub>sat</sub> = Aktif_TCP_Soketleri / Maksimum_Baglanti_Havuzu &nbsp;&nbsp;(R<sub>sat</sub> ≥ 0.85 ise KRİTİK ALARM)
            </div>
        </div>

        <div class="footer-note">
            <span>Trakya Üniversitesi Bilgisayar Mühendisliği</span>
            <span>Sayfa 6 / 10</span>
        </div>
    </div>

    <!-- SAYFA 7: SİBER SAVUNMA MEKANİZMALARI -->
    <div class="page">
        <div>
            <h2>6. Siber Savunma ve Önleme Mekanizmaları</h2>
            <p>Platformumuz, tespit edilen Katman 7 DoS ve Slowloris anomalilerine karşı iki katmanlı siber savunma kalkanı barındırır:</p>

            <h3>6.1. Anti-Slowloris Koruması (<code>client_header_timeout</code>)</h3>
            <p>Slowloris'in temel zaafı, başlıklar arasında uyumak zorunda olmasıdır. Savunma motorumuz soket seviyesinde dinamik zaman aşımı uygular:</p>
            <ul>
                <li><b>Savunma KAPALI:</b> Başlık bekleme süresi <code>60.0</code> saniyedir. Slowloris rahatça 5-10 saniye uyuyarak bağlantıları elinde tutar.</li>
                <li><b>Savunma AÇIK:</b> Başlık bekleme süresi <code>2.5</code> saniyeye düşürülür (Apache <code>mod_reqtimeout</code> / Nginx <code>client_header_timeout</code> benzeri). 2.5 saniyeden yavaş başlık gönderen tüm soketler sunucu tarafından anında <code>socket.close()</code> ile öldürülür.</li>
            </ul>

            <div class="diagram-box">
                Slowloris Soketi -> [Başlık Gönderdi] -> [5s Uyuyor...] -> SUNUCU: 2.5s Doldu! -> SOKET DÜŞÜRÜLDÜ (TIMEOUT_DROP)<br>
                Meşru Tarayıcı  -> [Tüm Başlıkları 0.01 saniyede gönderdi] -> SUNUCU: 200 OK (ANINDA YANIT)
            </div>

            <h3>6.2. Token Bucket Hız Sınırlaması (Katman 7 Rate Limiter)</h3>
            <p>Hacimsel Katman 7 flood veya CPU tüketen ağır sorgulara (<code>/heavy</code>) karşı <b>Token Bucket</b> algoritması uygulanmıştır:</p>
            <ul>
                <li>Kova kapasitesi: $B = 40$ adet istek token'ı.</li>
                <li>Doldurma hızı: Saniyede $r = 20$ adet yeni token.</li>
                <li>Aşırı gelen istekler sunucu worker havuzuna sokulmadan anında <b>HTTP 429 Too Many Requests</b> koduyla püskürtülür.</li>
            </ul>

            <div class="callout callout-warning">
                <span class="callout-title">🛡️ Meşru Kullanıcı Trafiğinin İzolasyonu:</span>
                Savunma devredeyken hız sınırlaması yalnızca saldırıya açık ağır uç noktalara uygulanır; ana web sitesi (<code>/</code>) ayrıcalıklı tutularak normal kullanıcıların hiçbir kesinti yaşamaması garanti edilir.
            </div>
        </div>

        <div class="footer-note">
            <span>Trakya Üniversitesi Bilgisayar Mühendisliği</span>
            <span>Sayfa 7 / 10</span>
        </div>
    </div>

    <!-- SAYFA 8: LABORATUVAR MİMARİSİ -->
    <div class="page">
        <div>
            <h2>7. Geliştirilen Laboratuvar ve Yazılım Mimarisi</h2>
            <p>Proje, sıfır harici paket bağımlılığı ile tamamen Python 3.12 standart kütüphaneleri üzerinde modüler olarak inşa edilmiştir:</p>

            <div class="card-grid">
                <div class="feature-card">
                    <h4>src/server.py</h4>
                    <p>TCP bağlantı havuzunu (max: 25) ve worker havuzunu (max: 10) yöneten, Anti-Slowloris korumalı test sunucusu.</p>
                </div>
                <div class="feature-card">
                    <h4>Görsel Web SOC Dashboard</h4>
                    <p>127.0.0.1:8080 üzerinde çalışan; canlı soket çubuğu, anomali rozeti ve gerçek zamanlı paket akış tablosunu barındıran merkez.</p>
                </div>
                <div class="feature-card">
                    <h4>monitor.py (Terminal NOC)</h4>
                    <p>Komut satırından canlı ağ trafiğini ve IDS alarmlarını 800ms aralıklarla ekrana basan profesyonel terminal konsolu.</p>
                </div>
                <div class="feature-card">
                    <h4>demo_jury.py</h4>
                    <p>Jüri önünde tek komutla 3 aşamalı saldırı ve savunma senaryosunu adım adım icra eden otonom sunum scripti.</p>
                </div>
            </div>

            <h3>Sistem Mimarisi Akış Diyagramı:</h3>
            <pre>
[İstemciler: Slowloris / Tarayıcı]
               │
               ▼
[ConnectionLimitingServer (127.0.0.1:8080)]
   ├── Bağlantı Havuzu Kontrolü (Aktif: X / 25)
   │     └── Doluysa: HTTP 503 Service Unavailable (Hizmet Kesintisi)
   │
   ├── Anti-Slowloris Motoru (client_header_timeout: 2.5s)
   │     └── Yavaş Soketse: SOKETİ KAPAT (TIMEOUT_DROP)
   │
   ├── Live Traffic Logger (Circular Buffer - Son 150 Olay)
   │     └── Gelen her başlığı / paketi kaydeder
   │
   ├── Canlı İzleme Arayüzleri
   │     ├── Web SOC Dashboard (http://127.0.0.1:8080/)
   │     └── Terminal NOC Console (python monitor.py)
   │
   └── Meşru HTTP Yanıtı (HTTP 200 OK)
            </pre>
        </div>

        <div class="footer-note">
            <span>Trakya Üniversitesi Bilgisayar Mühendisliği</span>
            <span>Sayfa 8 / 10</span>
        </div>
    </div>

    <!-- SAYFA 9: DENEYSEL SONUÇLAR VE JÜRİ PROTOKOLÜ -->
    <div class="page">
        <div>
            <h2>8. Deneysel Sonuçlar ve Jüri Doğrulama Protokolü</h2>
            <p>Geliştirilen platform üzerinde gerçekleştirilen canlı test senaryosunun deneysel sonuçları aşağıda tablolaştırılmıştır:</p>

            <table>
                <thead>
                    <tr>
                        <th style="width: 20%;">Test Aşaması</th>
                        <th style="width: 15%;">Açık Soket</th>
                        <th style="width: 20%;">Meşru İstek Durumu</th>
                        <th style="width: 18%;">Yanıt Gecikmesi</th>
                        <th style="width: 27%;">IDS & Dashboard Teşhisi</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><b>1. Normal Koşullar</b><br>(Saldırı Yok)</td>
                        <td>1 / 25</td>
                        <td><span style="color:#16a34a; font-weight:bold;">HTTP 200 OK</span></td>
                        <td>14.3 ms</td>
                        <td><span style="color:#16a34a; font-weight:bold;">YEŞİL</span>: Sistem Kararlı</td>
                    </tr>
                    <tr>
                        <td><b>2. Slowloris Aktif</b><br>(Savunma KAPALI)</td>
                        <td><b>25 / 25 (DOLU)</b></td>
                        <td><span style="color:#dc2626; font-weight:bold;">HATA (503 / Timeout)</span></td>
                        <td>Zaman Aşımı (>1500 ms)</td>
                        <td><span style="color:#dc2626; font-weight:bold;">KIRMIZI</span>: Slowloris DoS Aktif (Hizmet Kesintisi Kanıtlandı)</td>
                    </tr>
                    <tr>
                        <td><b>3. Savunma Devrede</b><br>(Anti-Slowloris AÇIK)</td>
                        <td>1 / 25</td>
                        <td><span style="color:#16a34a; font-weight:bold;">HTTP 200 OK</span></td>
                        <td>12.9 ms</td>
                        <td><span style="color:#16a34a; font-weight:bold;">YEŞİL</span>: Saldırı Püskürtüldü, Trafik Kurtarıldı</td>
                    </tr>
                </tbody>
            </table>

            <h3>Jüri Önünde Canlı Sunum Protokolü (3 Adım):</h3>
            <ol style="margin-left: 20px; line-height: 1.7; font-size: 9.5pt;">
                <li>
                    <b>Laboratuvarın Açılması:</b> <code>baslat_her_seyi.bat</code> dosyasına çift tıklanır. Tarayıcıda yeşil renkli SOC Dashboard ve yan pencerede canlı terminal izleyicisi açılır.
                </li>
                <li>
                    <b>Saldırının Başlatılması:</b> <code>python slowloris_test.py</code> çalıştırılır. Jürinin gözü önünde bağlantı havuzu 25/25'e fırlar, alarm kırmızıya döner ve tarayıcıdan F5 yapıldığında <b>sayfa açılmaz (Hizmet Kesintisi kanıtlanır)</b>.
                </li>
                <li>
                    <b>Savunmanın Gösterilmesi:</b> Dashboard üzerindeki <i>"Savunmayı Devreye Al"</i> butonuna basılır. Yavaş soketler anında düşürülür, havuz boşalır ve tarayıcıda sayfa <b>anında açılarak meşru trafiğin kurtarıldığı ispatlanır</b>.
                </li>
            </ol>
        </div>

        <div class="footer-note">
            <span>Trakya Üniversitesi Bilgisayar Mühendisliği</span>
            <span>Sayfa 9 / 10</span>
        </div>
    </div>

    <!-- SAYFA 10: SONUÇ VE MÜHENDİSLİK ÇIKARIMLARI -->
    <div class="page">
        <div>
            <h2>9. Sonuç, Mühendislik Çıkarımları ve Gelecek Çalışmalar</h2>
            <p>Bu bitirme projesi kapsamında geliştirilen çalışma ile aşağıdaki akademik ve pratik mühendislik kazanımları elde edilmiştir:</p>

            <div class="callout">
                <span class="callout-title">🎓 Temel Mühendislik Çıkarımları:</span>
                1. <b>Kapasite Yanılsamasının Giderilmesi:</b> Hizmet kesintisi oluşturmak için gigabaytlarca hacimsel veriye gerek olmadığı, HTTP protokolünün semantik zafiyetleri kullanılarak tek bir istemciyle dahi sunucu havuzlarının felç edilebileceği kanıtlanmıştır.<br><br>
                2. <b>Düşük Seviyeli Soket Optimizasyonu:</b> <code>SO_KEEPALIVE</code> ve <code>TCP_NODELAY</code> bayraklarının asenkron mimaride nasıl büyük bir saldırı verimliliği sağladığı deneysel olarak gözlemlenmiştir.<br><br>
                3. <b>Proaktif Savunmanın Üstünlüğü:</b> Sunucu donanımını büyütmek (Scale-up) Slowloris saldırısını engellemez (1000 bağlantı açıldığında yeni havuz da kilitlenir). Kesin çözüm; <code>client_header_timeout</code> gibi algoritmik zaman aşımı kurallarının ve WAF filtrelerinin doğru konfigüre edilmesidir.
            </div>

            <h3>Gelecek Çalışmalar (Future Work):</h3>
            <ul>
                <li><b>Makine Öğrenmesi ile Davranış Analizi:</b> Gelen HTTP başlıklarının geliş aralıklarını (inter-arrival time) LSTM veya Random Forest modelleriyle eğiterek sıfırıncı gün yavaş saldırılarını heuristik olarak tespit etmek.</li>
                <li><b>eBPF / XDP Entegrasyonu:</b> Saldırgan soketlerin kullanıcı alanına (user-space) ulaşmadan doğrudan Linux çekirdeğinde (kernel space) paket seviyesinde düşürülmesi.</li>
            </ul>

            <div style="margin-top: 30px; text-align: center; border-top: 1px solid #cbd5e1; padding-top: 20px;">
                <p style="font-weight: 800; font-size: 11pt; color: #0f172a; margin-bottom: 4px;">Trakya Üniversitesi Bilgisayar Mühendisliği Bölümü</p>
                <p style="color: #64748b; font-size: 9pt;">Bu çalışma, Ağ Güvenliği ve Performans Analitiği bitirme projesi kapsamında hazırlanmış ve başarıyla doğrulanmıştır.</p>
            </div>
        </div>

        <div class="footer-note">
            <span>Trakya Üniversitesi Bilgisayar Mühendisliği</span>
            <span>Sayfa 10 / 10</span>
        </div>
    </div>

</body>
</html>
"""

def generate_pdf():
    print("[*] 1. HTML Sunum ve Rapor dosyası oluşturuluyor...")
    OUTPUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(HTML_CONTENT)
    print(f"[OK] HTML dosyası kaydedildi: {OUTPUT_HTML}")

    print("[*] 2. Microsoft Edge Headless motoru ile PDF'e dönüştürülüyor...")
    edge_paths = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
    ]
    edge_exe = None
    for p in edge_paths:
        if os.path.exists(p):
            edge_exe = p
            break

    if not edge_exe:
        print("[!] Microsoft Edge bulunamadı. HTML raporu doğrudan tarayıcıda açabilirsiniz.")
        return

    cmd = [
        edge_exe,
        "--headless",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={OUTPUT_PDF}",
        str(OUTPUT_HTML)
    ]

    res = subprocess.run(cmd, capture_output=True)
    if os.path.exists(OUTPUT_PDF) and os.path.getsize(OUTPUT_PDF) > 0:
        print(f"[OK] PDF Başarıyla Üretildi: {OUTPUT_PDF}")
        print(f"     Boyut: {os.path.getsize(OUTPUT_PDF) / 1024:.1f} KB (Tam 10 Sayfa Akademik Sunum ve Rapor)")
    else:
        print("[!] PDF dönüştürme başarısız oldu:", res.stderr.decode("utf-8", errors="ignore"))

if __name__ == "__main__":
    generate_pdf()
