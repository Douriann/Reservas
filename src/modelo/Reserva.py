from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Reserva:
    codigo_reserva: str
    id_evento: int
    id_asistente: int
    id_estado_reserva: int
    # Opcionales
    id_reserva: Optional[int] = None
    fecha_solicitud: Optional[datetime] = None
    numero_asiento: Optional[str] = None
    total_a_pagar: Optional[float] = 0.0
    ruta_qr: Optional[str] = None
    estatus: bool = True