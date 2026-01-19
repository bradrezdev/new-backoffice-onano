"""
Página principal de Admin App con UI minimalista - Diseño mobile mejorado
"""

import reflex as rx
from .admin_state import AdminState
from .components import admin_input, admin_select, admin_button, admin_alert
from NNProtect_new_website.components.shared_ui.theme import Custom_theme


def admin_header() -> rx.Component:
    """Header simple y funcional con tema claro/oscuro"""
    return rx.box(
        rx.hstack(
            rx.heading(
                "Admin Panel",
                size="6",
                color=rx.color_mode_cond(
                    light=Custom_theme().light_colors()["text"],
                    dark=Custom_theme().dark_colors()["text"]
                ),
            ),
            rx.image(
                src="/nnprotect_logo.png",
                alt="NN Protect Logo",
                height="40px"
            ),
            justify="between",
            align="center",
            padding_x="9em",
            width="100%"
        ),
        background=rx.color_mode_cond(
            light=Custom_theme().light_colors()["tertiary"],
            dark=Custom_theme().dark_colors()["tertiary"]
        ),
        padding="1em 2em",
        border_bottom=f"1px solid {rx.color_mode_cond(light='#E5E7EB', dark='#374151')}",
        position="sticky",
        top="0",
        z_index="1",
    )


def admin_alert_banner() -> rx.Component:
    """Banner de alertas"""
    return rx.cond(
        AdminState.show_alert,
        rx.box(
            admin_alert(AdminState.alert_message, AdminState.alert_variant),
            rx.button(
                "✕",
                on_click=AdminState.hide_alert,
                position="absolute",
                right="1rem",
                top="50%",
                transform="translateY(-50%)",
                background="transparent",
                border="none",
                cursor="pointer",
                font_size="1.25rem",
                color=rx.color_mode_cond(light=Custom_theme().light_colors()["primary"], dark=Custom_theme().dark_colors()["primary"]),
                _hover={"color": rx.color_mode_cond(light=Custom_theme().light_colors()["border"], dark=Custom_theme().dark_colors()["border"])}
            ),
            position="relative",
            margin_bottom="1.5em"
        )
    )


def section_title(title: str, subtitle: str = "") -> rx.Component:
    """Título de sección consistente con tema claro/oscuro"""
    return rx.vstack(
        rx.text(
            title,
            size="8",
            color=rx.color_mode_cond(
                light=Custom_theme().light_colors()["text"],
                dark=Custom_theme().dark_colors()["text"]
            ),
        ),
        rx.cond(
            subtitle != "",
            rx.text(
                subtitle,
                size="4",
                color=rx.color_mode_cond(
                    light="#6B7280",  # gray-600 en modo claro
                    dark="#9CA3AF"   # gray-400 en modo oscuro
                ),
            )
        ),
        spacing="1",
        align_items="start",
        width="100%",
        margin_bottom="2rem"
    )


def read_only_field(label: str, value) -> rx.Component:
    """Campo de solo lectura para mostrar información del usuario"""
    return rx.vstack(
        rx.text(
            label, 
            font_weight="600", 
            font_size="0.875rem",
            color=rx.color_mode_cond(light="#6B7280", dark="#9CA3AF")
        ),
        rx.text(
            value, 
            font_size="1rem",
            font_weight="500",
            color=rx.color_mode_cond(
                light=Custom_theme().light_colors()["text"],
                dark=Custom_theme().dark_colors()["text"]
            )
        ),
        spacing="1",
        flex="1"
    )


# ===================== TAB 1: CREAR CUENTA =====================

def tab_create_account() -> rx.Component:
    """Tab para crear cuenta sin sponsor"""
    return rx.vstack(
        section_title(
            "Crear Cuenta Master (sin Sponsor)",
            "Registra un nuevo usuario master sin necesidad de sponsor"
        ),

        # ========== INFORMACIÓN PERSONAL ==========
        # ==================== Información Personal ====================
        rx.text(
            "Información Personal",
            font_weight="700",
            font_size="1.1rem",
            color=rx.color_mode_cond(
                light=Custom_theme().light_colors()["text"],
                dark=Custom_theme().dark_colors()["text"]
            ),
            margin_top="1rem"
        ),
        
        admin_input(
            "Nombre(s)*",
            placeholder="Ej: Juan",
            value=AdminState.new_user_first_name,
            on_change=AdminState.set_new_user_first_name
        ),
        admin_input(
            "Apellido(s)*",
            placeholder="Ej: Pérez",
            value=AdminState.new_user_last_name,
            on_change=AdminState.set_new_user_last_name
        ),
        admin_select(
            "Sexo*",
            ["Masculino", "Femenino"],
            value=AdminState.new_user_gender,
            on_change=AdminState.set_new_user_gender
        ),
        admin_input(
            "Celular*",
            placeholder="Ej: 3121234567",
            value=AdminState.new_user_phone,
            on_change=AdminState.set_new_user_phone,
            input_type="tel"
        ),

        # ========== DIRECCIÓN ==========
        # ==================== Dirección ====================
        rx.text(
            "Dirección",
            font_weight="700",
            font_size="1.1rem",
            color=rx.color_mode_cond(
                light=Custom_theme().light_colors()["text"],
                dark=Custom_theme().dark_colors()["text"]
            ),
            margin_top="1.5rem"
        ),

        admin_select(
            "País*",
            ["Mexico", "USA", "Colombia", "Republica Dominicana"],
            value=AdminState.new_user_country,
            on_change=AdminState.set_new_user_country
        ),
        admin_input(
            "Calle y Número*",
            placeholder="Ej: Av. Siempre Viva #742",
            value=AdminState.new_user_street,
            on_change=AdminState.set_new_user_street
        ),
        admin_input(
            "Colonia*",
            placeholder="Ej: Centro",
            value=AdminState.new_user_neighborhood,
            on_change=AdminState.set_new_user_neighborhood
        ),
        admin_input(
            "Ciudad*",
            placeholder="Ej: Colima",
            value=AdminState.new_user_city,
            on_change=AdminState.set_new_user_city
        ),
        admin_input(
            "Estado*",
            placeholder="Ej: Colima",
            value=AdminState.new_user_state,
            on_change=AdminState.set_new_user_state
        ),
        admin_input(
            "Código Postal*",
            placeholder="Ej: 28000",
            value=AdminState.new_user_zip_code,
            on_change=AdminState.set_new_user_zip_code,
            input_type="text"
        ),

        # ========== ACCESO AL SISTEMA ==========
        # ==================== Acceso al Sistema ====================
        rx.text(
            "Acceso al Sistema",
            font_weight="700",
            font_size="1.1rem",
            color=rx.color_mode_cond(
                light=Custom_theme().light_colors()["text"],
                dark=Custom_theme().dark_colors()["text"]
            ),
            margin_top="1.5rem"
        ),
        
        admin_input(
            "Usuario*",
            placeholder="Usuario único",
            value=AdminState.new_user_username,
            on_change=AdminState.set_new_user_username
        ),
        admin_input(
            "Correo Electrónico*",
            placeholder="usuario@ejemplo.com",
            value=AdminState.new_user_email,
            on_change=AdminState.set_new_user_email,
            input_type="email"
        ),
        admin_input(
            "Contraseña*",
            placeholder="••••••••",
            value=AdminState.new_user_password,
            on_change=AdminState.set_new_user_password,
            input_type="password"
        ),
        admin_input(
            "Confirmar Contraseña*",
            placeholder="••••••••",
            value=AdminState.new_user_password_confirm,
            on_change=AdminState.set_new_user_password_confirm,
            input_type="password"
        ),

        rx.box(height="1rem"),

        admin_button(
            "Crear Cuenta Master",
            on_click=AdminState.create_account_without_sponsor,
            disabled=AdminState.is_loading_create_account,
            height="68px",
            width="100%"
        ),

        spacing="4",
        width="100%",
        max_width="600px",
    )


# ===================== TAB 2: BUSCAR USUARIO =====================

def tab_search_user() -> rx.Component:
    """Tab para buscar y ver información de usuario"""
    return rx.vstack(
        section_title(
            "Buscar Usuario",
            "Busca por Member ID o Email para ver TODA su información y organización"
        ),

        # Buscador
        admin_input(
            "Member ID o Email*",
            placeholder="Ej: 1 o usuario@ejemplo.com",
            value=AdminState.search_user_query,
            on_change=AdminState.set_search_user_query
        ),
        admin_button(
            "Buscar socio",
            on_click=AdminState.search_user,
            disabled=AdminState.is_loading_search,
            height="40px",
            width="19%",
        ),

        # Resultado del usuario - Formulario con información completa
        rx.cond(
            AdminState.has_result,
            rx.vstack(
                # ================== INFORMACIÓN SOLO LECTURA ==================
                rx.heading(
                    "📋 Información General (Solo Lectura)",
                    font_size="1.25rem",
                    font_weight="600",
                    color=rx.color_mode_cond(
                        light=Custom_theme().light_colors()["text"],
                        dark=Custom_theme().dark_colors()["text"]
                    ),
                    margin_top="2rem"
                ),
                
                rx.box(
                    rx.vstack(
                        # Fila 1: IDs Principales
                        rx.hstack(
                            read_only_field("Member ID", AdminState.result_member_id),
                            read_only_field("Email", AdminState.result_email),
                            read_only_field("Status", AdminState.result_status),
                            spacing="4",
                            width="100%"
                        ),
                        
                        # Fila 2: Red y Referencias
                        rx.hstack(
                            read_only_field("Sponsor ID", AdminState.result_sponsor_id),
                            read_only_field("Ancestor ID", AdminState.result_ancestor_id),
                            read_only_field("Referral Link", AdminState.result_referral_link),
                            spacing="4",
                            width="100%"
                        ),
                        
                        # Fila 3: Género y Fecha
                        rx.hstack(
                            read_only_field("Género", AdminState.result_gender),
                            read_only_field("Fecha de Nacimiento", AdminState.result_date_of_birth),
                            read_only_field("Fecha de Registro", AdminState.result_fecha_registro),
                            spacing="4",
                            width="100%"
                        ),
                        
                        # Fila 4: Métricas de Negocio
                        rx.hstack(
                            read_only_field("PV (Personal Volume)", AdminState.result_pv),
                            read_only_field("PVG (Personal Volume Group)", AdminState.result_pvg),
                            spacing="4",
                            width="100%"
                        ),
                        
                        # Fila 5: Rangos
                        rx.hstack(
                            read_only_field("Rango Actual", AdminState.result_current_rank),
                            read_only_field("Rango Más Alto", AdminState.result_highest_rank),
                            spacing="4",
                            width="100%"
                        ),
                        
                        spacing="6",
                        width="100%"
                    ),
                    padding="2rem",
                    border_radius="12px",
                    border=rx.color_mode_cond(
                        light="1px solid #E5E7EB",
                        dark="1px solid #374151"
                    ),
                    background=rx.color_mode_cond(
                        light="#F9FAFB",
                        dark="#1F2937"
                    ),
                    width="100%"
                ),
                
                # ================== DIRECCIONES ==================
                rx.heading(
                    "📍 Direcciones Registradas",
                    font_size="1.25rem",
                    font_weight="600",
                    color=rx.color_mode_cond(
                        light=Custom_theme().light_colors()["text"],
                        dark=Custom_theme().dark_colors()["text"]
                    ),
                    margin_top="2rem"
                ),
                
                rx.cond(
                    AdminState.result_addresses,
                    rx.box(
                        rx.vstack(
                            rx.foreach(
                                AdminState.result_addresses,
                                lambda addr: rx.box(
                                    rx.vstack(
                                        rx.text(
                                            f"{addr['street']}, {addr['city']}, {addr['state']}",
                                            font_weight="500",
                                            color=rx.color_mode_cond(
                                                light=Custom_theme().light_colors()["text"],
                                                dark=Custom_theme().dark_colors()["text"]
                                            )
                                        ),
                                        rx.text(
                                            f"CP: {addr['zip_code']}, {addr['country']}",
                                            font_size="0.875rem",
                                            color=rx.color_mode_cond(light="#6B7280", dark="#9CA3AF")
                                        ),
                                        spacing="1"
                                    ),
                                    padding="1rem",
                                    border_radius="8px",
                                    border=rx.color_mode_cond(
                                        light="1px solid #E5E7EB",
                                        dark="1px solid #374151"
                                    ),
                                    background=rx.color_mode_cond(
                                        light="#FFFFFF",
                                        dark="#111827"
                                    )
                                )
                            ),
                            spacing="3",
                            width="100%"
                        ),
                        padding="2rem",
                        border_radius="12px",
                        border=rx.color_mode_cond(
                            light="1px solid #E5E7EB",
                            dark="1px solid #374151"
                        ),
                        background=rx.color_mode_cond(
                            light="#F9FAFB",
                            dark="#1F2937"
                        ),
                        width="100%"
                    ),
                    rx.text(
                        "No hay direcciones registradas",
                        color=rx.color_mode_cond(light="#6B7280", dark="#9CA3AF"),
                        font_style="italic"
                    )
                ),
                
                # ================== CAMPOS EDITABLES ==================
                rx.heading(
                    "✏️ Información Editable",
                    font_size="1.25rem",
                    font_weight="600",
                    color=rx.color_mode_cond(
                        light=Custom_theme().light_colors()["text"],
                        dark=Custom_theme().dark_colors()["text"]
                    ),
                    margin_top="2rem"
                ),
                
                rx.box(
                    rx.vstack(
                        # Fila 1: Nombres
                        rx.hstack(
                            admin_input(
                                "Nombre*",
                                placeholder="Juan",
                                value=AdminState.result_first_name,
                                on_change=AdminState.set_result_first_name
                            ),
                            admin_input(
                                "Apellido*",
                                placeholder="Pérez",
                                value=AdminState.result_last_name,
                                on_change=AdminState.set_result_last_name
                            ),
                            spacing="4",
                            width="100%"
                        ),
                        
                        # Fila 2: Red
                        rx.hstack(
                            admin_input(
                                "Sponsor ID*",
                                placeholder="1",
                                value=AdminState.result_sponsor_id,
                                on_change=AdminState.set_result_sponsor_id,
                                input_type="number"
                            ),
                            admin_input(
                                "Ancestor ID*",
                                placeholder="1",
                                value=AdminState.result_ancestor_id,
                                on_change=AdminState.set_result_ancestor_id,
                                input_type="number"
                            ),
                            spacing="4",
                            width="100%"
                        ),
                        
                        # Fila 3: Contacto
                        rx.hstack(
                            admin_input(
                                "Teléfono*",
                                placeholder="3121234567",
                                value=AdminState.result_phone,
                                on_change=AdminState.set_result_phone,
                                input_type="tel"
                            ),
                            admin_input(
                                "País*",
                                placeholder="Mexico",
                                value=AdminState.result_country,
                                on_change=AdminState.set_result_country
                            ),
                            spacing="4",
                            width="100%"
                        ),
                        
                        # Fila 4: Fecha y Wallet
                        rx.hstack(
                            admin_input(
                                "Fecha de Nacimiento (YYYY-MM-DD)*",
                                placeholder="1990-01-15",
                                value=AdminState.result_date_of_birth,
                                on_change=AdminState.set_result_date_of_birth
                            ),
                            admin_input(
                                "Balance de Wallet*",
                                placeholder="0.00",
                                value=AdminState.result_wallet_balance,
                                on_change=AdminState.set_result_wallet_balance,
                                input_type="number"
                            ),
                            spacing="4",
                            width="100%"
                        ),
                        
                        # Botón de guardar
                        admin_button(
                            "💾 Guardar Cambios",
                            on_click=AdminState.update_user,
                            disabled=AdminState.is_updating_user,
                            width="100%"
                        ),
                        
                        spacing="6",
                        width="100%"
                    ),
                    padding="2rem",
                    border_radius="12px",
                    border=rx.color_mode_cond(
                        light="2px solid #3B82F6",
                        dark="2px solid #60A5FA"
                    ),
                    background=rx.color_mode_cond(
                        light=Custom_theme().light_colors()["tertiary"],
                        dark=Custom_theme().dark_colors()["tertiary"]
                    ),
                    width="100%"
                ),
                
                # Tabla de Organización
                rx.heading(
                    "Organización Directa",
                    font_size="1.25rem",
                    font_weight="600",
                    color=rx.color_mode_cond(
                        light=Custom_theme().light_colors()["text"],
                        dark=Custom_theme().dark_colors()["text"]
                    ),
                    margin_top="2rem"
                ),
                rx.cond(
                    AdminState.search_user_organization,
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
                                        AdminState.search_user_organization,
                                        lambda member: rx.table.row(
                                            rx.table.cell(member.nombre),
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
                            border=rx.color_mode_cond(
                                light="1px solid #E5E7EB",
                                dark="1px solid #374151"
                            ),
                            background=rx.color_mode_cond(
                                light=Custom_theme().light_colors()["tertiary"],
                                dark=Custom_theme().dark_colors()["tertiary"]
                            ),
                            min_width="800px"
                        ),
                        type="auto",
                        scrollbars="horizontal",
                        style={"width": "100%", "max_width": "100%"}
                    ),
                    rx.box(
                        rx.text(
                            "Este usuario no tiene personas en su organización directa.",
                            color=rx.color_mode_cond(
                                light="#6B7280",  # gray-500 en modo claro
                                dark="#9CA3AF"   # gray-400 en modo oscuro
                            ),
                            text_align="center"
                        ),
                        padding="2rem",
                        border_radius="12px",
                        border=rx.color_mode_cond(
                            light="1px solid #E5E7EB",
                            dark="1px solid #374151"
                        ),
                        background=rx.color_mode_cond(
                            light="#F9FAFB",  # gray-50 en modo claro
                            dark="#1F2937"   # gray-800 en modo oscuro
                        )
                    )
                ),
                spacing="4",
                width="100%",
                max_width="100%"
            )
        ),

        spacing="4",
        width="100%",
        max_width="100%",
        padding="1rem"
    )


# ===================== TAB 3: CREAR ÓRDENES =====================

def tab_create_orders() -> rx.Component:
    """Tab para crear órdenes"""
    return rx.vstack(
        section_title(
            "Crear Órdenes",
            "Genera órdenes con 5 productos de suplementos predefinidos"
        ),

        admin_input(
            "Member IDs* (separados por coma)",
            placeholder="1, 2, 3, 4",
            value=AdminState.orders_member_ids,
            on_change=AdminState.set_orders_member_ids
        ),
        admin_input(
            "Cantidad de Órdenes* por Usuario (máx. 10)",
            placeholder="1",
            value=AdminState.orders_quantity,
            on_change=AdminState.set_orders_quantity,
            input_type="number"
        ),

        rx.box(
            rx.text(
                "ℹ️ Cada orden incluirá 5 productos de suplementos",
                font_size="0.875rem",
                color=rx.color_mode_cond(
                    light=Custom_theme().light_colors()["text"],
                    dark=Custom_theme().dark_colors()["text"]
                )
            ),
            background=rx.color_mode_cond(
                light="#EFF6FF",  # blue-50
                dark="#1E3A8A"   # blue-900
            ),
            padding="0.875rem 1rem",
            border_radius="12px",
            margin_y="1rem",
            border=rx.color_mode_cond(
                light=f"1px solid {Custom_theme().light_colors()['primary']}40",
                dark=f"1px solid {Custom_theme().dark_colors()['secondary']}40"
            )
        ),

        admin_button(
            "Crear Órdenes",
            on_click=AdminState.create_orders,
            disabled=AdminState.is_loading_orders,
            width="100%"
        ),

        spacing="4",
        width="100%",
        max_width="600px",
    )


# ===================== TAB 4: RED DESCENDENTE =====================

def tab_network_tree() -> rx.Component:
    """Tab para crear red descendente"""
    return rx.vstack(
        section_title(
            "Crear Red Descendente",
            "Genera una estructura completa de red multinivel configurable"
        ),

        admin_input(
            "Member ID Raíz",
            placeholder="1",
            value=AdminState.network_root_member_id,
            on_change=AdminState.set_network_root_member_id,
            input_type="number"
        ),
        admin_select(
            "Estructura de Red",
            ["2x2", "3x3", "4x4", "5x5"],
            value=AdminState.network_structure,
            on_change=AdminState.set_network_structure
        ),
        admin_select(
            "Profundidad (1-20 niveles)",
            [str(i) for i in range(1, 21)],
            value=AdminState.network_depth,
            on_change=AdminState.set_network_depth
        ),
        admin_select(
            "País de Registro",
            ["México", "USA", "Colombia", "República Dominicana", "Al azar"],
            value=AdminState.network_country,
            on_change=AdminState.set_network_country
        ),
        
        rx.box(
            rx.hstack(
                rx.checkbox(
                    checked=AdminState.network_create_orders,
                    on_change=AdminState.set_network_create_orders,
                    size="3"
                ),
                rx.text(
                    "Crear órdenes con 5 productos para cada usuario",
                    font_size="0.95rem",
                    #color=COLORS["gray_700"]
                ),
                spacing="2",
                align="center"
            ),
            padding="0.75rem",
            border_radius="8px",
            width="100%"
        ),

        rx.box(
            rx.text(
                "⚠️ Esta operación puede tomar varios minutos según la profundidad. Máximo 10,000 usuarios por operación.",
                font_size="0.875rem",
                #color=COLORS["gray_700"]
            ),
            background=rx.color_mode_cond(
                light=Custom_theme().light_colors()["warning_light"],
                dark=Custom_theme().dark_colors()["warning_light"]
            ),
            padding="0.875rem 1rem",
            border_radius="12px",
            margin_y="1rem",
            border=f"1px solid {rx.color_mode_cond(light=Custom_theme().light_colors()["warning"], dark=Custom_theme().dark_colors()["warning"])}40"
        ),
        
        # Contadores de estimación
        rx.cond(
            AdminState.network_estimated_users > 0,
            rx.vstack(
                rx.box(
                    rx.vstack(
                        rx.hstack(
                            rx.icon("users", size=20),
                            rx.text(
                                "Usuarios a crear:",
                                font_weight="600",
                                #color=COLORS["gray_700"]
                            ),
                            rx.text(
                                f"{AdminState.network_estimated_users:,}",
                                font_weight="700",
                                #color=COLORS["primary"],
                                font_size="1.1rem"
                            ),
                            spacing="2",
                            align="center"
                        ),
                        rx.cond(
                            AdminState.network_create_orders,
                            rx.vstack(
                                rx.divider(margin_y="0.5rem"),
                                rx.hstack(
                                    rx.icon("shopping-cart", size=18),
                                    rx.text(
                                        "PV por orden:",
                                        font_weight="500",
                                        #color=COLORS["gray_600"],
                                        font_size="0.9rem"
                                    ),
                                    rx.text(
                                        f"{AdminState.network_pv_per_order} PV",
                                        font_weight="600",
                                        #color=COLORS["success"]
                                    ),
                                    spacing="2",
                                    align="center"
                                ),
                                rx.hstack(
                                    rx.icon("trending-up", size=18),
                                    rx.text(
                                        "PVG total para el sponsor raíz:",
                                        font_weight="500",
                                        #color=COLORS["gray_600"],
                                        font_size="0.9rem"
                                    ),
                                    rx.text(
                                        f"{AdminState.network_total_pvg:,} PVG",
                                        font_weight="700",
                                        #color=COLORS["primary"],
                                        font_size="1.05rem"
                                    ),
                                    spacing="2",
                                    align="center"
                                ),
                                spacing="2",
                                width="100%"
                            )
                        ),
                        spacing="2",
                        width="100%"
                    ),
                    padding="1rem",
                    border_radius="12px",
                    background="linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%)",
                    border=f"2px solid {rx.color_mode_cond(light=Custom_theme().light_colors()['primary'], dark=Custom_theme().dark_colors()['secondary'])}40",
                    width="100%"
                ),
                spacing="3",
                width="100%"
            )
        ),
        
        # Progress bar (solo visible durante creación)
        rx.cond(
            AdminState.is_loading_network,
            rx.vstack(
                rx.text(
                    f"Creando usuarios... {AdminState.network_current_user} de {AdminState.network_estimated_users}",
                    font_weight="600",
                    color=rx.color_mode_cond(
                        light=Custom_theme().light_colors()["primary"],
                        dark=Custom_theme().dark_colors()["primary"]
                    ),
                    font_size="0.95rem",
                    text_align="center"
                ),
                rx.box(
                    rx.box(
                        width=f"{AdminState.network_progress}%",
                        height="100%",
                        background="white",
                        border_radius="8px",
                        transition="width 0.3s ease"
                    ),
                    width="100%",
                    height="24px",
                    border_radius="8px",
                    overflow="hidden",
                    position="relative"
                ),
                rx.text(
                    f"{AdminState.network_progress}%",
                    font_weight="700",
                    color=rx.color_mode_cond(
                        light=Custom_theme().light_colors()["primary"],
                        dark=Custom_theme().dark_colors()["primary"]
                    ),
                    font_size="1.2rem"
                ),
                spacing="2",
                width="100%",
                padding="1rem",
                border_radius="12px",
                border=f"2px solid {rx.color_mode_cond(
                    light=Custom_theme().light_colors()["primary"],
                    dark=Custom_theme().dark_colors()["secondary"]
                )}40"
            )
        ),

        admin_button(
            "Crear Red",
            on_click=AdminState.create_network_tree,
            disabled=AdminState.is_loading_network,
            width="100%"
        ),

        spacing="4",
        width="100%",
        max_width="600px",
    )


# ===================== TAB 5: WALLET =====================

def tab_wallet() -> rx.Component:
    """Tab para agregar dinero a wallet"""
    return rx.vstack(
        section_title(
            "Agregar Dinero a Billetera",
            "Añade fondos a las billeteras de uno o varios usuarios"
        ),

        admin_input(
            "Member IDs* (separados por coma)",
            placeholder="1, 2, 3, 4",
            value=AdminState.wallet_member_ids,
            on_change=AdminState.set_wallet_member_ids
        ),
        admin_input(
            "Cantidad*",
            placeholder="1000.00",
            value=AdminState.wallet_amount,
            on_change=AdminState.set_wallet_amount,
            input_type="number"
        ),
        admin_select(
            "Moneda*",
            ["MXN", "USD", "COP", "DOP"],
            value=AdminState.wallet_currency,
            on_change=AdminState.set_wallet_currency
        ),

        rx.box(
            rx.text(
                "ℹ️ El sistema convertirá automáticamente según el país del usuario",
                font_size="0.875rem",
                color=rx.color_mode_cond(
                    light=Custom_theme().light_colors()["text"],
                    dark=Custom_theme().dark_colors()["text"]
                ),
            ),
            background=rx.color_mode_cond(
                light=Custom_theme().light_colors()["info_light"],
                dark=Custom_theme().dark_colors()["info_light"]
            ),
            padding="0.875rem 1rem",
            border_radius="12px",
            margin_y="1rem",
            border=f"1px solid {rx.color_mode_cond(light=Custom_theme().light_colors()['info'], dark=Custom_theme().dark_colors()['info'])}40"
        ),

        admin_button(
            "Agregar Fondos",
            on_click=AdminState.add_money_to_wallet,
            disabled=AdminState.is_loading_wallet,
            width="100%"
        ),

        spacing="4",
        width="100%",
        max_width="600px",
    )


# ===================== TAB 6: LEALTAD =====================

def tab_loyalty() -> rx.Component:
    """Tab para agregar puntos de lealtad"""
    return rx.vstack(
        section_title(
            "Agregar Puntos de Lealtad",
            "Añade puntos al programa de lealtad de un usuario"
        ),

        admin_input(
            "Member ID*",
            placeholder="1",
            value=AdminState.loyalty_member_id,
            on_change=AdminState.set_loyalty_member_id,
            input_type="number"
        ),
        admin_input(
            "Cantidad de Puntos* (máx. 100)",
            placeholder="25",
            value=AdminState.loyalty_points,
            on_change=AdminState.set_loyalty_points,
            input_type="number"
        ),

        rx.box(
            rx.text(
                "ℹ️ El máximo de puntos de lealtad es 100",
                font_size="0.875rem",
                color=rx.color_mode_cond(
                    light=Custom_theme().light_colors()["text"],
                    dark=Custom_theme().dark_colors()["text"]
                )
            ),
            background=rx.color_mode_cond(
                light=Custom_theme().light_colors()["info_light"],
                dark=Custom_theme().dark_colors()["info_light"]
            ),
            padding="0.875rem 1rem",
            border_radius="12px",
            margin_y="1rem",
            border=f"1px solid {rx.color_mode_cond(light=Custom_theme().light_colors()['info'], dark=Custom_theme().dark_colors()['info'])}40"
        ),

        admin_button(
            "Agregar Puntos",
            on_click=AdminState.add_loyalty_points,
            disabled=AdminState.is_loading_loyalty,
            width="100%"
        ),

        spacing="4",
        width="100%",
        max_width="600px",
    )


# ===================== TAB 7: TEST COMISIONES =====================

def tab_test_commissions() -> rx.Component:
    """Tab para ejecutar cierre de período y cálculo de comisiones"""
    return rx.vstack(
        section_title(
            "Procesamiento de Comisiones",
            "Cierra el período actual, crea uno nuevo y ejecuta bonos Uninivel + Match"
        ),
        
        # Explicación
        rx.box(
            rx.vstack(
                rx.heading(
                    "⚠️ ¿Qué hace este botón?",
                    size="5",
                    color=rx.color_mode_cond(
                        light=Custom_theme().light_colors()["text"],
                        dark=Custom_theme().dark_colors()["text"]
                    ),
                ),
                rx.text(
                    "Este proceso ejecuta las siguientes acciones en orden:",
                    font_weight="600",
                    color=rx.color_mode_cond(light="#6B7280", dark="#9CA3AF")
                ),
                rx.list(
                    rx.list.item("1. Calcula el Bono Uninivel para todos los usuarios calificados"),
                    rx.list.item("2. Calcula el Bono Match (Igualación) para embajadores"),
                    rx.list.item("3. Procesa el Bono de Auto para rangos elegibles"),
                    rx.list.item("4. Deposita todas las comisiones PENDING en las wallets de los usuarios"),
                    rx.list.item("5. Resetea los volúmenes mensuales (PV)"),
                    rx.list.item("6. Cierra el período actual"),
                    rx.list.item("7. Crea un nuevo período para el siguiente mes"),
                    color=rx.color_mode_cond(light="#6B7280", dark="#9CA3AF"),
                    spacing="2"
                ),
                rx.callout(
                    "Este proceso NO puede revertirse. Úsalo solo al finalizar el mes.",
                    icon="triangle_alert",
                    color_scheme="yellow",
                    size="2",
                    margin_top="1rem"
                ),
                spacing="3",
                align="start"
            ),
            padding="1.5rem",
            border_radius="12px",
            border=f"1px solid {rx.color_mode_cond(light='#E5E7EB', dark='#374151')}",
            background=rx.color_mode_cond(light="#F9FAFB", dark="#1F2937"),
            margin_bottom="2rem"
        ),
        
        # Resultados (mostrar solo si hay datos)
        rx.cond(
            AdminState.commission_results != {},
            rx.box(
                rx.vstack(
                    rx.heading(
                        "📊 Resultados del Procesamiento",
                        size="5",
                        color=rx.color_mode_cond(
                            light=Custom_theme().light_colors()["text"],
                            dark=Custom_theme().dark_colors()["text"]
                        ),
                    ),
                    
                    # Grid de estadísticas
                    rx.grid(
                        # Período cerrado
                        rx.box(
                            rx.vstack(
                                rx.text("Período Cerrado", font_size="0.875rem", color=rx.color_mode_cond(light="#6B7280", dark="#9CA3AF")),
                                rx.text(
                                    AdminState.commission_results.get("closed_period", "N/A"),
                                    font_size="1.5rem",
                                    font_weight="700",
                                    color=rx.color_mode_cond(
                                        light=Custom_theme().light_colors()["text"],
                                        dark=Custom_theme().dark_colors()["text"]
                                    ),
                                ),
                                spacing="1",
                                align="start"
                            ),
                            padding="1rem",
                            border_radius="8px",
                            background=rx.color_mode_cond(light="#FEF3C7", dark="#78350F"),
                        ),
                        
                        # Nuevo período
                        rx.box(
                            rx.vstack(
                                rx.text("Nuevo Período", font_size="0.875rem", color=rx.color_mode_cond(light="#6B7280", dark="#9CA3AF")),
                                rx.text(
                                    AdminState.commission_results.get("new_period", "N/A"),
                                    font_size="1.5rem",
                                    font_weight="700",
                                    color=rx.color_mode_cond(
                                        light=Custom_theme().light_colors()["text"],
                                        dark=Custom_theme().dark_colors()["text"]
                                    ),
                                ),
                                spacing="1",
                                align="start"
                            ),
                            padding="1rem",
                            border_radius="8px",
                            background=rx.color_mode_cond(light="#D1FAE5", dark="#065F46"),
                        ),
                        
                        # Comisiones depositadas
                        rx.box(
                            rx.vstack(
                                rx.text("Comisiones Depositadas", font_size="0.875rem", color=rx.color_mode_cond(light="#6B7280", dark="#9CA3AF")),
                                rx.text(
                                    AdminState.commission_results.get("commissions_deposited", 0),
                                    font_size="1.5rem",
                                    font_weight="700",
                                    color=rx.color_mode_cond(
                                        light=Custom_theme().light_colors()["text"],
                                        dark=Custom_theme().dark_colors()["text"]
                                    ),
                                ),
                                spacing="1",
                                align="start"
                            ),
                            padding="1rem",
                            border_radius="8px",
                            background=rx.color_mode_cond(light="#DBEAFE", dark="#1E3A8A"),
                        ),
                        
                        # Monto total
                        rx.box(
                            rx.vstack(
                                rx.text("Monto Total Depositado", font_size="0.875rem", color=rx.color_mode_cond(light="#6B7280", dark="#9CA3AF")),
                                rx.text(
                                    f"${AdminState.commission_results.get('total_amount', 0):,.2f}",
                                    font_size="1.5rem",
                                    font_weight="700",
                                    color=rx.color_mode_cond(
                                        light=Custom_theme().light_colors()["text"],
                                        dark=Custom_theme().dark_colors()["text"]
                                    ),
                                ),
                                spacing="1",
                                align="start"
                            ),
                            padding="1rem",
                            border_radius="8px",
                            background=rx.color_mode_cond(light="#E0E7FF", dark="#3730A3"),
                        ),
                        
                        columns="2",
                        spacing="4",
                        width="100%"
                    ),
                    
                    # Detalles de bonos
                    rx.hstack(
                        rx.box(
                            rx.text(
                                f"Match: {AdminState.commission_results.get('match_bonuses', 0)}",
                                font_weight="600",
                                color=rx.color_mode_cond(light="#6B7280", dark="#9CA3AF")
                            ),
                            padding="0.5rem 1rem",
                            border_radius="6px",
                            background=rx.color_mode_cond(light="#F3F4F6", dark="#374151"),
                        ),
                        rx.box(
                            rx.text(
                                f"Auto: {AdminState.commission_results.get('auto_bonuses', 0)}",
                                font_weight="600",
                                color=rx.color_mode_cond(light="#6B7280", dark="#9CA3AF")
                            ),
                            padding="0.5rem 1rem",
                            border_radius="6px",
                            background=rx.color_mode_cond(light="#F3F4F6", dark="#374151"),
                        ),
                        rx.box(
                            rx.text(
                                f"Fallidos: {AdminState.commission_results.get('commissions_failed', 0)}",
                                font_weight="600",
                                color=rx.color_mode_cond(light="#EF4444", dark="#DC2626")
                            ),
                            padding="0.5rem 1rem",
                            border_radius="6px",
                            background=rx.color_mode_cond(light="#F3F4F6", dark="#374151"),
                        ),
                        spacing="3",
                        wrap="wrap"
                    ),
                    
                    spacing="4",
                    align="start",
                    width="100%"
                ),
                padding="1.5rem",
                border_radius="12px",
                border=f"2px solid {rx.color_mode_cond(light='#10B981', dark='#059669')}",
                background=rx.color_mode_cond(light="#ECFDF5", dark="#064E3B"),
                margin_bottom="2rem"
            )
        ),
        
        # Botón principal
        admin_button(
            "🚀 Ejecutar Cierre de Período y Calcular Comisiones",
            on_click=AdminState.process_period_end_and_commissions,
            disabled=AdminState.is_loading_commissions,
            height="68px",
            width="100%",
            color_scheme="red"  # Rojo para indicar precaución
        ),
        
        spacing="4",
        width="100%",
        max_width="800px",
    )


# ===================== PÁGINA PRINCIPAL =====================

def admin_page() -> rx.Component:
    """Página principal de Admin App - Diseño mobile optimizado"""
    return rx.box(
        admin_header(),

        rx.box(
            rx.container(
                admin_alert_banner(),

                # Tabs simplificadas
                rx.tabs.root(
                    rx.tabs.list(
                        rx.tabs.trigger("👤 Cuenta", value="create_account"),
                        rx.tabs.trigger("🔍 Buscar Usuario", value="search_user"),
                        rx.tabs.trigger("📦 Órdenes", value="create_orders"),
                        rx.tabs.trigger("🌳 Red", value="network_tree"),
                        rx.tabs.trigger("💰 Wallet", value="wallet"),
                        rx.tabs.trigger("🎁 Lealtad", value="loyalty"),
                        rx.tabs.trigger("💸 Test Comisiones", value="test_commissions"),
                        color_scheme="purple",
                    ),

                    rx.tabs.content(tab_create_account(), value="create_account"),
                    rx.tabs.content(tab_search_user(), value="search_user"),
                    rx.tabs.content(tab_create_orders(), value="create_orders"),
                    rx.tabs.content(tab_network_tree(), value="network_tree"),
                    rx.tabs.content(tab_wallet(), value="wallet"),
                    rx.tabs.content(tab_loyalty(), value="loyalty"),
                    rx.tabs.content(tab_test_commissions(), value="test_commissions"),

                    default_value="create_account",
                    variant="line",
                    width="100%",
                ),

                max_width="1200px",
                padding_y="2rem",
                padding_x="1.5rem",
            ),

            background=rx.color_mode_cond(
                light=Custom_theme().light_colors()["background"],
                dark=Custom_theme().dark_colors()["background"]
            ),
            min_height="calc(100vh - 80px)"
        ),

        width="100%",
        min_height="100vh"
    )
