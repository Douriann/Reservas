from dataclasses import dataclass
from typing import Optional

@dataclass
class Organizacion:
    nombre_empresa: str
    id_organizacion: Optional[int] = None
    direccion: Optional[str] = None
    telefono_contacto: Optional[str] = None
    estatus: bool = True