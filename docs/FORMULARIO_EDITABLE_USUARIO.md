# 📝 Documentación: Formulario Editable de Usuario

## 🎯 Cambios Realizados

Se transformó la búsqueda de usuarios de una **tabla de solo lectura** a un **formulario completamente editable** con persistencia en la base de datos.

---

## ✨ Nuevas Funcionalidades

### 1. **Campos Editables** ✏️
Los siguientes campos ahora se pueden modificar directamente desde la UI:

- ✅ **Nombre Completo** (first_name + last_name)
- ✅ **Email** (email_cache en Users)
- ✅ **Teléfono** (phone_number en UserProfiles)
- ✅ **País** (country en Addresses + country_cache en Users)
- ✅ **Ciudad** (city en Addresses)
- ✅ **Estado/Código Postal** (state en Addresses)
- ✅ **Estatus** (status en Users - enum UserStatus)

### 2. **Campos de Solo Lectura** 🔒
Estos campos se muestran pero NO se pueden editar:

- 🔒 **Member ID** - Identificador único del usuario
- 🔒 **Sponsor ID** - ID del patrocinador
- 🔒 **Sponsor Nombre** - Nombre completo del patrocinador
- 🔒 **Ancestor ID** - ID del ancestro directo (depth=1 en UserTreePath) ⭐ **NUEVO**
- 🔒 **Fecha de Registro** - Fecha de creación del usuario

---

## 🆕 Campo Nuevo: Ancestor ID

### ¿Qué es el Ancestor ID?
El **Ancestor ID** es el identificador del **ancestro directo** en la jerarquía de red (árbol genealógico del MLM).

### ¿De dónde viene?
```python
# Se obtiene de la tabla UserTreePath con depth=1
tree_path = session.exec(
    sqlmodel.select(UserTreePath)
    .where(UserTreePath.descendant_id == user.member_id)
    .where(UserTreePath.depth == 1)  # ← Ancestro DIRECTO
).first()

ancestor_id = tree_path.ancestor_id if tree_path else "N/A"
```

### ¿Por qué es importante?
- **Sponsor ID**: Es quien PATROCINA al usuario (puede ser diferente)
- **Ancestor ID**: Es quien está DIRECTAMENTE ARRIBA en el árbol genealógico

**Ejemplo:**
```
Usuario Master (ID: 1)
├── Usuario A (ID: 2) - Sponsor: 1, Ancestor: 1
│   ├── Usuario B (ID: 3) - Sponsor: 2, Ancestor: 2
│   └── Usuario C (ID: 4) - Sponsor: 1, Ancestor: 2  ← Sponsor ≠ Ancestor
```

En este caso:
- Usuario C tiene **Sponsor ID = 1** (fue patrocinado por el Master)
- Usuario C tiene **Ancestor ID = 2** (está ubicado debajo del Usuario A en la red)

---

## 🔧 Cambios en el Estado (`admin_state.py`)

### Nuevos Campos de Estado

```python
# Campo para guardar el ID interno del usuario (necesario para updates)
result_user_id: int = 0

# Nuevo campo para mostrar Ancestor ID
result_ancestor_id: str = ""

# Flag para controlar el estado de actualización
is_updating_user: bool = False
```

### Nuevos Setters

Se agregaron setters para TODOS los campos editables:

```python
def set_result_nombre(self, value: str):
    """Permite editar el nombre completo del usuario"""
    self.result_nombre = value

def set_result_email(self, value: str):
    """Permite editar el email del usuario"""
    self.result_email = value

def set_result_telefono(self, value: str):
    """Permite editar el teléfono del usuario"""
    self.result_telefono = value

def set_result_pais(self, value: str):
    """Permite editar el país del usuario"""
    self.result_pais = value

def set_result_ciudad(self, value: str):
    """Permite editar la ciudad del usuario"""
    self.result_ciudad = value

def set_result_estado_postal(self, value: str):
    """Permite editar el estado/código postal"""
    self.result_estado_postal = value

def set_result_estatus(self, value: str):
    """Permite editar el estatus del usuario"""
    self.result_estatus = value
```

**¿Por qué tantos setters?**
- Reflex necesita un setter por cada campo editable
- Cada setter actualiza el estado y la UI se re-renderiza automáticamente
- Permite control granular de qué se puede editar

---

## 💾 Método `update_user()`

### Flujo Completo

```python
@rx.event
def update_user(self):
    """
    Actualiza los datos del usuario en múltiples tablas de la BD.
    
    TABLAS AFECTADAS:
    - Users: first_name, last_name, email_cache, country_cache, status
    - UserProfiles: phone_number
    - Addresses: country, city, state
    
    PROCESO:
    1. Validar que hay un usuario seleccionado
    2. Obtener el usuario de la BD por ID
    3. Actualizar nombres (dividir nombre completo)
    4. Actualizar email cache
    5. Actualizar país cache
    6. Actualizar teléfono en UserProfiles
    7. Actualizar dirección en Addresses
    8. Actualizar estatus (enum UserStatus)
    9. Commit a la BD
    10. Recargar datos actualizados
    11. Mostrar mensaje de éxito/error
    """
```

### Manejo de Nombres

```python
# Dividir nombre completo en first_name y last_name
nombre_partes = self.result_nombre.strip().split(" ", 1)

if len(nombre_partes) == 2:
    user.first_name = nombre_partes[0]   # "Juan"
    user.last_name = nombre_partes[1]    # "Pérez García"
else:
    user.first_name = nombre_partes[0]   # Solo un nombre
```

**Explicación:**
- `split(" ", 1)`: Divide solo en el PRIMER espacio
- Ejemplo: "Juan Pérez García" → ["Juan", "Pérez García"]
- Si no hay espacios: "Juan" → ["Juan"]

### Manejo de Estatus

```python
try:
    if self.result_estatus != "N/A":
        user.status = UserStatus[self.result_estatus]
except KeyError:
    pass  # Si el estatus no es válido, no lo cambiamos
```

**Valores válidos de UserStatus:**
- `NO_QUALIFIED`
- `ACTIVE`
- `SUSPENDED`
- `CANCELLED`

**¿Por qué el try/except?**
- El usuario podría escribir un estatus inválido
- En lugar de fallar, ignoramos el cambio
- Se mantiene el estatus anterior

### Actualización Cascada

```python
# 1. Actualizar Users
user.first_name = "Juan"
user.last_name = "Pérez"
user.email_cache = "juan@example.com"
user.country_cache = "Mexico"
user.status = UserStatus.ACTIVE

# 2. Actualizar UserProfiles
profile.phone_number = "3121234567"

# 3. Actualizar Addresses
address.country = "Mexico"
address.city = "Colima"
address.state = "Colima"

# 4. Commit TODO junto
session.add(user)
session.add(profile)  # Si existe
session.add(address)  # Si existe
session.commit()
```

---

## 🎨 Cambios en la UI (`admin_page.py`)

### Estructura ANTES (Tabla)

```python
# ❌ ANTES: Tabla de solo lectura con scroll horizontal
rx.table.root(
    rx.table.header(...),
    rx.table.body(
        rx.table.row(
            rx.table.cell(AdminState.result_member_id),
            rx.table.cell(AdminState.result_nombre),
            rx.table.cell(AdminState.result_email),
            # ... 11 columnas
        )
    )
)
```

**Problemas:**
- ❌ No se puede editar
- ❌ Requiere scroll horizontal (muchas columnas)
- ❌ Difícil de leer en móviles
- ❌ No es intuitivo para edición

### Estructura AHORA (Formulario)

```python
# ✅ AHORA: Formulario editable organizado por filas
rx.vstack(
    # Fila 1: IDs no editables
    rx.hstack(
        rx.vstack(
            rx.text("Member ID"),
            rx.text(AdminState.result_member_id)
        ),
        rx.vstack(
            rx.text("Sponsor ID"),
            rx.text(AdminState.result_sponsor_id)
        ),
        # ... más IDs
    ),
    
    # Fila 2: Nombre y Email editables
    rx.hstack(
        admin_input("Nombre", value=..., on_change=...),
        admin_input("Email", value=..., on_change=...)
    ),
    
    # Fila 3-5: Más campos editables
    # ...
    
    # Botón de guardar
    admin_button("💾 Guardar Cambios", on_click=AdminState.update_user)
)
```

**Ventajas:**
- ✅ Campos editables con inputs nativos
- ✅ Organizado en filas lógicas
- ✅ No requiere scroll horizontal
- ✅ Responsive en móviles
- ✅ Intuitivo y familiar

---

## 📐 Diseño del Formulario

### Fila 1: Identificadores (No Editables)

```
┌────────────────────────────────────────────────────────┐
│ Member ID │ Sponsor ID │ Sponsor Nombre │ Ancestor ID │
│    5      │     1      │   Juan Pérez   │      2      │
└────────────────────────────────────────────────────────┘
```

**Por qué no son editables:**
- Member ID: Identificador único, no se debe cambiar
- Sponsor ID: Define relación de patrocinio (cambiar rompería la red)
- Sponsor Nombre: Es solo informativo (calculado del Sponsor ID)
- Ancestor ID: Es calculado del árbol (no se puede cambiar manualmente)

### Fila 2: Información de Contacto (Editables)

```
┌───────────────────────────────────────────────────────┐
│ [Nombre Completo*           ] [Email*               ] │
│  Juan Pérez García            juan@example.com        │
└───────────────────────────────────────────────────────┘
```

### Fila 3: Ubicación 1 (Editables)

```
┌───────────────────────────────────────────────────────┐
│ [Teléfono*                  ] [País*                ] │
│  3121234567                   Mexico                  │
└───────────────────────────────────────────────────────┘
```

### Fila 4: Ubicación 2 (Editables)

```
┌───────────────────────────────────────────────────────┐
│ [Ciudad*                    ] [Estado/CP*           ] │
│  Colima                       Colima                  │
└───────────────────────────────────────────────────────┘
```

### Fila 5: Metadata (Mixto)

```
┌───────────────────────────────────────────────────────┐
│ Fecha de Registro        │ [Estatus*               ] │
│ 2024-01-15 10:30:00       ACTIVE                     │
└───────────────────────────────────────────────────────┘
```

### Botón de Acción

```
┌───────────────────────────────────────────────────────┐
│                  [💾 Guardar Cambios]                 │
└───────────────────────────────────────────────────────┘
```

---

## 🎨 Estilos y Temas

### Campos No Editables

```python
# Label (gris medio/claro)
rx.text(
    "Member ID",
    font_weight="600",
    font_size="0.875rem",
    color=rx.color_mode_cond(
        light="#6B7280",  # Gris medio en claro
        dark="#9CA3AF"   # Gris claro en oscuro
    )
)

# Valor (texto principal)
rx.text(
    AdminState.result_member_id,
    font_size="1rem",
    font_weight="500",
    color=rx.color_mode_cond(
        light=Custom_theme().light_colors()["text"],  # Negro
        dark=Custom_theme().dark_colors()["text"]     # Blanco
    )
)
```

### Campos Editables

```python
# Usan el componente admin_input que ya tiene estilos oficiales
admin_input(
    "Nombre Completo*",
    placeholder="Nombre Apellido",
    value=AdminState.result_nombre,
    on_change=AdminState.set_result_nombre
)
```

### Contenedor del Formulario

```python
rx.box(
    # ... contenido del formulario ...
    padding="2rem",           # Espaciado interno generoso
    border_radius="12px",     # Bordes redondeados
    border=rx.color_mode_cond(
        light="1px solid #E5E7EB",  # Borde gris claro
        dark="1px solid #374151"   # Borde gris medio
    ),
    background=rx.color_mode_cond(
        light=Custom_theme().light_colors()["tertiary"],  # Blanco
        dark=Custom_theme().dark_colors()["tertiary"]     # Gris oscuro
    ),
    width="100%"
)
```

---

## 🔄 Flujo Completo de Usuario

### 1. **Buscar Usuario**

```
Usuario escribe "5" → Clic en "🔍 Buscar"
↓
AdminState.search_user()
↓
Query a BD (Users, UserProfiles, Addresses, UserTreePath)
↓
Poblar campos de resultado (result_*)
↓
has_result = True
↓
UI muestra formulario editable
```

### 2. **Editar Campos**

```
Usuario edita "Nombre" → on_change llama set_result_nombre()
↓
AdminState.result_nombre = "Nuevo Nombre"
↓
UI se actualiza automáticamente (reactivo)
↓
Usuario edita más campos...
↓
Usuario ve cambios en tiempo real (pero NO guardados aún)
```

### 3. **Guardar Cambios**

```
Usuario clic en "💾 Guardar Cambios"
↓
AdminState.update_user()
↓
is_updating_user = True (deshabilita botón)
↓
Query usuario por result_user_id
↓
Actualizar Users (nombre, email, país, estatus)
↓
Actualizar UserProfiles (teléfono)
↓
Actualizar Addresses (país, ciudad, estado)
↓
session.commit()
↓
Mensaje de éxito
↓
Recargar datos (search_user())
↓
is_updating_user = False (habilita botón)
```

---

## ⚠️ Validaciones y Manejo de Errores

### 1. **Usuario No Seleccionado**

```python
if self.result_user_id == 0:
    self.show_error("No hay usuario seleccionado para actualizar")
    return
```

### 2. **Usuario No Encontrado en BD**

```python
if not user:
    self.show_error("Usuario no encontrado en la base de datos")
    return
```

### 3. **Estatus Inválido**

```python
try:
    user.status = UserStatus[self.result_estatus]
except KeyError:
    pass  # Ignorar si el estatus no existe
```

### 4. **Campos "N/A"**

```python
# Solo actualizar si el valor NO es "N/A"
if self.result_email != "N/A":
    user.email_cache = self.result_email
```

### 5. **Perfil o Dirección No Existe**

```python
# Verificar que existan antes de actualizar
if profile:
    profile.phone_number = self.result_telefono

if address:
    address.city = self.result_ciudad
```

---

## 📊 Resumen de Cambios

| Aspecto | Antes | Ahora |
|---------|-------|-------|
| **UI** | Tabla de solo lectura | Formulario editable |
| **Campos Editables** | 0 | 7 campos |
| **Scroll** | Horizontal (molesto) | No necesario |
| **Responsive** | Malo (muchas columnas) | Bueno (filas adaptativas) |
| **Ancestor ID** | ❌ No mostrado | ✅ Visible |
| **Actualización BD** | ❌ No posible | ✅ Botón "Guardar" |
| **Validaciones** | N/A | ✅ Completas |
| **Feedback** | N/A | ✅ Mensajes éxito/error |
| **Recarga Datos** | Manual | ✅ Automática tras guardar |

---

## 🚀 Ventajas del Nuevo Sistema

### Para el Administrador:
✅ Puede editar usuarios directamente desde el admin panel
✅ No necesita acceso directo a la base de datos
✅ Interfaz intuitiva y familiar (formulario)
✅ Ve cambios en tiempo real antes de guardar
✅ Recibe confirmación inmediata de éxito/error

### Para el Desarrollo:
✅ Código más limpio y mantenible
✅ Separación clara de responsabilidades (estado vs UI)
✅ Fácil agregar más campos editables
✅ Validaciones centralizadas
✅ Manejo robusto de errores

### Para la BD:
✅ Actualizaciones atómicas (todo o nada)
✅ Integridad referencial preservada
✅ No se modifican IDs críticos
✅ Validaciones de tipo (enums, strings)

---

## 🎓 Conclusión

La transformación de tabla a formulario mejora significativamente la experiencia de administración de usuarios. El admin ahora puede:

1. 🔍 Buscar usuarios por Member ID
2. 👁️ Ver toda su información (incluido Ancestor ID)
3. ✏️ Editar 7 campos diferentes
4. 💾 Guardar cambios con un clic
5. ✅ Recibir confirmación inmediata
6. 🔄 Ver datos actualizados automáticamente

Todo esto mientras se mantiene la seguridad (campos críticos protegidos) y la integridad de la base de datos. 🚀
