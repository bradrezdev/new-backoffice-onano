"""Nueva Backoffice NN Protect | Método de pago"""

import reflex as rx
from rxconfig import config

from ....components.shared_ui.theme import Custom_theme
from ....components.shared_ui.layout import main_container_derecha, mobile_header, desktop_sidebar, mobile_sidebar, header

# Importaciones para creación de órdenes y pago
from ....modules.auth.auth_state import AuthState
from ....modules.store.state.store_state import CountProducts
from ..state.payment_state import PaymentState


def payment() -> rx.Component:
    # 📦 EJEMPLO DE REUTILIZACIÓN DE DATOS DEL CARRITO
    # Usando CountProducts podemos acceder a toda la información
    # del carrito desde cualquier página de forma dinámica

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
                        "Método de pago",
                        size="8",
                        font_weight="bold",
                        text_align="center",
                    ),

                    rx.text(
                        "Selecciona cómo quieres pagar tu pedido",
                        size="2",
                        color="gray",
                        margin_bottom="2em",
                        text_align="center"
                    ),

                    # Opciones de pago disponibles
                    rx.vstack(
                        # Opción 1: Saldo en billetera
                        rx.box(
                            rx.hstack(
                                # Icono de billetera
                                rx.box(
                                    rx.icon("wallet", size=24, color="#059669"),
                                    width="48px",
                                    height="48px",
                                    bg="rgba(5, 150, 105, 0.1)",
                                    border_radius="12px",
                                    display="flex",
                                    align_items="center",
                                    justify_content="center",
                                    margin_right="1em"
                                ),

                                # Información de la billetera
                                rx.vstack(
                                    rx.hstack(
                                        rx.text("Saldo en billetera", font_weight="semibold", size="3"),
                                        rx.cond(
                                            PaymentState.payment_method == "wallet",
                                            rx.badge("Seleccionado", color_scheme="green", size="1"),
                                            rx.fragment(),
                                        ),
                                        align="center",
                                        width="100%"
                                    ),

                                    rx.vstack(
                                        rx.text(
                                            f"Saldo actual: ${AuthState.profile_data.get('wallet_balance', 0)} MXN",
                                            size="3",
                                            font_weight="medium",
                                            color="#059669"
                                        ),
                                        rx.text(
                                            "Pago instantáneo",
                                            size="1",
                                            color="gray"
                                        ),
                                        align="start",
                                        spacing="1"
                                    ),

                                    align="start",
                                    spacing="1",
                                    flex="1"
                                ),

                                align="center",
                                width="100%",
                                spacing="0"
                            ),

                            # Estilos de la tarjeta
                            border=rx.cond(
                                PaymentState.payment_method == "wallet",
                                "2px solid #059669",
                                "2px solid transparent"
                            ),
                            bg=rx.color_mode_cond(
                                light=Custom_theme().light_colors()["tertiary"],
                                dark=Custom_theme().dark_colors()["tertiary"]
                            ),
                            border_radius="32px",
                            padding="1em",
                            #border="2px solid transparent",
                            _hover={"border": "2px solid #059669"},
                            transition="all 0.2s ease",
                            margin_bottom="16px",
                            width="100%",
                            cursor="pointer"
                        ),

                        # Opción 2: Tarjeta de Débito/Crédito
                        rx.box(
                            rx.hstack(
                                # Icono de tarjeta
                                rx.box(
                                    rx.icon("credit-card", size=24, color=Custom_theme().light_colors()["primary"]),
                                    width="48px",
                                    height="48px",
                                    bg=rx.color_mode_cond(
                                        light="rgba(0, 57, 242, 0.1)",
                                        dark="rgba(0, 57, 242, 0.2)"
                                    ),
                                    border_radius="12px",
                                    display="flex",
                                    align_items="center",
                                    justify_content="center",
                                    margin_right="1em"
                                ),

                                # Información de tarjeta
                                rx.vstack(
                                    rx.hstack(
                                        rx.text("Tarjeta de Débito/Crédito", font_weight="semibold", size="3"),
                                        align="center",
                                        width="100%"
                                    ),

                                    rx.vstack(
                                        rx.text(
                                            "Visa, Mastercard, American Express",
                                            size="1",
                                            color="gray"
                                        ),
                                        align="start",
                                        spacing="1"
                                    ),

                                    align="start",
                                    spacing="1",
                                    flex="1"
                                ),

                                align="center",
                                width="100%",
                                spacing="0"
                            ),

                            # Estilos de la tarjeta
                            bg=rx.color_mode_cond(
                                light=Custom_theme().light_colors()["tertiary"],
                                dark=Custom_theme().dark_colors()["tertiary"]
                            ),
                            border_radius="32px",
                            padding="1em",
                            border="2px solid transparent",
                            _hover={"border": "2px solid #d1d5db"},
                            transition="all 0.2s ease",
                            margin_bottom="16px",
                            width="100%",
                            cursor="not-allowed",
                            opacity="0.7"
                        ),
                        spacing="0",
                        width="100%",
                        margin_bottom="2em"
                    ),

                    # Métodos de pago alternativos
                    rx.vstack(
                        rx.text(
                            "Otros métodos",
                            size="4",

                            text_align="center"
                        ),
                        rx.text(
                            "Los siguientes pagos pueden tardar más en procesarse",
                            font_size="0.85em",
                            color="gray",
                            margin_bottom="1em",
                        ),

                        # Opción 1: Transferencia bancaria
                        rx.box(
                            rx.hstack(
                                rx.box(
                                    rx.icon("dollar-sign", size=24, color="#059669"),
                                    width="48px",
                                    height="48px",
                                    bg="rgba(5, 150, 105, 0.1)",
                                    border_radius="12px",
                                    display="flex",
                                    align_items="center",
                                    justify_content="center",
                                    margin_right="1em"
                                ),

                                rx.vstack(
                                    rx.text("Transferencia bancaria", font_weight="semibold", font_size="1rem"),
                                    rx.text(
                                        "Confirmación de pago\nentre 48-72 horas hábiles",
                                        font_size="0.85rem",
                                        color="gray",
                                        white_space="pre"
                                    ),
                                    align="start",
                                    spacing="1",
                                    flex="1"
                                ),

                                align="center",
                                width="100%",
                                spacing="0"
                            ),

                            bg=rx.color_mode_cond(
                                light=Custom_theme().light_colors()["tertiary"],
                                dark=Custom_theme().dark_colors()["tertiary"]
                            ),
                            border_radius="32px",
                            padding="1em",
                            border="2px solid transparent",
                            _hover={"border": "2px solid #059669"},
                            transition="all 0.2s ease",
                            margin_bottom="12px",
                            width="100%",
                            cursor="not-allowed",
                            opacity="0.7"
                        ),


                        # Opción 2: Pago en OXXO
                        rx.box(
                            rx.hstack(
                                # Icono de OXXO
                                rx.box(
                                    rx.box(
                                        rx.text("OXXO", font_size="0.7rem", font_weight="bold", color="#d32f2f"),
                                        width="100%",
                                        height="100%",
                                        display="flex",
                                        align_items="center",
                                        justify_content="center"
                                    ),
                                    width="48px",
                                    height="48px",
                                    bg="rgba(211, 47, 47, 0.1)",
                                    border_radius="12px",
                                    display="flex",
                                    align_items="center",
                                    justify_content="center",
                                    margin_right="1em"
                                ),

                                # Información de OXXO
                                rx.vstack(
                                    rx.hstack(
                                        rx.text("Pago en OXXO", font_weight="semibold", size="3"),
                                        align="center",
                                        width="100%"
                                    ),

                                    rx.vstack(
                                        rx.text(
                                            "Paga en cualquier tienda OXXO\n",
                                            size="1",
                                            color="gray"
                                        ),
                                        align="start",
                                        spacing="1"
                                    ),

                                    align="start",
                                    spacing="1",
                                    flex="1"
                                ),

                                align="center",
                                width="100%",
                                spacing="0"
                            ),

                            # Estilos de la tarjeta
                            bg=rx.color_mode_cond(
                                light=Custom_theme().light_colors()["tertiary"],
                                dark=Custom_theme().dark_colors()["tertiary"]
                            ),
                            border_radius="32px",
                            padding="1em",
                            border="2px solid transparent",
                            _hover={"border": "2px solid #d32f2f"},
                            transition="all 0.2s ease",
                            margin_bottom="16px",
                            width="100%",
                            cursor="not-allowed",
                            opacity="0.7"
                        ),

                        spacing="0",
                        width="100%",
                        margin_bottom="2em"
                    ),

                    # Espacio para el box flotante
                    rx.box(height="200px"),

                    # Propiedades del vstack principal móvil
                    margin="80px 0 20px 0",
                    width="100%",
                    padding="0 1em",
                ),

                # Box flotante con resumen de pago - copiado de shopping_cart.py
                rx.box(
                    rx.vstack(
                        # Línea divisoria superior
                        rx.box(
                            width="60px",
                            height="4px",
                            bg="rgba(0,0,0,0.2)",
                            border_radius="2px",
                            margin="0 auto 1em auto"
                        ),

                        # Resumen del pedido
                        rx.vstack(
                            # Productos
                            rx.hstack(
                                rx.text(f"Productos ({CountProducts.cart_total})", font_size="0.9rem", color="gray"),
                                rx.spacer(),
                                rx.text(f"${CountProducts.cart_subtotal:.2f}", font_size="0.9rem", font_weight="medium"),
                                width="100%",
                                align="center"
                            ),

                            # Puntos de volumen
                            rx.hstack(
                                rx.text("Puntos de volumen", font_size="0.9rem", color="gray"),
                                rx.spacer(),
                                rx.text(f"{CountProducts.cart_volume_points} pts", font_size="0.9rem", font_weight="medium", color="#f59e0b"),
                                width="100%",
                                align="center"
                            ),

                            # Costo de envío
                            rx.hstack(
                                rx.text("Costo de envío", font_size="0.9rem", color="gray"),
                                rx.spacer(),
                                rx.cond(
                                    CountProducts.cart_shipping_cost == 0,
                                    rx.text("GRATIS", font_size="0.9rem", font_weight="medium", color="#059669"),
                                    rx.text(f"${CountProducts.cart_shipping_cost:.2f}", font_size="0.9rem", font_weight="medium")
                                ),
                                width="100%",
                                align="center"
                            ),

                            # Línea divisoria
                            rx.box(
                                height="1px",
                                bg="rgba(0,0,0,0.1)",
                                width="100%",
                                margin="0.5em 0"
                            ),

                            # Total
                            rx.hstack(
                                rx.text("Total", font_size="1rem", font_weight="bold"),
                                rx.spacer(),
                                rx.text(f"${CountProducts.cart_final_total:.2f}", font_size="1rem", font_weight="bold", color=Custom_theme().light_colors()["primary"]),
                                width="100%",
                                align="center"
                            ),

                            spacing="1",
                            width="100%"
                        ),

                        # Botones de acción
                        rx.vstack(
                            rx.button(
                                rx.cond(
                                    PaymentState.is_processing,
                                    rx.hstack(
                                        rx.spinner(size="3", color="white"),
                                        rx.text("Procesando…", color="white"),
                                        align="center",
                                        justify="center",
                                        spacing="2"
                                    ),
                                    "Confirmar pago"
                                ),
                                on_click=PaymentState.confirm_payment,
                                is_disabled=PaymentState.is_processing,
                                cursor=rx.cond(PaymentState.is_processing, "not-allowed", "pointer"),
                                opacity=rx.cond(PaymentState.is_processing, "0.7", "1"),
                                align="center",
                                bg=Custom_theme().light_colors()["primary"],
                                color="white",
                                size="4",
                                border_radius="32px",
                                padding="16px",
                                width="100%",
                                _hover={"opacity": 0.9, "transform": "translateY(-1px)"},
                                transition="all 0.2s ease",
                            ),
                            spacing="2",
                            width="100%",
                            margin_top="1em"
                        ),
                        spacing="0",
                        width="100%"
                    ),

                    # Estilos del box flotante
                    bg=rx.color_mode_cond(
                        light=Custom_theme().light_colors()["tertiary"],
                        dark=Custom_theme().dark_colors()["tertiary"]
                    ),
                    border_radius="29px 29px 0 0",
                    padding="20px",
                    box_shadow="0 -4px 12px rgba(0, 0, 0, 0.1)",
                    border_top="1px solid rgba(0,0,0,0.05)",
                    position="fixed",
                    bottom="0",
                    left="0",
                    right="0",
                    z_index="100",
                    width="100%",
                    max_width="100vw"
                ),
                width="100%",
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
        
        # 🔐 Cargar datos de autenticación al montar la página
        on_mount=[AuthState.load_user_from_token],
    )