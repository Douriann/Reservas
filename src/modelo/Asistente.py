from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Asistente:
    cedula: str
    nombre: str
    apellido_paterno: str
    email: str
    # Campos opcionales (pueden ser None al crear el objeto)
    id_asistente: Optional[int] = None
    id_organizacion: Optional[int] = None
    apellido_materno: Optional[str] = None
    telefono: Optional[str] = None
    puesto_cargo: Optional[str] = None
    fecha_registro: Optional[datetime] = None
    estatus: bool = True

    def nombre_completo(self) -> str:
        """Retorna el nombre completo formateado para reportes."""
        if self.apellido_materno:
            return f"{self.nombre} {self.apellido_paterno} {self.apellido_materno}"
        return f"{self.nombre} {self.apellido_paterno}"