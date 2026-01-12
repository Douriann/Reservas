from dataclasses import dataclass
from datetime import date
from typing import Optional

@dataclass
class Evento:
    nombre: str
    fecha_evento: date
    capacidad_total: int
    precio_base: float
    id_evento: Optional[int] = None
    lugar: Optional[str] = None
    estatus: bool = True