import reflex as rx
from sqlmodel import Field, SQLModel

class UserTreePath(SQLModel, table=True):
    """
    Estructura de árbol genealógico para el sistema MLM.
    Implementa el patrón "Path Enumeration" para consultas eficientes de jerarquía.

    Esta tabla almacena todas las relaciones ancestro-descendiente pre-calculadas,
    permitiendo consultas rápidas de línea ascendente y descendente sin recursión.

    NOTA: No necesariamente el sponsor_id puede ser el ancestro directo (depth=1).
    Un usuario puede tener un sponsor diferente al usuario directamente arriba en la jerarquía.
    Por ejemplo, un usuario puede ser patrocinado por un member_id=1 pero estar ubicado en la rama de otro usuario.
    """
    # Clave primaria compuesta
    sponsor_id: int = Field(foreign_key="users.member_id", index=True, nullable=True)  # Permitir NULL para el usuario master
    ancestor_id: int = Field(primary_key=True, foreign_key="users.member_id", index=True)
    descendant_id: int = Field(primary_key=True, foreign_key="users.member_id", index=True)
    depth: int = Field(primary_key=True)  # 0=self, 1=hijo directo, 2=nieto, etc.