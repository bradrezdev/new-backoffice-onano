"""Nueva Backoffice NN Protect | Solicitud de retiro"""

import reflex as rx
from ....components.shared_ui.theme import Custom_theme
from rxconfig import config
from ....components.shared_ui.layout import main_container_derecha, mobile_header, desktop_sidebar, mobile_sidebar, header

def new_withdrawal() -> rx.Component:
    # Welcome Page (Index)
    return rx.center(
        rx.desktop_only(
            rx.vstack(
                header(),  # Muestra el usuario logueado en la esquina superior derecha
                rx.hstack(
                    desktop_sidebar(),
                    # Container de la derecha. Contiene el formulario de registro.
                    main_container_derecha(
                        rx.vstack(
                            # Encabezado de la página con navegación
                            rx.hstack(
                                rx.hstack(
                                    rx.text("Backoffice", size="2", color="gray"),
                                    rx.text("/", size="2", color="gray"),
                                    rx.text("Solicitud de retiro", size="2", weight="medium"),
                                    spacing="2"
                                ),
                                justify="start",
                                width="100%",
                                margin_bottom="1em"
                            ),
                            
                            rx.hstack(
                                rx.text(
                                    "💰",
                                    font_size="2rem",
                                ),
                                rx.text(
                                    "Solicitud de retiro",
                                    font_size="2rem",
                                    font_weight="bold",
                                ),
                                align="center",
                                spacing="3",
                                margin_bottom="0.5em"
                            ),
                            
                            rx.text(
                                "Complete el formulario para solicitar un retiro de sus ganancias",
                                font_size="1rem",
                                color="gray",
                                margin_bottom="2em"
                            ),
                            
                            # Contenedor principal con dos columnas
                            rx.hstack(
                                # Columna izquierda - Formulario
                                rx.box(
                                    rx.vstack(
                                        # Información de saldo disponible
                                        rx.box(
                                            rx.vstack(
                                                rx.hstack(
                                                    rx.icon("wallet", size=20, color=Custom_theme().light_colors()["primary"]),
                                                    rx.text("Saldo disponible", font_size="0.9rem", color="gray"),
                                                    align="center",
                                                    spacing="2"
                                                ),
                                                rx.text(
                                                    "$2,450.00 USD",
                                                    font_size="1.5rem",
                                                    font_weight="bold",
                                                    color=Custom_theme().light_colors()["primary"]
                                                ),
                                                spacing="1",
                                                align="start"
                                            ),
                                            bg=rx.color_mode_cond(
                                                light="rgba(59, 130, 246, 0.05)",
                                                dark="rgba(59, 130, 246, 0.1)"
                                            ),
                                            border=f"1px solid rgba(59, 130, 246, 0.2)",
                                            border_radius="12px",
                                            padding="16px",
                                            margin_bottom="1.5em",
                                            width="100%"
                                        ),
                                        
                                        # Monto a retirar
                                        rx.vstack(
                                            rx.hstack(
                                                rx.icon("dollar-sign", size=16, color=Custom_theme().light_colors()["primary"]),
                                                rx.text("Monto a retirar *", font_size="1rem", font_weight="semibold"),
                                                align="center",
                                                spacing="2"
                                            ),
                                            rx.input(
                                                placeholder="0.00",
                                                type="number",
                                                min="10",
                                                max="2450",
                                                step="0.01",
                                                padding="16px",
                                                border_radius="12px",
                                                border=f"1px solid {Custom_theme().light_colors()['border']}",
                                                _focus={
                                                    "border": f"2px solid {Custom_theme().light_colors()['primary']}",
                                                    "box_shadow": f"0 0 0 3px rgba(59, 130, 246, 0.1)"
                                                },
                                                _hover={
                                                    "border": f"1px solid {Custom_theme().light_colors()['primary']}"
                                                },
                                                font_size="1.1rem",
                                                height="50px"
                                            ),
                                            rx.hstack(
                                                rx.text("Mínimo: $10.00", font_size="0.8rem", color="gray"),
                                                rx.spacer(),
                                                rx.text("Máximo: $2,450.00", font_size="0.8rem", color="gray"),
                                                width="100%"
                                            ),
                                            width="100%",
                                            margin_bottom="1.5em",
                                            spacing="2"
                                        ),
                                        
                                        # Método de retiro
                                        rx.vstack(
                                            rx.hstack(
                                                rx.icon("credit-card", size=16, color=Custom_theme().light_colors()["primary"]),
                                                rx.text("Método de retiro *", font_size="1rem", font_weight="semibold"),
                                                align="center",
                                                spacing="2"
                                            ),
                                            rx.select(
                                                ["🏦 Cuenta bancaria - Banco Santander ****1234", 
                                                 "🏦 Cuenta bancaria - BBVA ****5678", 
                                                 "💳 PayPal - usuario@email.com",
                                                 "🪙 Cuenta crypto - Bitcoin",
                                                 "➕ Agregar nuevo método"],
                                                placeholder="Seleccione un método de retiro",
                                                size="3",
                                                padding="16px",
                                                border_radius="12px",
                                                border=f"1px solid {Custom_theme().light_colors()['border']}",
                                                _focus={
                                                    "border": f"2px solid {Custom_theme().light_colors()['primary']}"
                                                },
                                                height="50px"
                                            ),
                                            width="100%",
                                            margin_bottom="1.5em",
                                            spacing="2"
                                        ),
                                        
                                        # Concepto/Nota opcional
                                        rx.vstack(
                                            rx.hstack(
                                                rx.icon("message-circle", size=16, color=Custom_theme().light_colors()["primary"]),
                                                rx.text("Concepto/Nota (opcional)", font_size="1rem", font_weight="semibold"),
                                                align="center",
                                                spacing="2"
                                            ),
                                            rx.text_area(
                                                placeholder="Agregue una nota o concepto para este retiro...",
                                                padding="16px",
                                                border_radius="12px",
                                                border=f"1px solid {Custom_theme().light_colors()['border']}",
                                                _focus={
                                                    "border": f"2px solid {Custom_theme().light_colors()['primary']}",
                                                    "box_shadow": f"0 0 0 3px rgba(59, 130, 246, 0.1)"
                                                },
                                                min_height="80px",
                                                resize="vertical"
                                            ),
                                            width="100%",
                                            margin_bottom="2em",
                                            spacing="2"
                                        ),
                                        
                                        # Botones de acción
                                        rx.hstack(
                                            rx.button(
                                                rx.icon("x", size=16),
                                                "Cancelar",
                                                variant="outline",
                                                size="3",
                                                border_radius="12px",
                                                padding="16px 24px",
                                                flex="1",
                                                _hover={"opacity": 0.8}
                                            ),
                                            rx.button(
                                                rx.icon("send", size=16),
                                                "Enviar solicitud",
                                                bg=Custom_theme().light_colors()["primary"],
                                                color="white",
                                                size="3",
                                                border_radius="12px",
                                                padding="16px 24px",
                                                _hover={"opacity": 0.9, "transform": "translateY(-1px)"},
                                                flex="2",
                                                transition="all 0.2s ease"
                                            ),
                                            spacing="3",
                                            width="100%"
                                        )
                                    ),
                                    bg=rx.color_mode_cond(
                                        light=Custom_theme().light_colors()["tertiary"],
                                        dark=Custom_theme().dark_colors()["tertiary"]
                                    ),
                                    border_radius="24px",
                                    padding="32px",
                                    box_shadow="0 4px 6px rgba(0, 0, 0, 0.05)",
                                    flex="2"
                                ),
                                
                                # Columna derecha - Información y consejos
                                rx.vstack(
                                    # Información importante
                                    rx.box(
                                        rx.vstack(
                                            rx.hstack(
                                                rx.icon("info", size=18, color="#2563eb"),
                                                rx.text("Información importante", font_weight="semibold", font_size="1rem"),
                                                align="center",
                                                spacing="2"
                                            ),
                                            rx.vstack(
                                                rx.text("⏱️ Tiempo de procesamiento: 1-3 días hábiles", font_size="0.9rem", color="gray"),
                                                rx.text("💵 Comisión: 2% del monto retirado", font_size="0.9rem", color="gray"),
                                                rx.text("🕐 Horario: Lunes a viernes 9:00 AM - 6:00 PM", font_size="0.9rem", color="gray"),
                                                rx.text("📧 Recibirá confirmación por email", font_size="0.9rem", color="gray"),
                                                spacing="2",
                                                align="start"
                                            ),
                                            spacing="3",
                                            align="start"
                                        ),
                                        bg="rgba(37, 99, 235, 0.05)",
                                        border="1px solid rgba(37, 99, 235, 0.2)",
                                        border_radius="16px",
                                        padding="20px",
                                        margin_bottom="1em"
                                    ),
                                    
                                    # Historial de retiros recientes
                                    rx.box(
                                        rx.vstack(
                                            rx.hstack(
                                                rx.icon("history", size=18, color="#059669"),
                                                rx.text("Retiros recientes", font_weight="semibold", font_size="1rem"),
                                                align="center",
                                                spacing="2"
                                            ),
                                            rx.vstack(
                                                rx.hstack(
                                                    rx.text("$500.00", font_weight="medium", font_size="0.9rem"),
                                                    rx.spacer(),
                                                    rx.badge("Completado", color_scheme="green", size="1"),
                                                    width="100%"
                                                ),
                                                rx.text("15 Sep 2024 - Banco Santander", font_size="0.8rem", color="gray"),
                                                
                                                rx.hstack(
                                                    rx.text("$750.00", font_weight="medium", font_size="0.9rem"),
                                                    rx.spacer(),
                                                    rx.badge("Procesando", color_scheme="blue", size="1"),
                                                    width="100%"
                                                ),
                                                rx.text("10 Sep 2024 - PayPal", font_size="0.8rem", color="gray"),
                                                
                                                rx.hstack(
                                                    rx.text("$300.00", font_weight="medium", font_size="0.9rem"),
                                                    rx.spacer(),
                                                    rx.badge("Completado", color_scheme="green", size="1"),
                                                    width="100%"
                                                ),
                                                rx.text("05 Sep 2024 - BBVA", font_size="0.8rem", color="gray"),
                                                
                                                spacing="2",
                                                align="start",
                                                width="100%"
                                            ),
                                            spacing="3",
                                            align="start"
                                        ),
                                        bg="rgba(5, 150, 105, 0.05)",
                                        border="1px solid rgba(5, 150, 105, 0.2)",
                                        border_radius="16px",
                                        padding="20px",
                                        margin_bottom="1em"
                                    ),
                                    
                                    # Soporte
                                    rx.box(
                                        rx.vstack(
                                            rx.hstack(
                                                rx.icon("circle_help", size=18, color="#dc2626"),
                                                rx.text("¿Necesita ayuda?", font_weight="semibold", font_size="1rem"),
                                                align="center",
                                                spacing="2"
                                            ),
                                            rx.text("Si tiene dudas sobre su retiro, contacte a nuestro equipo de soporte.", font_size="0.9rem", color="gray"),
                                            rx.button(
                                                rx.icon("message-square", size=16),
                                                "Contactar soporte",
                                                variant="outline",
                                                size="2",
                                                border_radius="8px",
                                                width="100%",
                                                _hover={"bg": "rgba(220, 38, 38, 0.05)"}
                                            ),
                                            spacing="2",
                                            align="start"
                                        ),
                                        bg="rgba(220, 38, 38, 0.05)",
                                        border="1px solid rgba(220, 38, 38, 0.2)",
                                        border_radius="16px",
                                        padding="20px"
                                    ),
                                    
                                    width="300px",
                                    spacing="0"
                                ),
                                
                                spacing="6",
                                align="start",
                                width="100%"
                            ),
                            
                            # Propiedades del contenedor del formulario
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
                    
                    # Título con emoji
                    rx.hstack(
                        rx.text("💰", font_size="1.5rem"),
                        rx.text(
                            "Solicitud de retiro",
                            font_size="1.5rem",
                            font_weight="bold",
                        ),
                        align="center",
                        spacing="2",
                        margin_bottom="0.5em",
                        margin_top="0.5em",
                    ),
                    
                    rx.text(
                        "Complete el formulario para solicitar un retiro",
                        font_size="0.9rem",
                        color="gray",
                        margin_bottom="1.5em",
                        text_align="center"
                    ),
                    
                    # Formulario móvil
                    rx.box(
                        rx.vstack(
                            # Saldo disponible (móvil)
                            rx.box(
                                rx.vstack(
                                    rx.hstack(
                                        rx.icon("wallet", size=16, color=Custom_theme().light_colors()["primary"]),
                                        rx.text("Saldo disponible", font_size="0.8rem", color="gray"),
                                        align="center",
                                        spacing="2"
                                    ),
                                    rx.text(
                                        "$2,450.00 USD",
                                        font_size="1.3rem",
                                        font_weight="bold",
                                        color=Custom_theme().light_colors()["primary"]
                                    ),
                                    spacing="1",
                                    align="center"
                                ),
                                bg=rx.color_mode_cond(
                                    light="rgba(59, 130, 246, 0.05)",
                                    dark="rgba(59, 130, 246, 0.1)"
                                ),
                                border=f"1px solid rgba(59, 130, 246, 0.2)",
                                border_radius="12px",
                                padding="16px",
                                margin_bottom="1.5em",
                                width="100%"
                            ),
                            
                            # Monto a retirar (móvil)
                            rx.vstack(
                                rx.hstack(
                                    rx.icon("dollar-sign", size=14, color=Custom_theme().light_colors()["primary"]),
                                    rx.text("Monto a retirar *", font_size="0.9rem", font_weight="semibold"),
                                    align="center",
                                    spacing="2"
                                ),
                                rx.input(
                                    placeholder="0.00",
                                    type="number",
                                    min="10",
                                    max="2450",
                                    step="0.01",
                                    padding="14px",
                                    border_radius="10px",
                                    border=f"1px solid {Custom_theme().light_colors()['border']}",
                                    _focus={
                                        "border": f"2px solid {Custom_theme().light_colors()['primary']}",
                                        "box_shadow": f"0 0 0 2px rgba(59, 130, 246, 0.1)"
                                    },
                                    font_size="1rem",
                                    height="48px"
                                ),
                                rx.hstack(
                                    rx.text("Min: $10", font_size="0.7rem", color="gray"),
                                    rx.spacer(),
                                    rx.text("Max: $2,450", font_size="0.7rem", color="gray"),
                                    width="100%"
                                ),
                                width="100%",
                                margin_bottom="1.5em",
                                spacing="2"
                            ),
                            
                            # Método de retiro (móvil)
                            rx.vstack(
                                rx.hstack(
                                    rx.icon("credit-card", size=14, color=Custom_theme().light_colors()["primary"]),
                                    rx.text("Método de retiro *", font_size="0.9rem", font_weight="semibold"),
                                    align="center",
                                    spacing="2"
                                ),
                                rx.select(
                                    ["🏦 Banco Santander ****1234", 
                                     "🏦 BBVA ****5678", 
                                     "💳 PayPal",
                                     "🪙 Bitcoin",
                                     "➕ Agregar nuevo"],
                                    placeholder="Seleccione método",
                                    size="2",
                                    padding="14px",
                                    border_radius="10px",
                                    border=f"1px solid {Custom_theme().light_colors()['border']}",
                                    height="48px"
                                ),
                                width="100%",
                                margin_bottom="1.5em",
                                spacing="2"
                            ),
                            
                            # Concepto/Nota (móvil)
                            rx.vstack(
                                rx.hstack(
                                    rx.icon("message-circle", size=14, color=Custom_theme().light_colors()["primary"]),
                                    rx.text("Concepto (opcional)", font_size="0.9rem", font_weight="semibold"),
                                    align="center",
                                    spacing="2"
                                ),
                                rx.text_area(
                                    placeholder="Nota opcional...",
                                    padding="14px",
                                    border_radius="10px",
                                    border=f"1px solid {Custom_theme().light_colors()['border']}",
                                    _focus={
                                        "border": f"2px solid {Custom_theme().light_colors()['primary']}"
                                    },
                                    min_height="60px",
                                    resize="vertical"
                                ),
                                width="100%",
                                margin_bottom="2em",
                                spacing="2"
                            ),
                            
                            # Información importante (móvil)
                            rx.box(
                                rx.vstack(
                                    rx.hstack(
                                        rx.icon("info", size=16, color="#2563eb"),
                                        rx.text("Información", font_weight="semibold", font_size="0.9rem"),
                                        align="center",
                                        spacing="2"
                                    ),
                                    rx.vstack(
                                        rx.text("⏱️ Procesamiento: 1-3 días", font_size="0.8rem", color="gray"),
                                        rx.text("💵 Comisión: 2%", font_size="0.8rem", color="gray"),
                                        rx.text("📧 Confirmación por email", font_size="0.8rem", color="gray"),
                                        spacing="1",
                                        align="start"
                                    ),
                                    spacing="2",
                                    align="start"
                                ),
                                bg="rgba(37, 99, 235, 0.05)",
                                border="1px solid rgba(37, 99, 235, 0.2)",
                                border_radius="12px",
                                padding="16px",
                                width="100%"
                            ),
                        ),
                        bg=rx.color_mode_cond(
                            light=Custom_theme().light_colors()["tertiary"],
                            dark=Custom_theme().dark_colors()["tertiary"]
                        ),
                        border_radius="20px",
                        padding="16px",
                        box_shadow="0 2px 4px rgba(0, 0, 0, 0.05)",
                        width="100%",
                        margin_bottom="1em"
                    ),
                    
                    rx.vstack(
                        rx.button(
                            rx.icon("send", size=16),
                            "Enviar solicitud",
                            bg=Custom_theme().light_colors()["primary"],
                            color="white",
                            size="3",
                            border_radius="12px",
                            padding="16px",
                            _hover={"opacity": 0.9},
                            width="100%"
                        ),
                        rx.button(
                            "Cancelar",
                            variant="outline",
                            size="2",
                            border_radius="10px",
                            padding="12px",
                            width="100%",
                            _hover={"opacity": 0.8}
                        ),
                        spacing="2",
                        width="100%"
                    ),

                    # Propiedades del vstack principal móvil
                    width="100%",
                    padding="16px",
                ),
            ),
            width="100%",
        ),
        width="100%",
        bg=rx.color_mode_cond(
            light=Custom_theme().light_colors()["background"],
            dark=Custom_theme().dark_colors()["background"],
        ),
    )