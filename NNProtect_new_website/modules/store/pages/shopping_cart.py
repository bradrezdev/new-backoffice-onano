"""Nueva Backoffice NN Protect | Carrito de compras"""

import reflex as rx
from rxconfig import config

from ....components.shared_ui.theme import Custom_theme
from ....components.shared_ui.layout import main_container_derecha, mobile_header, desktop_sidebar, header

from ..state.store_state import CountProducts
from ..backend.product_manager import ProductManager
from database.addresses import Countries

from ..components.product_components import plusminus_buttons



def shopping_cart() -> rx.Component:

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
                        "Carrito de compras",
                        size="8",
                        font_weight="bold",
                    ),

                    rx.text(
                        rx.cond(
                            CountProducts.cart_total == 1,
                            f"{CountProducts.cart_total} producto en tu carrito", 
                            f"{CountProducts.cart_total} productos en tu carrito"
                        ),
                        font_size="0.9rem",
                        color="gray",
                        margin_bottom="1.5em",
                        text_align="center"
                    ),

                    # Lista de productos en el carrito
                    rx.vstack(
                        rx.foreach(
                            CountProducts.cart_items_detailed,
                            lambda item: rx.box(
                                rx.hstack(
                                    # Imagen del producto
                                    rx.box(
                                        rx.image(
                                            src=item["image"],
                                            height="60px",
                                            width="60px",
                                            object_fit="contain",
                                            border_radius="13px",
                                            bg="rgba(0,0,0,0.05)"
                                        ),
                                        border_radius="8px",
                                        overflow="hidden"
                                    ),

                                    # Información del producto
                                    rx.vstack(
                                        rx.text(
                                            item["name"],
                                            font_weight="semibold",
                                            font_size="0.9rem",
                                            line_height="1.2"
                                        ),
                                        rx.hstack(
                                            rx.text(
                                                f"${item['price']:.2f}",
                                                font_size="0.8rem",
                                                color=Custom_theme().light_colors()["primary"],
                                                font_weight="medium"
                                            ),
                                            rx.text(
                                                f"• {item['volume_points']} PV",
                                                font_size="0.8rem",
                                                color="gray"
                                            ),
                                            spacing="1",
                                            align="center"
                                        ),
                                        rx.text(
                                            f"Subtotal: ${item['subtotal']:.2f}",
                                            font_size="0.8rem",
                                            font_weight="medium",
                                            color="#059669"
                                        ),
                                        spacing="1",
                                        align="start",
                                        flex="1"
                                    ),

                                    # Controles de cantidad y eliminar
                                    rx.vstack(
                                        # Controles de cantidad
                                        rx.hstack(
                                            # Botón decrementar - CORREGIDO
                                            rx.button(
                                                rx.icon("minus", size=12),
                                                size="1",
                                                variant="outline",
                                                border_radius="32px",
                                                min_width="28px",
                                                height="28px",
                                                _hover={"bg": "rgba(239, 68, 68, 0.1)"},
                                                on_click=CountProducts.decrement_cart_item(item["id"]),  # ✅ CORREGIDO: sin lambda
                                            ),
                                            rx.box(
                                                rx.text(
                                                    item["quantity"],
                                                    font_size="0.9em",
                                                    font_weight="bold",
                                                    text_align="center"
                                                ),
                                                min_width="32px",
                                                height="28px",
                                                border_radius="32px",
                                                display="flex",
                                                align_items="center",
                                                justify_content="center"
                                            ),
                                            # Botón incrementar - CORREGIDO
                                            rx.button(
                                                rx.icon("plus", size=12),
                                                size="1",
                                                variant="soft",
                                                border_radius="32px",
                                                min_width="28px",
                                                height="28px",
                                                _hover={"bg": "rgba(34, 197, 94, 0.1)"},
                                                on_click=CountProducts.increment_cart_item(item["id"]),  # ✅ CORREGIDO: sin lambda
                                            ),
                                            spacing="1",
                                            align="center"
                                        ),

                                        # Botón eliminar - CORREGIDO
                                        rx.button(
                                            "Eliminar",
                                            #rx.icon("trash-2", size=16),
                                            variant="outline",
                                            size="2",
                                            border_radius="32px",
                                            #padding="6px",
                                            _hover={"bg": "rgba(239, 68, 68, 0.1)"},
                                            width="100%",
                                            margin_top="0.5em",
                                            on_click=CountProducts.remove_from_cart(item["id"]),  # ✅ CORREGIDO: sin lambda
                                        ),

                                        spacing="1",
                                        align="center"
                                    ),

                                    spacing="3",
                                    align="start",
                                    width="100%"
                                ),
                                bg=rx.color_mode_cond(
                                    light=Custom_theme().light_colors()["tertiary"],
                                    dark=Custom_theme().dark_colors()["tertiary"]
                                ),
                                border_radius="32px",
                                padding="16px",
                                #border="1px solid rgba(0,0,0,0.05)",
                                margin_bottom="12px",
                                width="100%"
                            )
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

                # Box flotante con resumen - posicionado fixed
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
                                rx.text(
                                    rx.cond(
                                        CountProducts.cart_total == 1,
                                        f"Productos ({CountProducts.cart_total})",
                                        f"Productos ({CountProducts.cart_total})"
                                    ), 
                                    font_size="0.9rem", 
                                    color="gray"
                                ),
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
                            rx.link(
                                rx.button(
                                    "Proceder al envío",
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
                                width="100%",
                                href="/shipment_method",
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
        on_mount=CountProducts.check_cart_access
    )