"""Nueva Backoffice NN Protect | Reportes de ingresos"""

import reflex as rx
from NNProtect_new_website.components.shared_ui.theme import Custom_theme
from rxconfig import config
from NNProtect_new_website.components.shared_ui.layout import main_container_derecha, mobile_header, desktop_sidebar, mobile_sidebar, logged_in_user

def income_reports() -> rx.Component:
    return rx.center(
        rx.desktop_only(
            rx.vstack(
                logged_in_user(),
                rx.hstack(
                    desktop_sidebar(),
                    main_container_derecha(
                        rx.vstack(
                            rx.text(
                                "Reportes de ingresos",
                                font_size="2rem",
                                font_weight="bold",
                                margin_bottom="0.1em"
                            ),
                            
                            # Resumen de ingresos
                            rx.hstack(
                                rx.box(
                                    rx.vstack(
                                        rx.text("Ingresos totales", font_weight="bold", font_size="1.1rem"),
                                        rx.text("$15,420.50", font_size="2rem", font_weight="bold", color=rx.color_mode_cond(
                                            light=Custom_theme().light_colors()["primary"],
                                            dark=Custom_theme().dark_colors()["primary"]
                                        )),
                                        rx.text("Este mes", font_size="0.9rem", color="gray"),
                                        spacing="2",
                                        align="center"
                                    ),
                                    bg=rx.color_mode_cond(
                                        light=Custom_theme().light_colors()["tertiary"],
                                        dark=Custom_theme().dark_colors()["tertiary"]
                                    ),
                                    border_radius="16px",
                                    padding="2rem",
                                    width="30%"
                                ),
                                rx.box(
                                    rx.vstack(
                                        rx.text("Comisiones", font_weight="bold", font_size="1.1rem"),
                                        rx.text("$3,280.75", font_size="2rem", font_weight="bold", color=rx.color_mode_cond(
                                            light=Custom_theme().light_colors()["secondary"],
                                            dark=Custom_theme().dark_colors()["secondary"]
                                        )),
                                        rx.text("Este mes", font_size="0.9rem", color="gray"),
                                        spacing="2",
                                        align="center"
                                    ),
                                    bg=rx.color_mode_cond(
                                        light=Custom_theme().light_colors()["tertiary"],
                                        dark=Custom_theme().dark_colors()["tertiary"]
                                    ),
                                    border_radius="16px",
                                    padding="2rem",
                                    width="30%"
                                ),
                                rx.box(
                                    rx.vstack(
                                        rx.text("Bonos", font_weight="bold", font_size="1.1rem"),
                                        rx.text("$1,890.25", font_size="2rem", font_weight="bold", color="green"),
                                        rx.text("Este mes", font_size="0.9rem", color="gray"),
                                        spacing="2",
                                        align="center"
                                    ),
                                    bg=rx.color_mode_cond(
                                        light=Custom_theme().light_colors()["tertiary"],
                                        dark=Custom_theme().dark_colors()["tertiary"]
                                    ),
                                    border_radius="16px",
                                    padding="2rem",
                                    width="30%"
                                ),
                                justify="between",
                                width="100%",
                                margin_bottom="2rem"
                            ),
                            
                            # Tabla de ingresos detallada
                            rx.box(
                                rx.vstack(
                                    rx.text("Detalle de ingresos por mes", font_weight="bold", font_size="1.3rem", margin_bottom="1rem"),
                                    rx.table.root(
                                        rx.table.header(
                                            rx.table.row(
                                                rx.table.column_header_cell("Mes"),
                                                rx.table.column_header_cell("Ventas personales"),
                                                rx.table.column_header_cell("Comisiones red"),
                                                rx.table.column_header_cell("Bonos"),
                                                rx.table.column_header_cell("Total"),
                                                rx.table.column_header_cell("Estado")
                                            )
                                        ),
                                        rx.table.body(
                                            *[rx.table.row(
                                                rx.table.row_header_cell(f"Enero 2024"),
                                                rx.table.cell("$4,500.00"),
                                                rx.table.cell("$1,200.50"),
                                                rx.table.cell("$800.25"),
                                                rx.table.cell("$6,500.75", font_weight="bold"),
                                                rx.table.cell(rx.badge("Pagado", color="green"))
                                            ),
                                            rx.table.row(
                                                rx.table.row_header_cell(f"Febrero 2024"),
                                                rx.table.cell("$3,800.00"),
                                                rx.table.cell("$950.75"),
                                                rx.table.cell("$650.50"),
                                                rx.table.cell("$5,401.25", font_weight="bold"),
                                                rx.table.cell(rx.badge("Pagado", color="green"))
                                            ),
                                            rx.table.row(
                                                rx.table.row_header_cell(f"Marzo 2024"),
                                                rx.table.cell("$5,200.00"),
                                                rx.table.cell("$1,580.25"),
                                                rx.table.cell("$920.75"),
                                                rx.table.cell("$7,701.00", font_weight="bold"),
                                                rx.table.cell(rx.badge("Pendiente", color="orange"))
                                            )]
                                        ),
                                        width="100%"
                                    ),
                                    spacing="3",
                                    width="100%"
                                ),
                                bg=rx.color_mode_cond(
                                    light=Custom_theme().light_colors()["tertiary"],
                                    dark=Custom_theme().dark_colors()["tertiary"]
                                ),
                                border_radius="16px",
                                padding="2rem",
                                width="100%"
                            ),
                            
                            spacing="4",
                            width="100%",
                        )
                    ),
                    width="100%",
                ),
                align="end",
                margin_top="8em",
                margin_bottom="2em",
                max_width="1920px",
            )
        ),
        
        # Versión móvil
        rx.mobile_only(
            rx.vstack(
                # Header móvil
                mobile_header(),
                
                # Contenido principal móvil
                rx.vstack(
                    rx.text(
                        "Reportes de Ingresos",
                        font_size="1.5rem",
                        font_weight="bold",
                        margin_bottom="1rem",
                        text_align="center"
                    ),
                    
                    # Resumen de ingresos móvil - Grid 2x2
                    rx.grid(
                        rx.box(
                            rx.vstack(
                                rx.text("Ingresos totales", font_size="0.8rem", text_align="center"),
                                rx.scroll_area(
                                    rx.text("$312,450.75", font_size="1.3rem", font_weight="bold", color="green", text_align="left", margin_bottom="0.25em"),
                                ),
                                spacing="0",
                            ),
                            bg=rx.color_mode_cond(
                                light=Custom_theme().light_colors()["tertiary"],
                                dark=Custom_theme().dark_colors()["tertiary"]
                            ),
                            border_radius="32px",
                            overflow="hidden",
                            padding="1em",
                            width="100%"
                        ),
                        rx.box(
                            rx.vstack(
                                rx.text("Billetera", font_size="0.8rem", text_align="center"),
                                rx.scroll_area(
                                    rx.text("$3,567.50", font_size="1.3rem", font_weight="bold", color="blue", text_align="left", margin_bottom="0.25em"),
                                ),
                                spacing="0"
                            ),
                            bg=rx.color_mode_cond(
                                light=Custom_theme().light_colors()["tertiary"],
                                dark=Custom_theme().dark_colors()["tertiary"]
                            ),
                            border_radius="32px",
                            overflow="hidden",
                            padding="1rem",
                            width="100%"
                        ),
                        rx.box(
                            rx.vstack(
                                rx.text("Ganancias Uninivel", font_size="0.8rem", text_align="center"),
                                rx.scroll_area(
                                    rx.text("$7,890.00", font_size="1.3rem", font_weight="bold", color="orange", text_align="left", margin_bottom="0.25em"),
                                ),
                                spacing="0"
                            ),
                            bg=rx.color_mode_cond(
                                light=Custom_theme().light_colors()["tertiary"],
                                dark=Custom_theme().dark_colors()["tertiary"]
                            ),
                            border_radius="32px",
                            padding="1rem",
                            width="100%"
                        ),
                        rx.box(
                            rx.vstack(
                                rx.text("Ganancias Matching", font_size="0.8rem", text_align="center"),
                                rx.scroll_area(
                                    rx.text("$1,890.25", font_size="1.3rem", font_weight="bold", color="purple", text_align="left", margin_bottom="0.25em"),
                                ),
                                spacing="0",
                            ),
                            bg=rx.color_mode_cond(
                                light=Custom_theme().light_colors()["tertiary"],
                                dark=Custom_theme().dark_colors()["tertiary"]
                            ),
                            border_radius="32px",
                            padding="1rem",
                            width="100%"
                        ),
                        columns="2",
                        spacing="3",
                        width="100%",
                        margin_bottom="2rem"
                    ),
                    
                    # Historial simplificado para móvil
                    rx.box(
                        rx.vstack(
                            rx.text("Historial de ingresos", font_weight="bold", font_size="1.2rem", margin_bottom="1rem"),
                            
                            # Tarjetas de historial
                            *[rx.box(
                                rx.vstack(
                                    rx.hstack(
                                        rx.text(mes, font_weight="bold", font_size="1rem"),
                                        rx.badge(estado, color_scheme="green" if estado == "Pagado" else "orange", size="1"),
                                        justify="between",
                                        width="100%"
                                    ),
                                    rx.divider(margin_y="0.5rem"),
                                    rx.grid(
                                        rx.vstack(
                                            rx.text("Ventas", font_size="0.75rem", color=rx.color("gray", 9)),
                                            rx.text(ventas, font_weight="600", font_size="0.9rem")
                                        ),
                                        rx.vstack(
                                            rx.text("Comisiones", font_size="0.75rem", color=rx.color("gray", 9)),
                                            rx.text(comisiones, font_weight="600", font_size="0.9rem")
                                        ),
                                        rx.vstack(
                                            rx.text("Bonos", font_size="0.75rem", color=rx.color("gray", 9)),
                                            rx.text(bonos, font_weight="600", font_size="0.9rem")
                                        ),
                                        rx.vstack(
                                            rx.text("Total", font_size="0.75rem", color=rx.color("gray", 9)),
                                            rx.text(total, font_weight="bold", font_size="0.9rem", color="green")
                                        ),
                                        columns="2",
                                        spacing="2",
                                        width="100%"
                                    ),
                                    spacing="2",
                                    width="100%"
                                ),
                                bg=rx.color_mode_cond(
                                    light=rx.color("gray", 2),
                                    dark=rx.color("gray", 12)
                                ),
                                padding="12px",
                                border_radius="8px",
                                width="100%",
                                margin_bottom="0.5rem"
                            ) for mes, ventas, comisiones, bonos, total, estado in [
                                ("Enero 2024", "$4,500.00", "$1,200.50", "$780.25", "$6,480.75", "Pagado"),
                                ("Febrero 2024", "$5,800.00", "$1,450.00", "$950.50", "$8,200.50", "Pagado"),
                                ("Marzo 2024", "$5,200.00", "$1,580.25", "$920.75", "$7,701.00", "Pendiente")
                            ]],
                            
                            spacing="3",
                            width="100%"
                        ),
                        bg=rx.color_mode_cond(
                            light=Custom_theme().light_colors()["tertiary"],
                            dark=Custom_theme().dark_colors()["tertiary"]
                        ),
                        border_radius="16px",
                        padding="1rem",
                        width="100%"
                    ),
                    spacing="4",
                    width="100%",
                    padding="1rem",
                    margin_top="80px"
                ),
            ),
            width="100%",
        ),
        bg=rx.color_mode_cond(
            light=Custom_theme().light_colors()["background"],
            dark=Custom_theme().dark_colors()["background"]
        ),
        position="absolute",
        width="100%",
    )