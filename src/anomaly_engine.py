from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional

class ThreatSeverity(str, Enum):
    NORMAL = "NORMAL"
    WARNING = "UYARI"
    CRITICAL = "KRITIK_TEHDIT"

@dataclass
class AnomalyStatus:
    status_code: str
    severity: ThreatSeverity
    title: str
    osi_layer: str
    description: str
    recommendation: str

class LiveAnomalyDetector:
    def __init__(self, slowloris_threshold: int = 15, conn_saturation_ratio: float = 0.85):
        self.slowloris_threshold = slowloris_threshold
        self.conn_saturation_ratio = conn_saturation_ratio

    def evaluate(
        self,
        active_conn: int,
        max_conn: int,
        active_workers: int,
        max_workers: int,
        slowloris_suspects: int,
        dropped_503: int,
        rps: float,
        defense_enabled: bool
    ) -> AnomalyStatus:
        conn_ratio = active_conn / max_conn if max_conn > 0 else 0.0

        if slowloris_suspects >= 10 or (conn_ratio >= self.conn_saturation_ratio and slowloris_suspects > 5):
            if defense_enabled:
                return AnomalyStatus(
                    status_code="SLOWLORIS_MITIGATED",
                    severity=ThreatSeverity.WARNING,
                    title="SLOWLORIS ANOMALİSİ ENGELLENDİ",
                    osi_layer="Katman 7 (Uygulama)",
                    description=(
                        f"Yavaş HTTP başlığı (Slowloris) saldırısı tespit edildi. Anti-Slowloris "
                        f"mekanizması şüpheli soketleri zaman aşımıyla düşürüyor."
                    ),
                    recommendation="Savunma devrede. Başlık zaman aşımı (client_header_timeout) uygulanıyor."
                )
            else:
                return AnomalyStatus(
                    status_code="SLOWLORIS_ACTIVE",
                    severity=ThreatSeverity.CRITICAL,
                    title="KRİTİK ANOMALİ: SLOWLORIS SALDIRISI AKTİF!",
                    osi_layer="Katman 7 (Uygulama)",
                    description=(
                        f"Açık soket havuzu ({active_conn}/{max_conn}) yavaş HTTP başlıklarıyla kilitlendi! "
                        f"Meşru kullanıcılar siteye erişemiyor (Denial of Service)."
                    ),
                    recommendation="Acilen 'Savunmayı Aktif Et' butonuna basarak Anti-Slowloris korumasını açın!"
                )

        if dropped_503 > 0 and conn_ratio >= self.conn_saturation_ratio:
            return AnomalyStatus(
                status_code="SERVICE_OUTAGE_DOS",
                severity=ThreatSeverity.CRITICAL,
                title="HİZMET KESİNTİSİ (DoS) GERÇEKLEŞTİ",
                osi_layer="Katman 7 (Uygulama)",
                description=(
                    f"Sunucu bağlantı havuzu tamamen doldu ({active_conn}/{max_conn}). "
                    f"Yeni gelen meşru isteklere HTTP 503 (Hizmet Verilemiyor) dönüyor."
                ),
                recommendation="Bağlantı sınırlandırmalarını veya WAF hız sınırlayıcıyı etkinleştirin."
            )

        if rps > 150:
            return AnomalyStatus(
                status_code="HIGH_VOLUME_SPIKE",
                severity=ThreatSeverity.WARNING,
                title="YÜKSEK HACİMLİ İSTEK TRAFİĞİ (SPIKE)",
                osi_layer="Katman 7 (Uygulama)",
                description=f"İstek hızı ({rps:.1f} req/s) normal temel çizginin üzerine çıktı.",
                recommendation="Trafik artışı izleniyor. Token Bucket koruması hazırda tutulmalıdır."
            )

        return AnomalyStatus(
            status_code="SYSTEM_HEALTHY",
            severity=ThreatSeverity.NORMAL,
            title="SİSTEM ÇEVRİMİÇİ VE GÜVENLİ",
            osi_layer="Tüm Katmanlar",
            description="Trafik normal kullanıcı parametreleri dahilinde. Tehdit saptanmadı.",
            recommendation="Sistem normal çalışma döngüsünde izlenmeye devam ediyor."
        )

anomaly_detector = LiveAnomalyDetector()
