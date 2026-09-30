# Ağ Güvenliği, Canlı Trafik İzleme ve DoS Analitiği Platformu (Proje 1)

**Trakya Üniversitesi Bilgisayar Mühendisliği Bölümü Lisans Mezuniyet Projesi**  
Bu platform; ağ trafiğindeki anomalileri incelemek, Katman 7 Slowloris DoS saldırılarını gerçek zamanlı izlemek ve siber savunma mekanizmalarının etkinliğini jüriye canlı olarak sunmak için geliştirilmiştir.

---

## 🌟 Öne Çıkan Özellikler

1. **Canlı SOC Web Dashboard (`http://127.0.0.1:8080/`):**
   * Tarayıcıdan açılan modern karanlık tema kontrol merkezi.
   * Açık TCP bağlantı havuzu (Slowloris hedefi: `0 / 25`) ve aktif iş parçacığı havuzu canlı göstergeleri.
   * Gelen her paketi, HTTP başlıklarını (`X-a: ...`), durum kodlarını (`200`, `429`, `503`, `TIMEOUT`) 800ms'de bir canlı listeleyen akış tablosu.
   * Tek tıkla açılıp kapatılabilen Siber Savunma (Anti-Slowloris + WAF Token Bucket) butonu.

2. **Canlı Terminal İzleme Konsolu (`python monitor.py`):**
   * Terminal üzerinden canlı ağ trafiğini, anlık RPS'i, TCP havuz doluluğunu ve IDS anomali alarmlarını gösteren NOC konsolu.

3. **Gerçekçi Katman 7 Slowloris Koruması:**
   * **Savunma KAPALI iken:** Başlık zaman aşımı 60 saniyedir. Slowloris havuzu kilitler (`25/25`), meşru kullanıcılar siteye giremez (`503 Service Unavailable / Connection Aborted`).
   * **Savunma AÇIK iken:** Anti-Slowloris `client_header_timeout = 2.5s` devreye girer. Yavaş soketler anında düşürülür, meşru kullanıcılar kesintisiz hizmet almaya devam eder.

4. **10 Sayfalık Akademik Sunum ve Rapor PDF'i:**
   * Proje kök dizininde hazır bulunan, jüriye doğrudan sunulabilecek A4 yatay formatta tam 10 sayfalık akademik rapor.

---

## 📁 Sadeleştirilmiş Salt Proje Mimarisi

```
Proje1/
├── src/
│   ├── __init__.py
│   ├── server.py                   # Akıllı Test Sunucusu, Web Dashboard ve Anti-Slowloris Motoru
│   ├── traffic_logger.py           # Gerçek Zamanlı Paket/Soket Olay Günlüğü Motoru
│   └── anomaly_engine.py           # Katman 7 Anomali ve IDS Tespit Algoritmaları
├── monitor.py                      # Canlı Terminal Ağ Trafiği ve IDS Paneli (Terminal NOC)
├── main.py                         # Ana Yönetim Konsolu (İnteraktif CLI)
├── demo_jury.py                    # Jüri için Otomatik 3 Aşamalı DoS & Savunma Sunumu
├── generate_pdf_report.py          # Sunum ve Akademik Rapor PDF Derleyicisi
├── Sunum_ve_Akademik_Rapor.pdf     # 10 Sayfalık Yüksek Çözünürlüklü Sunum ve Rapor
├── baslat_her_seyi.bat             # TEK TIKLA: Sunucu + Web Dashboard + Terminal İzleyiciyi açar
├── sunucuyu_durdur.bat             # Arka plandaki sunucuyu kapatır
├── requirements.txt                # 0 harici bağımlılık (Saf Python standart kütüphaneleri)
└── README.md                        # Kullanım kılavuzu
```

---

## 🚀 Jüri Sunumu için 3 Kolay Adım

### Adım 1: Laboratuvarı Başlat
Klasördeki [**`baslat_her_seyi.bat`**](file:///C:/Users/emrea/Desktop/Proje1/baslat_her_seyi.bat) dosyasına çift tıklayın:
1. `127.0.0.1:8080` Web Sunucusu arka planda başlar.
2. Web tarayıcınızda [**`http://127.0.0.1:8080/`**](http://127.0.0.1:8080/) canlı SOC Dashboard açılır.
3. Yan pencerede canlı terminal ağ izleyicisi (`monitor.py`) açılır.

### Adım 2: Slowloris Saldırısını Başlat
Masaüstündeki saldırı scriptini çalıştırın:
```powershell
python C:\Users\emrea\Desktop\Slowloris-Test-Script-main\slowloris_test.py
```
* İzleme ekranlarında soket havuzunun 25/25 dolduğunu ve durumun **L7 CRITICAL: SLOWLORIS ATTACK** olduğunu gösterin.
* Yeni bir sekmeden `http://127.0.0.1:8080/` açmaya çalıştığınızda sitenin kilitlendiğini (`HTTP 503 / Timeout`) gösterin.

### Adım 3: Savunmayı Aç ve Sistemi Kurtar
* Web arayüzündeki **"🛡️ SAVUNMAYI AÇ"** butonuna basın.
* Anti-Slowloris motorunun (2.5 sn zaman aşımı) yavaş soketleri temizleyerek meşru kullanıcılara anında `HTTP 200 OK` sağladığını gösterin.
