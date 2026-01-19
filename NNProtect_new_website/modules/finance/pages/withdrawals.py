"""Nueva Backoffice NN Protect | Retiros"""

import reflex as rx
from ....components.shared_ui.theme import Custom_theme
from rxconfig import config
from ....components.shared_ui.layout import main_container_derecha, mobile_header, desktop_sidebar, mobile_sidebar, header
from ..state.finance_state import FinanceState

def withdrawals() -> rx.Component:
    # Datos obtenidos del estado
    
    return rx.center(
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
                            
                            # Encabezado de la página
                            rx.hstack(
                                rx.text("💰", font_size="2rem"),
                                rx.text(
                                    "Historial de retiros",
                                    font_size="2rem",
                                    font_weight="bold",
                                ),
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

                            # Barra de herramientas superior
                            rx.hstack(
                                # Buscador por número de retiro
                                rx.hstack(
                                    rx.icon("search", size=18, color=Custom_theme().light_colors()["primary"]),
                                    rx.input(
                                        placeholder="Buscar por # de retiro (ej: WD001)",
                                        padding="12px 16px",
                                        border_radius="12px",
                                        border=f"1px solid {Custom_theme().light_colors()['border']}",
                                        _focus={
                                            "border": f"2px solid {Custom_theme().light_colors()['primary']}",
                                            "box_shadow": f"0 0 0 3px rgba(59, 130, 246, 0.1)"
                                        },
                                        _hover={
                                            "border": f"1px solid {Custom_theme().light_colors()['primary']}"
                                        },
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
                                
                                # Botón para nuevo retiro
                                rx.button(
                                    rx.icon("plus", size=16),
                                    "Nuevo retiro",
                                    bg=Custom_theme().light_colors()["primary"],
                                    color="white",
                                    size="3",
                                    border_radius="12px",
                                    padding="12px 20px",
                                    _hover={"opacity": 0.9, "transform": "translateY(-1px)"},
                                    transition="all 0.2s ease"
                                ),
                                
                                width="100%",
                                margin_bottom="1.5em"
                            ),

                            # Estadísticas rápidas
                            rx.hstack(
                                # Total retirado
                                rx.box(
                                    rx.vstack(
                                        rx.hstack(
                                            rx.icon("trending-up", size=16, color="#059669"),
                                            rx.text("Total retirado", font_size="0.9rem", color="gray"),
                                            align="center",
                                            spacing="2"
                                        ),
                                        rx.text("$5,650.00", font_size="1.5rem", font_weight="bold", color="#059669"),
                                        spacing="1",
                                        align="start"
                                    ),
                                    bg="rgba(5, 150, 105, 0.05)",
                                    border="1px solid rgba(5, 150, 105, 0.2)",
                                    border_radius="12px",
                                    padding="16px",
                                    flex="1"
                                ),
                                
                                # Retiros completados
                                rx.box(
                                    rx.vstack(
                                        rx.hstack(
                                            rx.icon("check-check", size=16, color="#2563eb"),
                                            rx.text("Completados", font_size="0.9rem", color="gray"),
                                            align="center",
                                            spacing="2"
                                        ),
                                        rx.text("7", font_size="1.5rem", font_weight="bold", color="#2563eb"),
                                        spacing="1",
                                        align="start"
                                    ),
                                    bg="rgba(37, 99, 235, 0.05)",
                                    border="1px solid rgba(37, 99, 235, 0.2)",
                                    border_radius="12px",
                                    padding="16px",
                                    flex="1"
                                ),
                                
                                # En proceso
                                rx.box(
                                    rx.vstack(
                                        rx.hstack(
                                            rx.icon("clock", size=16, color="#f59e0b"),
                                            rx.text("En proceso", font_size="0.9rem", color="gray"),
                                            align="center",
                                            spacing="2"
                                        ),
                                        rx.text("2", font_size="1.5rem", font_weight="bold", color="#f59e0b"),
                                        spacing="1",
                                        align="start"
                                    ),
                                    bg="rgba(245, 158, 11, 0.05)",
                                    border="1px solid rgba(245, 158, 11, 0.2)",
                                    border_radius="12px",
                                    padding="16px",
                                    flex="1"
                                ),
                                
                                # Rechazados
                                rx.box(
                                    rx.vstack(
                                        rx.hstack(
                                            rx.icon("x", size=16, color="#dc2626"),
                                            rx.text("Rechazados", font_size="0.9rem", color="gray"),
                                            align="center",
                                            spacing="2"
                                        ),
                                        rx.text("1", font_size="1.5rem", font_weight="bold", color="#dc2626"),
                                        spacing="1",
                                        align="start"
                                    ),
                                    bg="rgba(220, 38, 38, 0.05)",
                                    border="1px solid rgba(220, 38, 38, 0.2)",
                                    border_radius="12px",
                                    padding="16px",
                                    flex="1"
                                ),
                                
                                spacing="4",
                                width="100%",
                                margin_bottom="2em"
                            ),

                            # Tabla de retiros
                            rx.box(
                                rx.vstack(
                                    # Encabezado de la tabla
                                    rx.hstack(
                                        rx.text("# Retiro", font_weight="semibold", font_size="0.9rem", color="gray", width="120px"),
                                        rx.text("Método", font_weight="semibold", font_size="0.9rem", color="gray", width="250px"),
                                        rx.text("Monto", font_weight="semibold", font_size="0.9rem", color="gray", width="120px"),
                                        rx.text("Fecha", font_weight="semibold", font_size="0.9rem", color="gray", width="120px"),
                                        rx.text("Estado", font_weight="semibold", font_size="0.9rem", color="gray", width="120px"),
                                        rx.text("Acciones", font_weight="semibold", font_size="0.9rem", color="gray", width="100px"),
                                        padding="16px 20px",
                                        border_bottom=f"1px solid {Custom_theme().light_colors()['border']}",
                                        width="100%"
                                    ),
                                    
                                    # Filas de la tabla
                                    rx.foreach(
                                        withdrawals_data,
                                        lambda withdrawal: rx.hstack(
                                            # Número de retiro
                                            rx.text(
                                                withdrawal["id"], 
                                                font_weight="medium", 
                                                font_size="0.9rem",
                                                width="120px"
                                            ),
                                            
                                            # Método de retiro
                                            rx.text(
                                                withdrawal["method"], 
                                                font_size="0.9rem",
                                                width="250px"
                                            ),
                                            
                                            # Monto
                                        FinanceState.withdrawals_list
                                                f"${withdrawal['amount']:.2f}", 
                                                font_weight="medium", 
                                                font_size="0.9rem",
                                                color="#059669",
                                                width="120px"
                                            ),
                                            
                                            # Fecha
                                            rx.text(
                                                withdrawal["date"], 
                                                font_size="0.9rem",
                                                color="gray",
                                                width="120px"
                                            ),
                                            
                                            # Estado
                                            rx.cond(
                                                withdrawal["status"] == "Completado",
                                                rx.badge("Completado", color_scheme="green", size="1"),
                                                rx.cond(
                                                    withdrawal["status"] == "Procesando",
                                                    rx.badge("Procesando", color_scheme="blue", size="1"),
                                                    rx.badge("Rechazado", color_scheme="red", size="1")
                                                )
                                            ),
                                            
                                            # Acciones
                                            rx.hstack(
                                                rx.button(
                                                    rx.icon("eye", size=14),
                                                    variant="ghost",
                                                    size="1",
                                                    padding="6px",
                                                    border_radius="6px",
                                                    _hover={"bg": "rgba(59, 130, 246, 0.1)"}
                                                ),
                                                rx.button(
                                                    rx.icon("download", size=14),
                                                    variant="ghost",
                                                    size="1",
                                                    padding="6px",
                                                    border_radius="6px",
                                                    _hover={"bg": "rgba(5, 150, 105, 0.1)"}
                                                ),
                                                spacing="1",
                                                width="100px"
                                            ),
                                            
                                            padding="16px 20px",
                                            border_bottom=f"1px solid rgba(0, 0, 0, 0.05)",
                                            width="100%",
                                            _hover={"bg": "rgba(0, 0, 0, 0.02)"},
                                            transition="background-color 0.2s ease"
                                        )
                                    ),
                                    
                                    spacing="0",
                                    width="100%"
                                ),
                                
                                bg=rx.color_mode_cond(
                                    light=Custom_theme().light_colors()["tertiary"],
                                    dark=Custom_theme().dark_colors()["tertiary"]
                                ),
                                border_radius="16px",
                                overflow="hidden",
                                box_shadow="0 4px 6px rgba(0, 0, 0, 0.05)",
                                width="100%",
                                margin_bottom="2em"
                            ),

                            # Paginación
                            rx.hstack(
                                rx.text("Mostrando 1-10 de 10 retiros", font_size="0.9rem", color="gray"),
                                rx.spacer(),
                                rx.hstack(
                                    rx.button(
                                        rx.icon("chevron-left", size=16),
                                        variant="outline",
                                        size="2",
                                        disabled=True,
                                        border_radius="8px"
                                    ),
                                    rx.text("1", font_size="0.9rem", color="gray"),
                                    rx.button(
                                        rx.icon("chevron-right", size=16),
                                        variant="outline",
                                        size="2",
                                        disabled=True,
                                        border_radius="8px"
                                    ),
                                    spacing="2"
                                ),
                                width="100%"
                            ),
                            
                            # Propiedades del contenedor principal
                            width="100%",
                        ),
                    )
                ),
                # Propiedades vstack que contiene el contenido de la página.
                justify="center",
                margin_top="120px",
                margin_bottom="0.2em",
                max_width="1440px",
            )
        ),
        
        # Versión móvil
        rx.mobile_only(
            rx.vstack(
                # Header móvil
                mobile_header(),
                
                # Contenido principal móvil
                rx.vstack(
                    # Navegación móvil
                    rx.hstack(
                        rx.text("Backoffice", size="1", color="gray"),
                        rx.text("/", size="1", color="gray"),
                        rx.text("Retiros", size="1", weight="medium"),
                        spacing="1",
                        margin_bottom="1em"
                    ),
                    
                    # Título móvil
                    rx.hstack(
                        rx.text("💰", font_size="1.5rem"),
                        rx.text(
                            "Retiros",
                            font_size="1.5rem",
                            font_weight="bold",
                        ),
                        align="center",
                        spacing="2",
                        margin_bottom="0.5em",
                        margin_top="0.5em",
                    ),
                    
                    # Buscador móvil
                    rx.hstack(
                        rx.icon("search", size=16, color=Custom_theme().light_colors()["primary"]),
                        rx.input(
                            placeholder="Buscar # retiro",
                            padding="12px",
                            border_radius="10px",
                            border=f"1px solid {Custom_theme().light_colors()['border']}",
                            _focus={
                                "border": f"2px solid {Custom_theme().light_colors()['primary']}"
                            },
                            flex="1"
                        ),
                        spacing="2",
                        bg="white",
                        padding="8px 12px",
                        border_radius="10px",
                        border=f"1px solid {Custom_theme().light_colors()['border']}",
                        margin_bottom="1.5em",
                        width="100%"
                    ),
                    
                    # Estadísticas móviles (en grid 2x2)
                    rx.vstack(
                        rx.hstack(
                            # Total y completados
                            rx.box(
                                rx.vstack(
                                    rx.text("💰", font_size="1.2rem"),
                                    rx.text("$5,650", font_size="1.1rem", font_weight="bold", color="#059669"),
                                    rx.text("Total", font_size="0.8rem", color="gray"),
                                    spacing="1",
                                    align="center"
                                ),
                                bg="rgba(5, 150, 105, 0.05)",
                                border="1px solid rgba(5, 150, 105, 0.2)",
                                border_radius="10px",
                                padding="12px",
                                flex="1"
                            ),
                            rx.box(
                                rx.vstack(
                                    rx.text("✅", font_size="1.2rem"),
                                    rx.text("7", font_size="1.1rem", font_weight="bold", color="#2563eb"),
                                    rx.text("Completados", font_size="0.8rem", color="gray"),
                                    spacing="1",
                                    align="center"
                                ),
                                bg="rgba(37, 99, 235, 0.05)",
                                border="1px solid rgba(37, 99, 235, 0.2)",
                                border_radius="10px",
                                padding="12px",
                                flex="1"
                            ),
                            spacing="3",
                            width="100%"
                        ),
                        rx.hstack(
                            # En proceso y rechazados
                            rx.box(
                                rx.vstack(
                                    rx.text("⏳", font_size="1.2rem"),
                                    rx.text("2", font_size="1.1rem", font_weight="bold", color="#f59e0b"),
                                    rx.text("Proceso", font_size="0.8rem", color="gray"),
                                    spacing="1",
                                    align="center"
                                ),
                                bg="rgba(245, 158, 11, 0.05)",
                                border="1px solid rgba(245, 158, 11, 0.2)",
                                border_radius="10px",
                                padding="12px",
                                flex="1"
                            ),
                            rx.box(
                                rx.vstack(
                                    rx.text("❌", font_size="1.2rem"),
                                    rx.text("1", font_size="1.1rem", font_weight="bold", color="#dc2626"),
                                    rx.text("Rechazados", font_size="0.8rem", color="gray"),
                                    spacing="1",
                                    align="center"
                                ),
                                bg="rgba(220, 38, 38, 0.05)",
                                border="1px solid rgba(220, 38, 38, 0.2)",
                                border_radius="10px",
                                padding="12px",
                                flex="1"
                            ),
                            spacing="3",
                            width="100%"
                        ),
                        spacing="2",
                        margin_bottom="1em",
                        width="100%"
                    ),

                    # Botón nuevo retiro móvil
                    rx.link(
                        rx.button(
                            rx.icon("plus", size=16),
                            "Nuevo retiro",
                            bg=Custom_theme().light_colors()["primary"],
                            color="white",
                            size="3",
                            border_radius="12px",
                            padding="16px",
                            width="100%",
                            margin_bottom="1em",
                            _hover={"opacity": 0.9}
                        ),
                        href="/new_withdrawal",
                        width="100%",
                    ),
                    
                    # Lista de retiros móvil (cards en lugar de tabla)
                    rx.vstack(
                        rx.foreach(
                            withdrawals_data,
                            lambda withdrawal: rx.box(
                                rx.vstack(
                                    # Fila superior: ID y estado
                                    rx.hstack(
                                        rx.text(withdrawal["id"], font_weight="bold", font_size="0.9rem"),
                                        rx.spacer(),
                                        rx.cond(
                                            withdrawal["status"] == "Completado",
                                            rx.badge("✅ Completado", color_scheme="green", size="1"),
                                            rx.cond(
                                                withdrawal["status"] == "Procesando",
                                                rx.badge("⏳ Procesando", color_scheme="blue", size="1"),
                                                rx.badge("❌ Rechazado", color_scheme="red", size="1")
                                            )
                                        ),
                                        width="100%",
                                        align="center"
                                    ),
                                    
                                    # Fila del medio: método y monto
                                    rx.hstack(
                                        rx.vstack(
                                            rx.text("Método:", font_size="0.7rem", color="gray"),
                                            rx.text(withdrawal["method"], font_size="0.8rem"),
                                            spacing="1",
                                            align="start",
                                            flex="2"
                                        ),
                                        rx.vstack(
                                            rx.text("Monto:", font_size="0.7rem", color="gray"),
                                            rx.text(f"${withdrawal['amount']:.2f}", font_size="0.9rem", font_weight="bold", color="#059669"),
                                            spacing="1",
                                            align="end",
                                            flex="1"
                                        ),
                                        width="100%",
                                        align="start"
                                    ),
                                    
                                    # Fila inferior: fecha y acciones
                                    rx.hstack(
                                        rx.text(withdrawal["date"], font_size="0.8rem", color="gray"),
                                        rx.spacer(),
                                        rx.hstack(
                                            rx.button(
                                                rx.icon("eye", size=12),
                                                variant="ghost",
                                                size="1",
                                                padding="4px",
                                                border_radius="6px"
                                            ),
                                            rx.button(
                                                rx.icon("download", size=12),
                                                variant="ghost",
                                                size="1",
                                                padding="4px",
                                                border_radius="6px"
                                            ),
                                            spacing="1"
                                        ),
                                        width="100%",
                                        align="center"
                                    ),
                                    
                                    spacing="2",
                                    align="start",
                                    width="100%"
                                ),
                                bg=rx.color_mode_cond(
                                    light=Custom_theme().light_colors()["tertiary"],
                                    dark=Custom_theme().dark_colors()["tertiary"]
                                ),
                                border_radius="12px",
                                padding="16px",
                                margin_bottom="12px",
                                box_shadow="0 2px 4px rgba(0, 0, 0, 0.05)",
                                width="100%"
                            )
                        ),
                        
                        spacing="0",
                        width="100%",
                        margin_bottom="1em"
                    ),
                    
                    # Propiedades del vstack principal móvil
                    width="100%",
                    padding="16px",
                ),
            ),
            width="100%",
        ),
        width="100vw",
        height="100%",
        bg=rx.color_mode_cond(
            light=Custom_theme().light_colors()["background"],
            dark=Custom_theme().dark_colors()["background"],
        ),
    )