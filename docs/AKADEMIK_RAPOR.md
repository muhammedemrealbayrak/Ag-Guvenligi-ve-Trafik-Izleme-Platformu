# Bilgisayar Mühendisliği Proje 1: Ağ Güvenliği ve Performans Analitiği Akademik Raporu

**Proje Başlığı:** OSI Modeli Tabanlı Ağ Anomalilerinin Sınıflandırılması, Kapasite Dayanıklılık Analitiği ve İstatistiki Trafik İzleme  
**Çalışma Alanı:** Bilgisayar Ağları, Ağ Güvenliği ve Siber Savunma Sistemleri  
**Platform:** Python 3.12 (Standart Ağ ve Eşzamanlılık Kütüphaneleri)

---

## 1. Giriş ve Problem Tanımı

Modern bilgisayar ağlarında hizmet sürekliliği (High Availability), yalnızca yetkisiz erişimlerin engellenmesiyle değil, aynı zamanda aşırı yük ve anomali durumlarında altyapının kararlılığını korumasıyla mümkündür. Ağ trafiğinde gözlemlenen olağandışı hareketlilikler; doğal kullanıcı yoğunluğu (pik saatler, ani popülerlik) kaynaklı olabileceği gibi, sistem kaynaklarını tüketmeye yönelik Katman 3, Katman 4 veya Katman 7 düzeyindeki anomalilerden de kaynaklanabilmektedir.

Bu projenin temel hedefleri şunlardır:
1. Ağ anomalilerini ve potansiyel tehditleri akademik bir taksonomi ile **OSI (Open Systems Interconnection)** referans modelinin ilgili katmanlarına göre sınıflandırmak.
2. Yerel test ortamlarında (`localhost` / `127.0.0.1`) çalışan servislerin azami yük dayanıklılığını, kuyruk davranışını ve gecikme (latency) profillerini ölçmek için standart kütüphanelerle araç geliştirmek.
3. Zaman serisi verileri üzerinden kayar pencere (**sliding window**) ve istatistiksel standart sapma (**Z-Score**) formülasyonunu kullanarak ani trafik sıçramalarını ve anomalilerini gerçek zamanlı tespit eden dedektör tasarlamak.
4. Ağ savunma mekanizmalarından **Token Bucket** hız sınırlamasını (Rate Limiting) simüle ederek servis kararlılığının korunmasını deneysel olarak ortaya koymak.

---

## 2. OSI Modeli Çerçevesinde Tehdit ve Anomali Taksonomisi

Ağ üzerindeki sapmalar, literatürde etki alanlarına göre iki ana eksende incelenir:

### 2.1. Pasif ve Aktif Anomali Ayrımı

* **Pasif Anomaliler:** Ağın veri iletim kapasitesini doğrudan tüketmeyen, ancak alışılmadık paternler veya bilgi toplama girişimleri içeren durumlardır (örneğin; sıra dışı port taramaları, ICMP haritalamaları, TCP ACK/FIN yoklamaları).
* **Aktif Anomaliler:** İletişim kanalının bant genişliğini, donanım kaynaklarını (CPU/RAM) veya servis bağlantı havuzlarını doygunluğa (saturation) ulaştırmayı hedefleyen hacimsel sapmalardır.

### 2.2. Katman Bazlı Sınıflandırma Tablosu

| Katman | Anomali Tipi | Doğası | Mühendislik Göstergeleri | Savunma ve Önleme Mekanizması |
| :--- | :--- | :--- | :--- | :--- |
| **Katman 3 (Ağ)** | ICMP / IP Parçalanma Yoğunluğu | Aktif | Yüksek Paket/Saniye (PPS), bant genişliği doygunluğu | Sınır yönlendiricide ICMP hız sınırlama, BGP Flowspec |
| **Katman 3 (Ağ)** | Topoloji / Adres Tarama | Pasif | Farklı IP'lere düzenli yankı talebi, Unreachable artışı | Ağ duvarı eşikleri, yayın (broadcast) yanıtlarını kapatma |
| **Katman 4 (Taşıma)** | TCP Durum Tablosu Doygunluğu | Aktif | Asimetrik SYN/ACK oranı, `SYN_RECV` yığılması | TCP SYN Cookies, SYN Proxy, Backlog optimizasyonu |
| **Katman 4 (Taşıma)** | Port / Servis Taraması | Pasif | Çok sayıda farklı porta tek kaynaktan başarısız denemeler, RST artışı | Stateful Inspection, dinamik IP engelleme |
| **Katman 7 (Uygulama)** | HTTP Kaynak ve Havuz Doygunluğu | Aktif | RPS sıçraması, HTTP 503/504 oranları, gecikme patlaması | Token Bucket Rate Limiting, WAF, Concurrency Throttling |
| **Katman 7 (Uygulama)** | Düşük Hızlı Bağlantı Tutma (Slow-rate)| Aktif | Düşük bant genişliğine rağmen tükenen iş parçacığı havuzu | İstemci başlık zaman aşımı (header timeout), min-transfer-rate |

---

## 3. Matematiksel Anomali Tespit Modeli

Trafik izleme modülümüzde (`traffic_monitor.py`), ani trafik sıçramalarını ve anomalilerini doğal dalgalanmalardan ayırt etmek amacıyla **Z-Score Normalizasyonu** ve **Kayar Pencere (Sliding Window)** yaklaşımı uygulanmıştır.

### 3.1. Kayar Pencere ve Temel İstatistikler

Belirli bir $W$ pencere boyutu (ör. son 15 örnek) için ortalama ($\mu$) ve standart sapma ($\sigma$) formülleri:

$$\mu = \frac{1}{W} \sum_{i=t-W+1}^{t} X_i$$

$$\sigma = \sqrt{\frac{1}{W-1} \sum_{i=t-W+1}^{t} (X_i - \mu)^2}$$

### 3.2. Z-Skoru Formülasyonu

Anlık frekans $X_t$ için standartlaştırılmış sapma katsayısı:

$$Z = \frac{X_t - \mu}{\sigma}$$

* **$Z < 1.5$:** Doğal varyasyon (Normal Kullanıcı Trafiği)
* **$1.5 \le Z < 2.5$:** Trafik artışı / Pik saat kullanımı (Yüksek Yoğunluk)
* **$2.5 \le Z < 4.0$:** Beklenmeyen hacimsel sıçrama (Trafik Anomalisi)
* **$Z \ge 4.0$:** Kritik doygunluk ve kapasite aşım riski (Kritik Anomali)

---

## 4. Ağ Yük Dayanıklılık ve Kapasite Sınır Analizi

Kapasite test modülü (`load_tester.py`), yerel bir servise kontrollü ve yüksek eşzamanlı istekler göndererek sunucunun doygunluk eşiğini ölçer:

* **İstek/Saniye (Throughput / RPS):** Sunucunun birim zamanda hatasız işleyebildiği istek adedi.
* **Gecikme Dağılımı (Latency Percentiles):**
  * **p50 (Medyan):** İsteklerin %50'sinin tamamlanma süresi.
  * **p95:** İsteklerin %95'inin altında kaldığı süre; sistemin uç yüklerdeki davranışını gösterir.
  * **p99:** En yavaş %1'lik dilim; kuyruk gecikmelerini ve thread tıkanmalarını açığa çıkarır.
* **Hata Oranı (Error Rate):** HTTP 4xx/5xx ve bağlantı zaman aşımı (timeout) yüzdesi.

---

## 5. Siber Savunma ve Kapasite Koruma Mekanizmaları

### 5.1. Token Bucket Hız Sınırlaması

Proje kapsamında geliştirilen `mock_server.py`, Katman 7 kapasite koruması için **Token Bucket** algoritması ile donatılmıştır:
* Kova sabit bir kapasiteye ($B$) sahiptir.
* Kova, saniyede $r$ adet token ile sürekli doldurulur.
* Her geçerli istek kovadan 1 token tüketir.
* Kova boşaldığında gelen istekler derhal **HTTP 429 (Too Many Requests)** durumuyla geri çevrilir; böylece arka uç veritabanı veya iş parçacığı havuzu korunmuş olur.

### 5.2. TCP SYN Cookie (Katman 4 Koruma)

Katman 4 el sıkışma kuyruğunun şişmesini engellemek için sunucu, gelen SYN talebini bellek durum tablosunda saklamak yerine; istemcinin IP'si, portu ve bir sır (secret) anahtarı üzerinden kriptografik bir sıra numarası (Sequence Number) üreterek SYN-ACK paketine ekler. İstemciden ACK geldiğinde bu numara doğrulanarak bağlantı açılır, böylece bellek tükenmesi önlenir.

---

## 6. Güvenlik ve Etik Sınırlar

Bu projede geliştirilen tüm kodlar, istem dışı veya yetkisiz ağ testlerinin önüne geçmek amacıyla:
* Yalnızca **`127.0.0.1`** ve **`localhost`** hedefleriyle çalışacak şekilde tasarlanmıştır.
* Kod seviyesinde adres doğrulama (whitelisting) denetimi uygulanmış olup, harici IP adreslerine yönelik istekler `PermissionError` fırlatarak derhal durdurulur.

---

## 7. Deneysel Analiz: 100.000 İstek Paradoksu ve DoS Kanıtlama Metodolojisi

Mühendislik testlerinde sıkça karşılaşılan *"Sunucuya 100.000 istek gönderdim ancak süreç kapanmadı/çökmedi"* gözlemi, bilgisayar ağları literatüründe iki temel kavrama dayanır:

### 7.1. Toplam İstek Sayısı ile Anlık Eşzamanlılık (Concurrency) Farkı
Bir döngü içerisinde 100.000 istek göndermek, modern bir işlemci (CPU) için sadece ardışık bellek kopyalama işlemidir. Sunucu her isteği milisaniyenin onda birinde (0.1 ms) yanıtlayıp kapattığı takdirde, CPU üzerinde hiçbir kuyruk birikmesi yaşanmaz. Önemli olan toplam istek sayısı değil; **aynı milisaniyede kaç iş parçacığının (thread) sunucu kaynaklarını kilitlediğidir**.

### 7.2. DoS (Denial of Service) Ne Anlama Gelir?
DoS saldırısı, **sunucu sürecinin tamamen kapanması (crash/segfault)** anlamına **gelmez**. DoS; sistem kaynaklarının (Worker Pool, Veritabanı Havuzu, Bellek, CPU) tükenmesi sonucu **"Meşru kullanıcıların sisteme erişememesi ve hizmet alamaması (HTTP 503 / Timeout)"** durumudur.

### 7.3. Kanıtlama Senaryosu (Worker Starvation)
Sunucunun `MAX_WORKERS = 10` iş parçacığı havuzu sınırına sahip olduğu gerçekçi bir senaryoda:
1. Saldırgan iş parçacıkları sunucunun ağır işlem gerektiren uç noktasına (`/heavy`) yüklenir.
2. 10 adet worker thread tamamen kilitlenir.
3. Bu esnada sıradan bir kullanıcı tarayıcıdan (`http://127.0.0.1:8080/`) siteyi açmaya çalıştığında, sunucu yeni bağlantı kabul edemez ve meşru kullanıcı **HTTP 503 (Service Unavailable)** hatası alır.
4. **Token Bucket / Rate Limiting** koruması devreye girdiğinde, ağır istekler sınırlandırılarak worker havuzu boşaltılır ve meşru kullanıcı **HTTP 200 OK** ile hizmet almaya devam eder.

