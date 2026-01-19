"""Nueva Backoffice NN Protect | Método de envío"""

import reflex as rx
from rxconfig import config

from ....components.shared_ui.theme import Custom_theme
from ....components.shared_ui.layout import main_container_derecha, mobile_header, desktop_sidebar, header

def shipment_method() -> rx.Component:
    # Datos de ejemplo para domicilios almacenados
    saved_addresses = [
        {
            "id": 1,
            "name": "Casa Principal",
            "address": "Av. Reforma 123, Col. Centro, CDMX",
            "recipient": "Bryan Núñez",
            "phone": "+52 55 1234 5678"
        },
        {
            "id": 2,
            "name": "Oficina",
            "address": "Paseo de la Reforma 456, Piso 15, CDMX",
            "recipient": "Bryan Núñez",
            "phone": "+52 55 8765 4321"
        }
    ]

    # Datos de ejemplo para CEDIS disponibles
    cedis_locations = [
        {
            "id": 1,
            "name": "CEDIS Centro",
            "address": "Calle Principal 789, Col. Industrial, CDMX",
            "schedule": "Lunes a Viernes: 8:00 AM - 6:00 PM",
            "phone": "+52 55 1111 2222"
        },
        {
            "id": 2,
            "name": "CEDIS Norte",
            "address": "Av. Insurgentes 321, Naucalpan, Estado de México",
            "schedule": "Lunes a Sábado: 9:00 AM - 7:00 PM",
            "phone": "+52 55 3333 4444"
        },
        {
            "id": 3,
            "name": "CEDIS Sur",
            "address": "Blvd. Adolfo López Mateos 654, Tlalpan, CDMX",
            "schedule": "Lunes a Viernes: 7:00 AM - 5:00 PM",
            "phone": "+52 55 5555 6666"
        }
    ]

    return rx.center(
        # Versión desktop - dejada en blanco según requerimiento
        rx.desktop_only(),

        # Versión móvil - implementación completa
        rx.mobile_only(
            rx.vstack(
                # Header móvil
                mobile_header(),

                # Contenido principal móvil
                rx.vstack(

                    # Título principal
                    rx.text(
                        "Método de envío",
                        size="8",
                        font_weight="bold",
                    ),

                    rx.text(
                        "Elige cómo quieres recibir tu pedido",
                        size="2",
                        color="gray",
                        margin_bottom="2em",
                        text_align="center"
                    ),

                    # Opciones de envío - Solo RECOLECCIÓN disponible temporalmente
                    rx.vstack(
                        # ❌ Opción 1: Envío a Domicilio - DESHABILITADA TEMPORALMENTE
                        rx.box(
                            rx.vstack(
                                rx.hstack(
                                    rx.icon("truck", size=20, color="gray"),
                                    rx.text("Envío a Domicilio", font_weight="semibold", font_size="1rem", color="gray"),
                                    align="center",
                                    spacing="2"
                                ),
                                rx.text(
                                    "Temporalmente no disponible",
                                    font_size="0.8rem",
                                    color="gray",
                                    margin_top="0.5em",
                                    font_style="italic"
                                ),
                                rx.hstack(
                                    rx.text("No disponible", font_weight="medium", font_size="0.8rem", color="gray"),
                                    spacing="2",
                                    margin_top="0.5em"
                                ),
                                align="start",
                                spacing="1"
                            ),
                            bg="rgba(128, 128, 128, 0.1)",
                            border_radius="29px",
                            padding="20px",
                            border="2px solid rgba(128, 128, 128, 0.2)",
                            opacity="0.6",
                            margin_bottom="1em",
                            width="100%"
                        ),

                        # ✅ Opción 2: Recoger en CEDIS - ÚNICA OPCIÓN DISPONIBLE
                        rx.box(
                            rx.vstack(
                                rx.hstack(
                                    rx.icon("package", size=20, color=Custom_theme().light_colors()["primary"]),
                                    rx.text("Recoger en CEDIS", font_weight="semibold", font_size="1rem"),
                                    rx.badge("DISPONIBLE", color_scheme="green", size="1"),
                                    align="center",
                                    spacing="2"
                                ),
                                rx.text(
                                    "Recoge tu pedido en uno de nuestros centros de distribución",
                                    font_size="0.8rem",
                                    color="gray",
                                    margin_top="0.5em"
                                ),
                                rx.hstack(
                                    rx.text("GRATIS", font_weight="bold", font_size="0.9rem", color="#059669"),
                                    rx.text("• Disponible inmediatamente", font_size="0.8rem", color="gray"),
                                    spacing="2",
                                    margin_top="0.5em"
                                ),
                                align="start",
                                spacing="1"
                            ),
                            bg=rx.color_mode_cond(
                                light=Custom_theme().light_colors()["tertiary"],
                                dark=Custom_theme().dark_colors()["tertiary"]
                            ),
                            border_radius="29px",
                            padding="20px",
                            border=f"2px solid {Custom_theme().light_colors()['primary']}",
                            transition="all 0.2s ease",
                            margin_bottom="2em",
                            width="100%"
                        ),

                        spacing="0",
                        width="100%"
                    ),

                    # ❌ Sección de domicilios guardados - DESHABILITADA (solo recolección disponible)
                    rx.cond(
                        False,  # Ocultar domicilios mientras solo hay recolección
                        rx.vstack(
                            rx.text(
                                "Selecciona una dirección de envío",
                                size="3",
                                font_weight="semibold",
                                margin_bottom="0.5em"
                            ),
                            rx.vstack(
                                *[rx.box(
                                    rx.hstack(
                                        rx.vstack(
                                            rx.hstack(
                                                rx.icon("map-pin", size=16, color=Custom_theme().light_colors()["primary"]),
                                                rx.text(address["name"], font_weight="semibold", font_size="0.9rem"),
                                                align="center",
                                                spacing="2"
                                            ),
                                            rx.text(
                                                address["address"],
                                                font_size="0.8rem",
                                                color="gray",
                                                margin_top="0.25em"
                                            ),
                                            rx.hstack(
                                                rx.icon("user", size=12, color="gray"),
                                                rx.text(address["recipient"], font_size="0.8rem", color="gray"),
                                                rx.icon("phone", size=12, color="gray"),
                                                rx.text(address["phone"], font_size="0.8rem", color="gray"),
                                                spacing="1",
                                                margin_top="0.25em"
                                            ),
                                            align="start",
                                            spacing="1"
                                        ),
                                        rx.spacer(),
                                        rx.button(
                                            rx.icon("square-pen", size=14),
                                            variant="ghost",
                                            size="1",
                                            border_radius="8px",
                                            padding="8px"
                                        ),
                                        align="start",
                                        width="100%"
                                    ),
                                    bg=rx.color_mode_cond(
                                        light="rgba(59, 130, 246, 0.05)",
                                        dark="rgba(59, 130, 246, 0.1)"
                                    ),
                                    border=f"1px solid rgba(59, 130, 246, 0.2)",
                                    border_radius="29px",
                                    padding="16px",
                                    margin_bottom="12px",
                                    width="100%"
                                ) for address in saved_addresses],
                                spacing="0",
                                width="100%",
                                margin_bottom="1em"
                            ),

                            # Botón para agregar nueva dirección
                            rx.button(
                                rx.hstack(
                                    rx.icon("plus", size=16),
                                    rx.text("Agregar nueva dirección"),
                                    spacing="2",
                                    align="center"
                                ),
                                variant="outline",
                                size="2",
                                border_radius="15px",
                                width="100%",
                                _hover={"bg": "rgba(59, 130, 246, 0.05)"}
                            ),
                            spacing="0",
                            width="100%"
                        ),
                        rx.box()  # Elemento vacío cuando no se cumple la condición
                    ),

                    # Sección condicional: CEDIS disponibles
                    rx.cond(
                        False,  # Aquí iría la condición para mostrar CEDIS
                        rx.vstack(
                            rx.text(
                                "Selecciona un CEDIS para recoger",
                                font_size="1rem",
                                font_weight="semibold",
                                margin_bottom="1em"
                            ),
                            rx.vstack(
                                *[rx.box(
                                    rx.hstack(
                                        rx.vstack(
                                            rx.hstack(
                                                rx.icon("building", size=16, color=Custom_theme().light_colors()["primary"]),
                                                rx.text(cedis["name"], font_weight="semibold", font_size="0.9rem"),
                                                align="center",
                                                spacing="2"
                                            ),
                                            rx.text(
                                                cedis["address"],
                                                font_size="0.8rem",
                                                color="gray",
                                                margin_top="0.25em"
                                            ),
                                            rx.hstack(
                                                rx.icon("clock", size=12, color="gray"),
                                                rx.text(cedis["schedule"], font_size="0.8rem", color="gray"),
                                                spacing="1",
                                                margin_top="0.25em"
                                            ),
                                            rx.hstack(
                                                rx.icon("phone", size=12, color="gray"),
                                                rx.text(cedis["phone"], font_size="0.8rem", color="gray"),
                                                spacing="1",
                                                margin_top="0.25em"
                                            ),
                                            align="start",
                                            spacing="1"
                                        ),
                                        rx.spacer(),
                                        rx.button(
                                            rx.icon("navigation", size=14),
                                            variant="ghost",
                                            size="1",
                                            border_radius="8px",
                                            padding="8px"
                                        ),
                                        align="start",
                                        width="100%"
                                    ),
                                    bg=rx.color_mode_cond(
                                        light="rgba(5, 150, 105, 0.05)",
                                        dark="rgba(5, 150, 105, 0.1)"
                                    ),
                                    border="1px solid rgba(5, 150, 105, 0.2)",
                                    border_radius="12px",
                                    padding="16px",
                                    margin_bottom="12px",
                                    width="100%"
                                ) for cedis in cedis_locations],
                                spacing="0",
                                width="100%",
                                margin_bottom="1.5em"
                            ),

                            # Información adicional sobre recogida
                            rx.box(
                                rx.vstack(
                                    rx.hstack(
                                        rx.icon("info", size=16, color="#f59e0b"),
                                        rx.text("Información importante", font_weight="semibold", font_size="0.9rem"),
                                        align="center",
                                        spacing="2"
                                    ),
                                    rx.text(
                                        "• Presenta identificación oficial al recoger",
                                        font_size="0.8rem",
                                        color="gray"
                                    ),
                                    rx.text(
                                        "• El pedido estará disponible 24 horas después de la confirmación",
                                        font_size="0.8rem",
                                        color="gray"
                                    ),
                                    rx.text(
                                        "• Horarios sujetos a cambios, verifica antes de acudir",
                                        font_size="0.8rem",
                                        color="gray"
                                    ),
                                    spacing="1",
                                    align="start"
                                ),
                                bg="rgba(245, 158, 11, 0.05)",
                                border="1px solid rgba(245, 158, 11, 0.2)",
                                border_radius="12px",
                                padding="16px",
                                width="100%"
                            ),
                            spacing="0",
                            width="100%"
                        ),
                        rx.box()  # Elemento vacío cuando no se cumple la condición
                    ),

                    # Botón de continuar
                    rx.link(
                        rx.button(
                            "Continuar con el pago",
                            bg=Custom_theme().light_colors()["primary"],
                            color="white",
                            size="4",
                            border_radius="32px",
                            width="90.5%",
                            _hover={"opacity": 0.9, "transform": "translateY(-1px)"},
                            transition="all 0.2s ease",
                            #margin_top="2em",
                            position="fixed",
                            bottom="1em",
                            left="1em",
                            right="1em",
                            justify="end",
                        ),
                        href="/payment",
                        width="100%"
                    ),
                    # Propiedades del vstack principal móvil
                    margin="80px 0 20px 0",  # Espacio para el header fijo
                    width="100%",
                    padding="0 1em",
                ),
                height="100vh",
            ),
            width="100%",
        ),

        # Propiedades del contenedor principal
        bg=rx.color_mode_cond(
            light=Custom_theme().light_colors()["background"],
            dark=Custom_theme().dark_colors()["background"]
        ),
        position="absolute",
        width="100%",
    )