# 📘 Documentación Completa: Estructura UI Admin Panel

## 🎯 Objetivo
Este documento explica **paso a paso** cómo funciona la UI del Admin Panel, desde los conceptos básicos de Reflex hasta la implementación completa del CRUD de usuarios.

---

## 📚 Tabla de Contenidos
1. [Conceptos Básicos de Reflex](#1-conceptos-básicos-de-reflex)
2. [Estructura de Archivos](#2-estructura-de-archivos)
3. [Componentes Reutilizables](#3-componentes-reutilizables)
4. [Estado y Eventos](#4-estado-y-eventos)
5. [UI del CRUD de Usuarios](#5-ui-del-crud-de-usuarios)
6. [Flujo Completo de Datos](#6-flujo-completo-de-datos)

---

## 1. Conceptos Básicos de Reflex

### ¿Qué es Reflex?
Reflex es un framework de Python para crear aplicaciones web **reactivas** (como React, pero en Python puro).

### Conceptos Clave:

#### 1.1. Componentes (`rx.Component`)
Todo en Reflex es un **componente**. Un componente es una función Python que retorna elementos visuales.

```python
def mi_componente() -> rx.Component:
    """
    -> rx.Component significa que esta función retorna un elemento visual
    
    Es como decir: "Esta función devuelve algo que se puede mostrar en pantalla"
    """
    return rx.text("Hola Mundo")
```

#### 1.2. Contenedores
Los contenedores organizan otros componentes:

**`rx.vstack`** = Vertical Stack (apila elementos verticalmente)
```python
rx.vstack(
    rx.text("Elemento 1"),  # ⬆️ Arriba
    rx.text("Elemento 2"),  # ⬇️ Abajo
    spacing="4"  # Espacio entre elementos (4 = 1rem)
)
```

**`rx.hstack`** = Horizontal Stack (apila elementos horizontalmente)
```python
rx.hstack(
    rx.text("Izquierda"),   # ⬅️
    rx.text("Derecha"),     # ➡️
    spacing="2"
)
```

**`rx.box`** = Caja flexible (como un `<div>` en HTML)
```python
rx.box(
    rx.text("Contenido"),
    padding="1rem",      # Espacio interno
    background="white",  # Color de fondo
    border_radius="8px"  # Esquinas redondeadas
)
```

#### 1.3. El Asterisco (*) - Desempaquetado
```python
# ❌ SIN asterisco - ERROR
elementos = [rx.text("A"), rx.text("B")]
rx.vstack(elementos)  # Esto NO funciona

# ✅ CON asterisco - CORRECTO
elementos = [rx.text("A"), rx.text("B")]
rx.vstack(*elementos)  # Desempaqueta la lista
# Equivale a: rx.vstack(rx.text("A"), rx.text("B"))
```

**¿Por qué?**
- `rx.vstack()` espera recibir componentes **separados**, no una lista
- El `*` "desempaqueta" la lista y pasa cada elemento como argumento separado

**Analogía:**
```python
# Es como hacer:
caja_de_galletas = ["galleta1", "galleta2", "galleta3"]

# Sin asterisco: pasas la caja entera
dar_galletas(caja_de_galletas)  # Recibe: [galleta1, galleta2, galleta3]

# Con asterisco: sacas las galletas de la caja
dar_galletas(*caja_de_galletas)  # Recibe: galleta1, galleta2, galleta3
```

---

## 2. Estructura de Archivos

```
Admin_app/
├── admin_state.py       # 🧠 LÓGICA: Estado y funciones de negocio
├── admin_page.py        # 🎨 UI: Componentes visuales
├── components.py        # 🧩 COMPONENTES: Elementos reutilizables
└── theme.py            # 🎨 TEMA: Colores y estilos
```

### 2.1. Separación de Responsabilidades

**admin_state.py** (El Cerebro):
```python
class AdminState(rx.State):
    """
    Estado = Variables que la UI puede leer y modificar
    
    Piénsalo como una "base de datos en memoria" que:
    - Almacena datos temporales
    - Ejecuta lógica de negocio
    - Se sincroniza automáticamente con la UI
    """
    
    # Variable de estado (dato)
    search_user_query: str = ""
    
    # Setter (función que modifica el dato)
    def set_search_user_query(self, value: str):
        """
        Cuando el usuario escribe en un input,
        esta función actualiza la variable
        """
        self.search_user_query = value
    
    # Evento (función que ejecuta lógica compleja)
    @rx.event
    def search_user(self):
        """
        @rx.event = Decorador que marca esta función como "evento"
        
        Un evento es una función que:
        1. Puede ser llamada desde la UI (botones, formularios)
        2. Puede hacer operaciones pesadas (consultas DB)
        3. Actualiza el estado cuando termina
        """
        # Lógica de búsqueda...
        pass
```

**admin_page.py** (La Cara):
```python
def tab_search_user() -> rx.Component:
    """
    Componente visual que:
    - Lee datos del estado (AdminState.search_user_query)
    - Muestra inputs y botones
    - Llama eventos cuando el usuario interactúa
    """
    return rx.vstack(
        # Input conectado al estado
        rx.input(
            value=AdminState.search_user_query,  # Lee del estado
            on_change=AdminState.set_search_user_query  # Escribe al estado
        ),
        # Botón que llama un evento
        rx.button(
            "Buscar",
            on_click=AdminState.search_user  # Ejecuta la búsqueda
        )
    )
```

---

## 3. Componentes Reutilizables

### 3.1. ¿Por qué crear componentes reutilizables?
**Problema:** Repetir código es tedioso y propenso a errores.

**Solución:** Crear funciones que generen componentes con estilos consistentes.

### 3.2. Ejemplo: `admin_input`

**En `components.py`:**
```python
def admin_input(
    label: str,           # Texto de la etiqueta
    placeholder: str,     # Texto de ejemplo en el input
    value,               # Valor actual (viene del estado)
    on_change,           # Función que se ejecuta al escribir
    input_type: str = "text"  # Tipo de input (text, number, email...)
) -> rx.Component:
    """
    Componente reutilizable para inputs del admin panel.
    
    VENTAJAS:
    - Estilos consistentes en toda la app
    - Cambiar el diseño en un solo lugar
    - Código más limpio y legible
    
    PARÁMETROS:
    - label: Texto que aparece arriba del input
    - placeholder: Texto gris dentro del input (ej: "Escribe aquí...")
    - value: Variable del estado que almacena lo que escribe el usuario
    - on_change: Función que actualiza el estado cuando el usuario escribe
    - input_type: Tipo de input (text=texto, number=números, email=correo)
    
    RETORNA:
    - rx.Component: Un contenedor vertical con label + input estilizado
    """
    return rx.vstack(
        # Etiqueta del input
        rx.text(
            label,
            font_size="0.875rem",      # Tamaño de fuente pequeño (14px)
            font_weight="600",          # Texto en negritas
            color=COLORS["gray_700"],   # Color gris oscuro
            margin_bottom="0.5rem"      # Espacio debajo de la etiqueta
        ),
        
        # Input estilizado
        rx.input(
            placeholder=placeholder,    # Texto de ayuda
            value=value,               # Valor actual del input
            on_change=on_change,       # Función al escribir
            type=input_type,           # Tipo de input
            width="100%",              # Ocupa todo el ancho disponible
            padding="0.75rem 1rem",    # Espacio interno (arriba/abajo izquierda/derecha)
            border_radius="12px",      # Esquinas redondeadas
            border=f"2px solid {COLORS['gray_300']}",  # Borde gris claro
            background="white",        # Fondo blanco
            font_size="0.95rem",      # Tamaño de fuente
            _focus={                   # Estilos cuando el input está enfocado (activo)
                "border": f"2px solid {COLORS['primary']}",  # Borde azul
                "outline": "none"      # Quitar borde del navegador
            }
        ),
        
        spacing="1",  # Espacio entre label e input (0.25rem)
        width="100%"  # El contenedor ocupa todo el ancho
    )
```

### 3.3. Uso del componente

**❌ SIN componente reutilizable:**
```python
# Hay que repetir TODO este código cada vez
rx.vstack(
    rx.text("Nombre", font_size="0.875rem", font_weight="600"...),
    rx.input(placeholder="Tu nombre", value=..., on_change=...),
    spacing="1"
)

rx.vstack(
    rx.text("Email", font_size="0.875rem", font_weight="600"...),
    rx.input(placeholder="Tu email", value=..., on_change=...),
    spacing="1"
)
```

**✅ CON componente reutilizable:**
```python
# Código limpio y legible
admin_input("Nombre", "Tu nombre", AdminState.name, AdminState.set_name)
admin_input("Email", "Tu email", AdminState.email, AdminState.set_email)
```

---

## 4. Estado y Eventos

### 4.1. Variables de Estado

```python
class AdminState(rx.State):
    """
    Estado = Variables que React(ive) puede observar
    
    Cuando una variable de estado cambia:
    1. Reflex detecta el cambio automáticamente
    2. Re-renderiza la UI para reflejar el nuevo valor
    3. Todo esto pasa sin recargar la página
    """
    
    # ==================== TIPOS DE VARIABLES ====================
    
    # String (texto)
    search_user_query: str = ""
    """
    : str = Anotación de tipo (dice que es texto)
    = ""  = Valor inicial (comienza vacío)
    
    Esta variable almacena lo que el usuario escribe en el input
    """
    
    # Boolean (verdadero/falso)
    is_loading_search: bool = False
    """
    : bool = Es un booleano (True o False)
    = False = Comienza en falso
    
    Controla si se muestra el spinner de carga
    """
    
    # Lista de objetos
    search_user_organization: list[OrganizationMember] = []
    """
    : list[OrganizationMember] = Lista que contiene objetos tipo OrganizationMember
    = [] = Comienza vacía
    
    Almacena los resultados de la búsqueda
    """
    
    # Campos individuales para el resultado
    result_nombre: str = ""
    result_email: str = ""
    result_pais: str = ""
    """
    Separamos los datos en campos individuales porque:
    - Reflex tiene problemas con diccionarios en la UI
    - Es más fácil acceder a AdminState.result_nombre
    - Evita errores de compilación
    """
```

### 4.2. Setters (Funciones que Modifican el Estado)

```python
def set_search_user_query(self, value: str):
    """
    Setter = Función que modifica una variable de estado
    
    PARÁMETROS:
    - self: Referencia a la instancia del estado
    - value: str = Nuevo valor que viene del input
    
    FLUJO:
    1. Usuario escribe "1" en el input
    2. El input llama: on_change=AdminState.set_search_user_query
    3. Esta función recibe value="1"
    4. Actualiza self.search_user_query = "1"
    5. Reflex detecta el cambio y actualiza la UI
    """
    self.search_user_query = value
```

### 4.3. Eventos (Funciones con Lógica Compleja)

```python
@rx.event
def search_user(self):
    """
    @rx.event = Decorador que marca esta función como "evento"
    
    ¿Qué hace el decorador?
    - Permite que la función sea llamada desde la UI
    - Maneja la sincronización con el frontend
    - Actualiza la UI automáticamente cuando termina
    
    ESTRUCTURA DE UN EVENTO:
    1. Cambiar estado inicial (ej: is_loading=True)
    2. Ejecutar lógica (consultas DB, cálculos)
    3. Actualizar estado con resultados
    4. Cambiar estado final (ej: is_loading=False)
    """
    
    # 1️⃣ Estado inicial
    self.is_loading_search = True
    self.has_result = False
    
    try:
        # 2️⃣ Lógica de negocio
        query = self.search_user_query.strip()
        member_id = int(query)
        
        # Consulta a la base de datos
        with rx.session() as session:
            user = session.exec(
                sqlmodel.select(Users)
                .where(Users.member_id == member_id)
            ).first()
        
        # 3️⃣ Actualizar estado con resultados
        if user:
            self.result_nombre = f"{user.first_name} {user.last_name}"
            self.result_email = user.email_cache or "N/A"
            self.has_result = True
        else:
            self.show_error("Usuario no encontrado")
    
    except Exception as e:
        self.show_error(f"Error: {str(e)}")
    
    finally:
        # 4️⃣ Estado final (siempre se ejecuta)
        self.is_loading_search = False
```

---

## 5. UI del CRUD de Usuarios

### 5.1. Estructura Completa con Comentarios

```python
def tab_search_user() -> rx.Component:
    """
    Componente principal de la tab "Buscar Usuario"
    
    ESTRUCTURA VISUAL:
    ┌─────────────────────────────────────┐
    │ [Título]                            │
    │ [Subtítulo]                         │
    │                                     │
    │ [Input: Member ID]  [Botón Buscar] │
    │                                     │
    │ [Tabla: Info del Usuario]          │ <- Solo si hay resultado
    │                                     │
    │ [Tabla: Organización]              │ <- Solo si hay resultado
    └─────────────────────────────────────┘
    
    RETORNA:
    - rx.Component: Contenedor vertical con todos los elementos
    """
    return rx.vstack(
        # ================== 1. ENCABEZADO ==================
        section_title(
            "Buscar Usuario",
            "Busca por Member ID para ver su información y organización"
        ),
        """
        section_title() es una función helper que retorna:
        - Un título grande
        - Un subtítulo pequeño
        - Estilos consistentes
        
        Definida en components.py o theme.py
        """
        
        # ================== 2. BUSCADOR ==================
        rx.hstack(
            """
            rx.hstack = Horizontal Stack
            Coloca elementos uno al lado del otro (⬅️➡️)
            """
            
            # Input para el Member ID
            admin_input(
                "Member ID*",                      # Label (etiqueta)
                placeholder="Ej: 1",               # Texto de ayuda
                value=AdminState.search_user_query, # Valor actual
                on_change=AdminState.set_search_user_query, # Función al escribir
                input_type="number"                # Solo acepta números
            ),
            """
            FLUJO DEL INPUT:
            1. Usuario escribe "5"
            2. on_change llama a set_search_user_query("5")
            3. AdminState.search_user_query = "5"
            4. El input se actualiza y muestra "5"
            """
            
            # Botón de búsqueda
            admin_button(
                "🔍 Buscar",                      # Texto del botón
                on_click=AdminState.search_user,  # Evento al hacer clic
                disabled=AdminState.is_loading_search, # Deshabilitado si está cargando
                width="auto"                       # Ancho automático (no 100%)
            ),
            """
            FLUJO DEL BOTÓN:
            1. Usuario hace clic
            2. on_click ejecuta AdminState.search_user()
            3. El método busca en la DB
            4. Actualiza las variables de resultado
            5. La UI se re-renderiza automáticamente
            
            disabled=AdminState.is_loading_search:
            - Si is_loading_search=True → Botón deshabilitado (gris)
            - Si is_loading_search=False → Botón habilitado (azul)
            """
            
            spacing="2",  # Espacio entre input y botón (0.5rem)
            width="100%", # Ocupa todo el ancho disponible
            max_width="600px" # Pero no más de 600px (se centra)
        ),
        
        # ================== 3. RESULTADO DEL USUARIO ==================
        rx.cond(
            """
            rx.cond = Condicional (if/else en Reflex)
            
            Sintaxis:
            rx.cond(
                condición,        # Si esto es True...
                componente_true,  # Muestra esto
                componente_false  # Si es False, muestra esto (opcional)
            )
            """
            
            AdminState.has_result,  # CONDICIÓN: ¿Hay resultado?
            """
            has_result es un boolean:
            - True: Usuario encontrado → Muestra las tablas
            - False: No hay usuario → No muestra nada
            """
            
            # 👇 SI hay resultado, muestra esto:
            rx.vstack(
                # -------- Título de la sección --------
                rx.heading(
                    "Información del Usuario",
                    font_size="1.25rem",       # 20px
                    font_weight="600",          # Semi-bold
                    color=COLORS["gray_900"],   # Gris muy oscuro
                    margin_top="2rem"           # Espacio arriba (32px)
                ),
                
                # -------- Tabla con scroll horizontal --------
                rx.scroll_area(
                    """
                    rx.scroll_area = Contenedor con scroll
                    
                    ¿Por qué?
                    La tabla puede ser muy ancha (1200px)
                    En móviles/tablets no cabe
                    El scroll permite desplazarse horizontalmente ⬅️➡️
                    """
                    
                    rx.box(
                        """
                        rx.box = Contenedor flexible
                        Envuelve la tabla para aplicar estilos
                        """
                        
                        rx.table.root(
                            """
                            rx.table.root = Componente de tabla de Reflex
                            
                            ESTRUCTURA:
                            table.root
                            ├── table.header (encabezados)
                            │   └── table.row
                            │       └── table.column_header_cell (cada columna)
                            └── table.body (contenido)
                                └── table.row (cada fila)
                                    └── table.cell (cada celda)
                            """
                            
                            # Encabezados
                            rx.table.header(
                                rx.table.row(
                                    rx.table.column_header_cell("Member ID"),
                                    rx.table.column_header_cell("Nombre"),
                                    rx.table.column_header_cell("Email"),
                                    rx.table.column_header_cell("Teléfono"),
                                    rx.table.column_header_cell("Sponsor ID"),
                                    rx.table.column_header_cell("Sponsor Nombre"),
                                    rx.table.column_header_cell("País"),
                                    rx.table.column_header_cell("Ciudad"),
                                    rx.table.column_header_cell("Estado Postal"),
                                    rx.table.column_header_cell("Fecha Registro"),
                                    rx.table.column_header_cell("Estatus"),
                                )
                            ),
                            
                            # Contenido (una sola fila con los datos)
                            rx.table.body(
                                rx.table.row(
                                    """
                                    Cada table.cell muestra un campo del resultado
                                    
                                    AdminState.result_nombre:
                                    - Lee la variable del estado
                                    - Muestra su valor en la celda
                                    - Si cambia, la UI se actualiza automáticamente
                                    """
                                    rx.table.cell(AdminState.result_member_id),
                                    rx.table.cell(AdminState.result_nombre),
                                    rx.table.cell(AdminState.result_email),
                                    rx.table.cell(AdminState.result_telefono),
                                    rx.table.cell(AdminState.result_sponsor_id),
                                    rx.table.cell(AdminState.result_sponsor_nombre),
                                    rx.table.cell(AdminState.result_pais),
                                    rx.table.cell(AdminState.result_ciudad),
                                    rx.table.cell(AdminState.result_estado_postal),
                                    rx.table.cell(AdminState.result_fecha_registro),
                                    rx.table.cell(AdminState.result_estatus),
                                )
                            ),
                            
                            width="100%",      # Ancho completo
                            variant="surface"  # Estilo predefinido de Reflex
                        ),
                        
                        # Estilos del contenedor de la tabla
                        padding="1rem",
                        border_radius="12px",
                        border=f"1px solid {COLORS['gray_200']}",
                        background="white",
                        min_width="1200px"  # ⚠️ CLAVE: Fuerza el scroll si no cabe
                        """
                        min_width="1200px":
                        - La tabla SIEMPRE tendrá al menos 1200px de ancho
                        - Si la pantalla es más pequeña → aparece scroll horizontal
                        - Garantiza que todas las columnas sean legibles
                        """
                    ),
                    
                    type="auto",              # Scroll automático
                    scrollbars="horizontal",  # Solo scroll horizontal ⬅️➡️
                    style={"width": "100%", "max_width": "100%"}
                    """
                    scrollbars="horizontal":
                    - Solo muestra barra de scroll horizontal
                    - No vertical (la tabla tiene una fila)
                    """
                ),
                
                # ================== 4. TABLA DE ORGANIZACIÓN ==================
                rx.heading(
                    "Organización Directa",
                    font_size="1.25rem",
                    font_weight="600",
                    color=COLORS["gray_900"],
                    margin_top="2rem"
                ),
                
                rx.cond(
                    """
                    Segunda condición:
                    ¿Hay personas en la organización?
                    """
                    AdminState.search_user_organization,
                    """
                    Verifica si la lista tiene elementos:
                    - [] (vacía) = False → Muestra mensaje "no tiene organización"
                    - [item1, item2] = True → Muestra la tabla
                    """
                    
                    # 👇 SI hay organización, muestra tabla
                    rx.scroll_area(
                        rx.box(
                            rx.table.root(
                                rx.table.header(
                                    rx.table.row(
                                        rx.table.column_header_cell("Nombre"),
                                        rx.table.column_header_cell("Member ID"),
                                        rx.table.column_header_cell("País"),
                                        rx.table.column_header_cell("PV"),
                                        rx.table.column_header_cell("PVG"),
                                        rx.table.column_header_cell("Nivel"),
                                        rx.table.column_header_cell("Ciudad"),
                                    )
                                ),
                                
                                rx.table.body(
                                    rx.foreach(
                                        """
                                        rx.foreach = Bucle en Reflex (equivalente a for)
                                        
                                        Sintaxis:
                                        rx.foreach(
                                            lista,           # Lista a iterar
                                            lambda item: ... # Función que procesa cada item
                                        )
                                        
                                        EJEMPLO:
                                        lista = [1, 2, 3]
                                        rx.foreach(lista, lambda x: rx.text(f"Número: {x}"))
                                        
                                        Genera:
                                        <text>Número: 1</text>
                                        <text>Número: 2</text>
                                        <text>Número: 3</text>
                                        """
                                        
                                        AdminState.search_user_organization,
                                        """
                                        Lista de objetos OrganizationMember:
                                        [
                                            OrganizationMember(nombre="Juan", member_id=2...),
                                            OrganizationMember(nombre="María", member_id=3...),
                                        ]
                                        """
                                        
                                        lambda member: rx.table.row(
                                            """
                                            lambda = Función anónima
                                            
                                            lambda member: ...
                                            - member: Cada elemento de la lista
                                            - ...: Qué hacer con cada elemento
                                            
                                            Por cada miembro de la organización:
                                            1. Toma el objeto (member)
                                            2. Extrae sus atributos (member.nombre, member.pais...)
                                            3. Crea una fila con esos datos
                                            """
                                            
                                            rx.table.cell(member.nombre),
                                            """
                                            member.nombre:
                                            - member: Objeto actual del bucle
                                            - .nombre: Atributo del objeto (definido en OrganizationMember)
                                            - Accede al valor y lo muestra
                                            """
                                            
                                            rx.table.cell(member.member_id),
                                            rx.table.cell(member.pais),
                                            rx.table.cell(member.pv),
                                            rx.table.cell(member.pvg),
                                            rx.table.cell(member.nivel),
                                            rx.table.cell(member.ciudad),
                                        )
                                    )
                                ),
                                
                                width="100%",
                                variant="surface"
                            ),
                            
                            padding="1rem",
                            border_radius="12px",
                            border=f"1px solid {COLORS['gray_200']}",
                            background="white",
                            min_width="800px"  # Fuerza scroll si no cabe
                        ),
                        
                        type="auto",
                        scrollbars="horizontal",
                        style={"width": "100%", "max_width": "100%"}
                    ),
                    
                    # 👇 SI NO hay organización, muestra mensaje
                    rx.box(
                        rx.text(
                            "Este usuario no tiene personas en su organización directa.",
                            color=COLORS["gray_500"],
                            text_align="center"
                        ),
                        padding="2rem",
                        border_radius="12px",
                        border=f"1px solid {COLORS['gray_200']}",
                        background=COLORS["gray_50"]
                    )
                ),
                
                spacing="4",      # Espacio entre elementos (1rem)
                width="100%",     # Ancho completo
                max_width="100%"  # Sin límite de ancho
            )
            # 👆 FIN del vstack que se muestra si has_result=True
        ),
        # 👆 FIN del rx.cond
        
        spacing="4",           # Espacio entre secciones principales
        width="100%",          # Ancho completo
        max_width="100%",      # Sin límite
        padding="1rem"         # Espacio interno del contenedor
    )
```

---

## 6. Flujo Completo de Datos

### 6.1. Diagrama de Flujo: Búsqueda de Usuario

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. USUARIO INTERACTÚA CON LA UI                                │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│ Usuario escribe "5" en el input                                 │
│                                                                  │
│ <input                                                           │
│   value={AdminState.search_user_query}  ← Lee: ""              │
│   on_change={AdminState.set_search_user_query} ← Llama setter  │
│ />                                                               │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. SETTER ACTUALIZA EL ESTADO                                   │
│                                                                  │
│ def set_search_user_query(self, value: str):                   │
│     self.search_user_query = value  # "5"                      │
│                                                                  │
│ Estado actual: search_user_query = "5"                          │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. REFLEX ACTUALIZA LA UI AUTOMÁTICAMENTE                       │
│                                                                  │
│ El input ahora muestra "5"                                      │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. USUARIO HACE CLIC EN "BUSCAR"                               │
│                                                                  │
│ <button                                                          │
│   on_click={AdminState.search_user}  ← Llama evento            │
│ >                                                                │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. EVENTO EJECUTA LÓGICA DE NEGOCIO                            │
│                                                                  │
│ @rx.event                                                        │
│ def search_user(self):                                          │
│     # A. Cambiar estado inicial                                │
│     self.is_loading_search = True  ← Botón se deshabilita      │
│     self.has_result = False        ← Oculta tablas             │
│                                                                  │
│     # B. Consultar base de datos                               │
│     with rx.session() as session:                               │
│         user = session.exec(                                    │
│             select(Users).where(Users.member_id == 5)          │
│         ).first()                                               │
│                                                                  │
│     # C. Actualizar estado con resultados                      │
│     if user:                                                     │
│         self.result_nombre = "Juan Pérez"                      │
│         self.result_email = "juan@example.com"                 │
│         self.result_pais = "México"                            │
│         # ... más campos ...                                    │
│         self.has_result = True  ← Muestra tablas               │
│                                                                  │
│     # D. Cambiar estado final                                  │
│     self.is_loading_search = False  ← Habilita botón           │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│ 6. REFLEX ACTUALIZA LA UI CON LOS NUEVOS DATOS                 │
│                                                                  │
│ Cambios detectados:                                             │
│ - has_result: False → True                                      │
│ - is_loading_search: True → False                              │
│ - result_nombre: "" → "Juan Pérez"                             │
│ - result_email: "" → "juan@example.com"                        │
│                                                                  │
│ Acciones:                                                        │
│ - rx.cond(has_result) detecta True → Muestra vstack con tablas│
│ - Botón se habilita (disabled=False)                           │
│ - Tabla muestra los datos de AdminState.result_*               │
└─────────────────────────────────────────────────────────────────┘
```

### 6.2. Flujo Visual Interactivo

```
ESTADO INICIAL (Página cargada)
═══════════════════════════════════════════════
┌──────────────────────────────────────────┐
│ Buscar Usuario                           │
│ Busca por Member ID...                   │
│                                          │
│ Member ID*: [        ] [🔍 Buscar]      │
│                                          │
└──────────────────────────────────────────┘

Variables de estado:
- search_user_query = ""
- has_result = False
- is_loading_search = False


USUARIO ESCRIBE "5"
═══════════════════════════════════════════════
┌──────────────────────────────────────────┐
│ Buscar Usuario                           │
│ Busca por Member ID...                   │
│                                          │
│ Member ID*: [   5    ] [🔍 Buscar]      │
│                        ↑                 │
│                  on_change llamó         │
│                  set_search_user_query   │
└──────────────────────────────────────────┘

Variables de estado:
- search_user_query = "5"  ← CAMBIÓ
- has_result = False
- is_loading_search = False


USUARIO HACE CLIC EN BUSCAR
═══════════════════════════════════════════════
┌──────────────────────────────────────────┐
│ Buscar Usuario                           │
│ Busca por Member ID...                   │
│                                          │
│ Member ID*: [   5    ] [⏳ Buscando...] │
│                        ↑                 │
│                  on_click llamó          │
│                  search_user()           │
│                  disabled=True           │
└──────────────────────────────────────────┘

Variables de estado:
- search_user_query = "5"
- has_result = False
- is_loading_search = True  ← CAMBIÓ (botón deshabilitado)


BÚSQUEDA COMPLETADA
═══════════════════════════════════════════════
┌──────────────────────────────────────────┐
│ Buscar Usuario                           │
│ Busca por Member ID...                   │
│                                          │
│ Member ID*: [   5    ] [🔍 Buscar]      │
│                                          │
│ Información del Usuario                  │
│ ┌────────────────────────────────────┐  │
│ │ Member ID │ Nombre │ Email  │ ... │  │
│ │ 5         │ Juan   │ juan@...│    │  │
│ └────────────────────────────────────┘  │
│ ← Tabla con scroll →                    │
│                                          │
│ Organización Directa                     │
│ ┌────────────────────────────────────┐  │
│ │ Nombre │ ID │ País │ PV │ PVG │..│  │
│ │ María  │ 10 │ MX   │ 50 │ 50  │  │  │
│ │ Pedro  │ 11 │ USA  │ 30 │ 30  │  │  │
│ └────────────────────────────────────┘  │
│ ← Tabla con scroll →                    │
└──────────────────────────────────────────┘

Variables de estado:
- search_user_query = "5"
- has_result = True  ← CAMBIÓ (muestra tablas)
- is_loading_search = False  ← CAMBIÓ (botón habilitado)
- result_nombre = "Juan Pérez"  ← CAMBIÓ
- result_email = "juan@example.com"  ← CAMBIÓ
- search_user_organization = [María, Pedro]  ← CAMBIÓ
```

---

## 7. Conceptos Avanzados

### 7.1. OrganizationMember: ¿Por qué una clase?

**Problema con diccionarios:**
```python
# ❌ NO FUNCIONA en Reflex UI
org_list = [
    {"nombre": "Juan", "pais": "México"},
    {"nombre": "María", "pais": "USA"}
]

# En el UI:
lambda member: rx.text(member["nombre"])  # Error de compilación
```

**Solución con clase:**
```python
# ✅ FUNCIONA
class OrganizationMember(rx.Base):
    """
    rx.Base = Clase base de Reflex para modelos de datos
    
    ¿Por qué heredar de rx.Base?
    - Reflex puede serializar/deserializar la clase
    - Compatible con la UI (puede acceder a atributos)
    - Valida tipos automáticamente
    """
    nombre: str
    member_id: int
    pais: str
    pv: int
    pvg: int
    nivel: int
    ciudad: str

# Crear objetos
org_list = [
    OrganizationMember(
        nombre="Juan",
        member_id=10,
        pais="México",
        pv=50,
        pvg=50,
        nivel=1,
        ciudad="CDMX"
    )
]

# En el UI (funciona perfectamente):
lambda member: rx.text(member.nombre)  # Acceso por atributo
```

### 7.2. rx.cond vs Python if

**Python if (no funciona en UI):**
```python
# ❌ ERROR: No se puede usar if directamente
def mi_componente():
    if AdminState.has_result:  # Esto no compila
        return rx.text("Sí hay resultado")
    else:
        return rx.text("No hay resultado")
```

**rx.cond (funciona en UI):**
```python
# ✅ CORRECTO
def mi_componente():
    return rx.cond(
        AdminState.has_result,  # Condición
        rx.text("Sí hay resultado"),  # Si True
        rx.text("No hay resultado")   # Si False (opcional)
    )
```

**¿Por qué?**
- Reflex necesita **rastrear** las condiciones para saber cuándo re-renderizar
- `if` de Python es estático (se evalúa una vez al cargar)
- `rx.cond` es reactivo (se re-evalúa cuando cambia el estado)

### 7.3. rx.foreach vs Python for

**Python for (no funciona):**
```python
# ❌ ERROR
def mi_tabla():
    filas = []
    for member in AdminState.search_user_organization:
        filas.append(rx.table.row(rx.table.cell(member.nombre)))
    return rx.table.body(*filas)  # No es reactivo
```

**rx.foreach (funciona):**
```python
# ✅ CORRECTO
def mi_tabla():
    return rx.table.body(
        rx.foreach(
            AdminState.search_user_organization,  # Lista reactiva
            lambda member: rx.table.row(          # Función para cada item
                rx.table.cell(member.nombre)
            )
        )
    )
```

**¿Por qué?**
- `for` de Python se ejecuta una sola vez
- `rx.foreach` se re-ejecuta cuando cambia la lista
- Permite agregar/quitar elementos dinámicamente

---

## 8. Mejores Prácticas

### 8.1. Nombres Descriptivos
```python
# ❌ MAL
def f1():
    return rx.box(...)

x = AdminState.d
y = AdminState.r

# ✅ BIEN
def tab_search_user():
    return rx.box(...)

search_query = AdminState.search_user_query
has_result = AdminState.has_result
```

### 8.2. Componentes Pequeños
```python
# ❌ MAL: Todo en una función gigante
def admin_page():
    return rx.vstack(
        # 500 líneas de código...
    )

# ✅ BIEN: Dividir en componentes pequeños
def admin_page():
    return rx.vstack(
        admin_header(),
        admin_tabs(),
        admin_footer()
    )

def admin_tabs():
    return rx.tabs(
        tab_search_user(),
        tab_create_account(),
        # ...
    )
```

### 8.3. Comentarios Útiles
```python
# ❌ MAL: Comentarios obvios
width="100%"  # Ancho 100%

# ✅ BIEN: Comentarios que explican el "por qué"
width="100%"  # Ocupa todo el ancho para que el scroll funcione en móviles
```

---

## 9. Resumen Ejecutivo

### Conceptos Clave:
1. **Componentes**: Funciones que retornan elementos visuales
2. **Estado**: Variables que React(ive) observa y sincroniza con la UI
3. **Eventos**: Funciones marcadas con `@rx.event` que ejecutan lógica de negocio
4. **Condicionales**: `rx.cond` para mostrar/ocultar elementos según el estado
5. **Bucles**: `rx.foreach` para iterar sobre listas de forma reactiva
6. **Desempaquetado**: `*` para pasar lista de argumentos como argumentos separados

### Flujo de Datos:
```
Usuario interactúa → Setter actualiza estado → Reflex detecta cambio → UI se actualiza
```

### Jerarquía de Componentes:
```
admin_page
├── admin_header
├── admin_tabs
│   ├── tab_search_user
│   │   ├── section_title
│   │   ├── admin_input
│   │   ├── admin_button
│   │   └── rx.table (con datos del estado)
│   ├── tab_create_account
│   └── ...
└── admin_footer
```

### Conexión Estado-UI:
- **Lectura**: `value={AdminState.campo}` → UI lee del estado
- **Escritura**: `on_change={AdminState.set_campo}` → UI escribe al estado
- **Eventos**: `on_click={AdminState.metodo}` → UI ejecuta lógica

---

## 10. Glosario

| Término | Significado | Ejemplo |
|---------|-------------|---------|
| **Componente** | Función que retorna elementos visuales | `def mi_btn() -> rx.Component` |
| **Estado** | Variables observables que sincronizan con la UI | `name: str = ""` |
| **Setter** | Función que modifica una variable de estado | `def set_name(self, v): self.name = v` |
| **Evento** | Función con lógica compleja marcada con `@rx.event` | `@rx.event def search()` |
| **Desempaquetado** | Operador `*` que convierte lista en argumentos | `rx.vstack(*lista)` |
| **rx.cond** | Condicional reactivo (if/else) | `rx.cond(estado, si_true, si_false)` |
| **rx.foreach** | Bucle reactivo (for) | `rx.foreach(lista, lambda x: ...)` |
| **rx.Base** | Clase base para modelos de datos en Reflex | `class User(rx.Base)` |
| **Stack** | Contenedor que apila elementos | `rx.vstack` (vertical), `rx.hstack` (horizontal) |
| **Scroll Area** | Contenedor con scroll | `rx.scroll_area(scrollbars="horizontal")` |

---

¡Listo! Ahora tienes una guía completa con todos los conceptos explicados detalladamente. 🎉
