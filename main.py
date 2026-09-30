import argparse
import os
import subprocess
import sys
import time

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from src.server import ensure_server_running, run_test_server

def print_banner():
    banner = r"""
================================================================================
    AĞ GÜVENLİĞİ, CANLI TRAFİK İZLEME VE DoS ANALİTİĞİ PLATFORMU
      Trakya Üniversitesi Bilgisayar Mühendisliği Mezuniyet Projesi
================================================================================
    """
    print(banner)

def show_taxonomy():
    taxonomy_data = [
        {
            "id": "L3-01",
            "name": "ICMP & IP Parçalanma Yoğunluğu",
            "layer": "Katman 3 (Ağ / Network)",
            "nature": "Aktif Anomali",
            "mechanism": "Aşırı hacimsel paket akışıyla yönlendirici ve bant genişliğini tüketme.",
            "indicators": ["Aşırı yüksek PPS", "Bant genişliği doygunluğu", "ICMP Echo yığılması"],
            "defense": "BGP Flowspec, Sınır yönlendiricide ICMP hız kısıtlama, Rate Limiting",
        },
        {
            "id": "L4-01",
            "name": "TCP SYN Durum Tablosu Doygunluğu (SYN Flood)",
            "layer": "Katman 4 (Taşıma / Transport)",
            "nature": "Aktif Anomali",
            "mechanism": "3-Way Handshake ACK adımını tamamlamayarak SYN_RECV kuyruğunu şişirme.",
            "indicators": ["Asimetrik SYN/ACK oranı", "SYN_RECV durum patlaması", "Bellek baskısı"],
            "defense": "TCP SYN Cookies (RFC 4987), SYN Proxy, Backlog kuyruk artırımı",
        },
        {
            "id": "L7-01",
            "name": "Slowloris Düşük Hızlı Bağlantı Tutma (Slow-rate DoS)",
            "layer": "Katman 7 (Uygulama / Application)",
            "nature": "Aktif / Asimetrik Tehdit",
            "mechanism": "Eksik HTTP başlığı (\\r\\n olmadan) göndererek sunucu iş parçacığı havuzunu kilitleme.",
            "indicators": ["Maksimum açık soket sayısı", "Düşük bant genişliği (KB/s)", "HTTP 503 Outage"],
            "defense": "client_header_timeout (2.5 sn), min_data_rate kontrolü, SO_LINGER reset",
        },
        {
            "id": "L7-02",
            "name": "HTTP İstek Seli & Kaynak Tüketimi (HTTP Flood)",
            "layer": "Katman 7 (Uygulama / Application)",
            "nature": "Aktif Anomali",
            "mechanism": "Geçerli HTTP istekleriyle web sunucusunun CPU/RAM ve veritabanı kaynaklarını boğma.",
            "indicators": ["RPS patlaması", "Ortalama yanıt süresi artışı (>2000ms)", "Yüksek 503/504"],
            "defense": "Token Bucket / Leaky Bucket Hız Sınırlaması, Web Application Firewall (WAF)",
        },
    ]

    print("\n" + "=" * 90)
    print("           OSI MODELİNE GÖRE AĞ TEHDİT VE ANOMALİ SINIFLANDIRMASI")
    print("=" * 90)

    for p in taxonomy_data:
        print(f"\n[ID: {p['id']}] {p['name']}")
        print(f"  |-- OSI Katmanı        : {p['layer']}")
        print(f"  |-- Anomali Doğası     : {p['nature']}")
        print(f"  |-- Mekanizma/Etki     : {p['mechanism']}")
        print(f"  |-- Mühendislik İzi    : {', '.join(p['indicators'])}")
        print(f"  \\-- Savunma Stratejisi : {p['defense']}")

    print("\n" + "=" * 90)

def start_server_action(port: int = 8080):
    print(f"\n[*] Web Dashboard ve Test Sunucusu 127.0.0.1:{port} adresinde başlatılıyor...")
    print(f"[*] Tarayıcınızdan açabilirsiniz: http://127.0.0.1:{port}/")
    print("[*] Durdurmak için CTRL+C tuşlarına basabilirsiniz.")
    run_test_server(host="127.0.0.1", port=port)

def run_jury_demo():
    ensure_server_running("127.0.0.1", 8080)
    import demo_jury
    demo_jury.main()

def run_monitor_action():
    ensure_server_running("127.0.0.1", 8080)
    import monitor
    monitor.run_monitor()

def open_report():
    pdf_path = os.path.join(os.path.dirname(__file__), "Sunum_ve_Akademik_Rapor.pdf")
    html_path = os.path.join(os.path.dirname(__file__), "docs", "Sunum_ve_Akademik_Rapor.html")

    if os.path.exists(pdf_path):
        print(f"\n[*] Akademik Sunum ve Rapor PDF'i açılıyor: {pdf_path}")
        os.startfile(pdf_path)
    elif os.path.exists(html_path):
        print(f"\n[*] HTML Sunum ve Rapor açılıyor: {html_path}")
        os.startfile(html_path)
    else:
        print("[!] Rapor dosyası bulunamadı. Lütfen 'python generate_pdf_report.py' çalıştırınız.")

def interactive_menu():
    while True:
        print_banner()
        print("1. Web Dashboard ve Test Sunucusunu Başlat (http://127.0.0.1:8080)")
        print("2. Canlı Terminal Ağ Trafiği ve IDS Paneli (NOC Console)")
        print("3. Jüri Canlı Slowloris ve Siber Savunma Demosunu Çalıştır")
        print("4. Akademik Sunum ve Rapor PDF'ini Aç (10 Sayfalık Sunum)")
        print("5. OSI Modeline Göre Akademik Tehdit Taksonomisini Görüntüle")
        print("0. Çıkış")
        print("-" * 80)

        choice = input("Lütfen seçim yapınız (0-5): ").strip()
        if choice == "1":
            start_server_action()
            input("\nMenüye dönmek için ENTER tuşuna basınız...")
        elif choice == "2":
            run_monitor_action()
            input("\nMenüye dönmek için ENTER tuşuna basınız...")
        elif choice == "3":
            run_jury_demo()
            input("\nMenüye dönmek için ENTER tuşuna basınız...")
        elif choice == "4":
            open_report()
            input("\nMenüye dönmek için ENTER tuşuna basınız...")
        elif choice == "5":
            show_taxonomy()
            input("\nMenüye dönmek için ENTER tuşuna basınız...")
        elif choice == "0":
            print("\nSistem kapatılıyor. İyi çalışmalar dileriz.")
            break
        else:
            print("[!] Geçersiz seçim, lütfen tekrar deneyiniz.")
            time.sleep(1)

def main():
    parser = argparse.ArgumentParser(description="Ağ Güvenliği ve Trafik İzleme Yönetim Konsolu")
    parser.add_argument("--server", action="store_true", help="Web Dashboard ve Sunucuyu başlat")
    parser.add_argument("--monitor", action="store_true", help="Canlı terminal izleyicisini aç")
    parser.add_argument("--jury", action="store_true", help="Jüri Slowloris ve savunma demosunu çalıştır")
    parser.add_argument("--report", action="store_true", help="Akademik rapor PDF'ini aç")
    parser.add_argument("--taxonomy", action="store_true", help="OSI taksonomi raporunu listele")

    args = parser.parse_args()

    if args.server:
        start_server_action()
    elif args.monitor:
        run_monitor_action()
    elif args.jury:
        run_jury_demo()
    elif args.report:
        open_report()
    elif args.taxonomy:
        show_taxonomy()
    else:
        interactive_menu()

if __name__ == "__main__":
    main()
