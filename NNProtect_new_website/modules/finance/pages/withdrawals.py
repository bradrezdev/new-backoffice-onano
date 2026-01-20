"""Nueva Backoffice NN Protect | Retiros"""

import reflex as rx
from ....components.shared_ui.theme import Custom_theme
from rxconfig import config
from ....components.shared_ui.layout import main_container_derecha, mobile_header, desktop_sidebar, mobile_sidebar, header
from ..state.finance_state import FinanceState

def get_status_color_scheme(status: str) -> rx.Component:
    """Retorna el color scheme de badge según el estado."""
    return rx.match(
        status,
        ("PENDING", "orange"),
        ("PROCESSING", "yellow"),
        ("COMPLETED", "green"),
        ("REJECTED", "red"),
        "gray"
    )

def desktop_withdrawal_row(withdrawal: dict) -> rx.Component:
    """Renderiza una fila de retiro en la tabla de escritorio."""
    return rx.table.row(
        rx.table.row_header_cell(
            withdrawal['id'],
            font_weight="bold"
        ),
        rx.table.cell(withdrawal['method']),
        rx.table.cell(
            rx.text("$", withdrawal['amount'], font_weight="bold", color="#059669")
        ),
        rx.table.cell(withdrawal['date']),
        rx.table.cell(
            rx.badge(
                withdrawal['status'],
                color_scheme=get_status_color_scheme(withdrawal['status'])
            )
        ),
        rx.table.cell(
            rx.hstack(
                rx.button(
                    rx.icon("eye", size=16),
                    "Detalles",
                    size="2",
                    variant="soft",
                    color_scheme="blue",
                    _hover={"cursor": "pointer"}
                ),
                spacing="2",
                justify="center"
            )
        ),
    )

def mobile_withdrawal_card(withdrawal: dict) -> rx.Component:
    """Renderiza una card de retiro en la versión móvil."""
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.text(withdrawal['id'], font_weight="bold", font_size="1.1em"),
                rx.badge(
                    withdrawal['status'],
                    color_scheme=get_status_color_scheme(withdrawal['status'])
                ),
                justify="between",
                width="100%"
            ),
            rx.divider(margin_y="2"),
            rx.hstack(
                rx.text("Fecha:", color="gray", font_size="0.9em"),
                rx.text(withdrawal['date'], font_weight="medium", font_size="0.9em"),
                justify="between",
                width="100%"
            ),
            rx.hstack(
                rx.text("Método:", color="gray", font_size="0.9em"),
                rx.text(withdrawal['method'], font_weight="medium", font_size="0.9em"),
                justify="between",
                width="100%"
            ),
            rx.hstack(
                rx.text("Monto:", color="gray", font_size="0.9em"),
                rx.text("$", withdrawal['amount'], font_weight="bold", color="#059669", font_size="1.1em"),
                justify="between",
                width="100%"
            ),
            width="100%",
            spacing="3"
        ),
        bg=rx.color_mode_cond(light="white", dark="#1F2937"),
        padding="1.5em",
        border_radius="12px",
        box_shadow="0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",
        border=f"1px solid {Custom_theme().light_colors()['border']}",
        margin_bottom="1em"
    )

def stat_card(icon: str, label: str, value: str, color_scheme: str) -> rx.Component:
    """Renderiza una tarjeta de estadística."""
    # Mapeo de colores hex
    colors = {
        "green": "#059669",
        "blue": "#2563eb",
        "orange": "#f59e0b",
        "red": "#dc2626",
    }
    color_hex = colors.get(color_scheme, "#6B7280")
    
    # Mapeo de background rgba
    bg_colors = {
        "green": "rgba(5, 150, 105, 0.05)",
        "blue": "rgba(37, 99, 235, 0.05)",
        "orange": "rgba(245, 158, 11, 0.05)",
        "red": "rgba(220, 38, 38, 0.05)",
    }
    bg_color = bg_colors.get(color_scheme, "rgba(107, 114, 128, 0.05)")
    
    # Mapeo de border rgba
    border_colors = {
        "green": "rgba(5, 150, 105, 0.2)",
        "blue": "rgba(37, 99, 235, 0.2)",
        "orange": "rgba(245, 158, 11, 0.2)",
        "red": "rgba(220, 38, 38, 0.2)",
    }
    border_color = border_colors.get(color_scheme, "rgba(107, 114, 128, 0.2)")

    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.icon(icon, size=16, color=color_hex),
                rx.text(label, font_size="0.9rem", color="gray"),
                align="center",
                spacing="2"
            ),
            rx.text(value, font_size="1.5rem", font_weight="bold", color=color_hex),
            spacing="1",
            align="start"
        ),
        bg=bg_color,
        border=f"1px solid {border_color}",
        border_radius="12px",
        padding="16px",
        flex="1",
        width="100%"
    )

def withdrawals() -> rx.Component:
    return rx.center(
        # ---------------------------------------------------------------------
        # DESKTOP VIEW
        # ---------------------------------------------------------------------
        rx.desktop_only(
            rx.vstack(
                header(),  # Muestra el usuario logueado en la esquina superior derecha
                rx.hstack(
                    desktop_sidebar(),
                    # Container de la derecha. Contiene la tabla de retiros.
                    main_container_derecha(
                        rx.vstack(
                            # Navegación breadcrumb
                            rx.hstack(
                                rx.hstack(
                                    rx.text("Backoffice", size="2", color="gray"),
                                    rx.text("/", size="2", color="gray"),
                                    rx.text("Retiros", size="2", weight="medium"),
                                    spacing="2"
                                ),
                                justify="start",
                                width="100%",
                                margin_bottom="1em"
                            ),
                            
                            # Header
                            rx.hstack(
                                rx.text("💰", font_size="2rem"),
                                rx.text("Historial de retiros", font_size="2rem", font_weight="bold"),
                                align="center",
                                spacing="3",
                                margin_bottom="0.5em"
                            ),
                            
                            rx.text(
                                "Administre y revise todos sus retiros realizados",
                                font_size="1rem",
                                color="gray",
                                margin_bottom="2em"
                            ),

                            # Stats row
                            rx.hstack(
                                stat_card("trending-up", "Total retirado", f"${FinanceState.total_withdrawn_formatted}", "green"),
                                stat_card("check-check", "Completados", f"{FinanceState.count_completed}", "blue"),
                                stat_card("clock", "En proceso", f"{FinanceState.count_pending}", "orange"),
                                stat_card("x", "Rechazados", f"{FinanceState.count_rejected}", "red"),
                                spacing="4",
                                width="100%",
                                margin_bottom="2em"
                            ),

                            # Toolbar
                            rx.hstack(
                                rx.hstack(
                                    rx.icon("search", size=18, color=Custom_theme().light_colors()["primary"]),
                                    rx.input(
                                        placeholder="Buscar por # de retiro...",
                                        padding="12px 16px",
                                        border_radius="12px",
                                        border=f"1px solid {Custom_theme().light_colors()['border']}",
                                        width="300px"
                                    ),
                                    align="center",
                                    spacing="2",
                                    bg="white",
                                    padding="8px 12px",
                                    border_radius="12px",
                                    border=f"1px solid {Custom_theme().light_colors()['border']}"
                                ),
                                rx.spacer(),
                                rx.link(
                                    rx.button(
                                        rx.icon("plus", size=16),
                                        "Nuevo retiro",
                                        bg=Custom_theme().light_colors()["primary"],
                                        color="white",
                                        size="3",
                                        border_radius="12px",
                                        padding="12px 20px"
                                    ),
                                    href="/new_withdrawal"
                                ),
                                width="100%",
                                margin_bottom="1.5em"
                            ),

                            # Table Container
                            rx.box(
                                rx.table.root(
                                    rx.table.header(
                                        rx.table.row(
                                            rx.table.column_header_cell("# Retiro"),
                                            rx.table.column_header_cell("Método"),
                                            rx.table.column_header_cell("Monto"),
                                            rx.table.column_header_cell("Fecha"),
                                            rx.table.column_header_cell("Estado"),
                                            rx.table.column_header_cell("Acciones"),
                                        )
                                    ),
                                    rx.table.body(
                                        rx.foreach(
                                            FinanceState.withdrawals_list,
                                            desktop_withdrawal_row
                                        )
                                    ),
                                    variant="surface",
                                    size="3",
                                    width="100%"
                                ),
                                bg=rx.color_mode_cond(
                                    light=Custom_theme().light_colors()["tertiary"],
                                    dark=Custom_theme().dark_colors()["tertiary"]
                                ),
                                border_radius="16px",
                                padding="1em",
                                box_shadow="0 4px 6px rgba(0, 0, 0, 0.05)",
                                width="100%",
                                margin_bottom="2em"
                            ),
                            
                            width="100%"
                        ),
                    )
                ),
                width="100%"
            )
        ),

        # ---------------------------------------------------------------------
        # MOBILE VIEW
        # ---------------------------------------------------------------------
        rx.mobile_only(
            rx.vstack(
                mobile_header(),
                rx.vstack(
                    # Nav & Header
                    rx.hstack(
                        rx.text("Backoffice", size="1", color="gray"),
                        rx.text("/", size="1", color="gray"),
                        rx.text("Retiros", size="1", weight="medium"),
                        spacing="1",
                        margin_bottom="1em"
                    ),
                    rx.hstack(
                        rx.text("💰", font_size="1.5rem"),
                        rx.text("Retiros", font_size="1.5rem", font_weight="bold"),
                        align="center",
                        spacing="2",
                        margin_bottom="1em"
                    ),

                    # Mobile Stats Grid
                    rx.vstack(
                        rx.hstack(
                            stat_card("trending-up", "Total", f"${FinanceState.total_withdrawn_formatted}", "green"),
                            stat_card("check-check", "Completados", f"{FinanceState.count_completed}", "blue"),
                            width="100%",
                            spacing="2"
                        ),
                        rx.hstack(
                            stat_card("clock", "En proceso", f"{FinanceState.count_pending}", "orange"),
                            stat_card("x", "Rechazados", f"{FinanceState.count_rejected}", "red"),
                             width="100%",
                            spacing="2"
                        ),
                        width="100%",
                        spacing="2",
                        margin_bottom="1.5em"
                    ),

                    # Action Button
                    rx.link(
                        rx.button(
                            rx.icon("plus", size=16),
                            "Nuevo retiro",
                            bg=Custom_theme().light_colors()["primary"],
                            color="white",
                            size="3",
                            width="100%",
                            border_radius="12px",
                            padding="16px"
                        ),
                        href="/new_withdrawal",
                        width="100%"
                    ),

                    # Withdrawal List (Cards)
                    rx.vstack(
                        rx.foreach(
                            FinanceState.withdrawals_list,
                            mobile_withdrawal_card
                        ),
                        width="100%",
                        spacing="3",
                        margin_top="1.5em"
                    ),
                    
                    padding="16px",
                    width="100%"
                ),
                width="100%"
            )
        ),

        width="100%",
        bg=rx.color_mode_cond(
            light=Custom_theme().light_colors()["background"],
            dark=Custom_theme().dark_colors()["background"],
        ),
        on_mount=FinanceState.on_load,
    )
