"""Nueva Backoffice NN Protect | Compras"""

import reflex as rx
from rxconfig import config

from ....components.shared_ui.theme import Custom_theme
from ....components.shared_ui.layout import main_container_derecha, mobile_header, desktop_sidebar, header

# Importar OrderDetailState para datos dinámicos
from ..state.orders_state import OrderDetailState

# ============================================================================
# COMPONENTES REUTILIZABLES
# ============================================================================

def product_row_desktop(item: dict) -> rx.Component:
    """Renderiza una fila de producto en el detalle de orden (desktop)
    
    Args:
        item: Dict con datos del producto (product_name, quantity, unit_price_formatted, 
              line_total_formatted, unit_pv, line_pv, presentation)
    """
    return rx.flex(
        rx.vstack(
            rx.text(
                f"{item['product_name']} {item.get('presentation', '')}",
                font_size="1em",
                font_weight="bold"
            ),
            rx.flex(
                rx.text(
                    f"Cantidad: {item['quantity']}",
                    font_size="0.8em",
                    color="#6B7280"
                ),
                rx.text(
                    f"Precio unitario: {item['unit_price_formatted']}",
                    font_size="0.8em",
                    color="#6B7280"
                ),
                rx.text(
                    f"{item['unit_pv']} PV por producto",
                    font_size="0.8em",
                    color="#6B7280"
                ),
                spacing="3",
            ),
        ),
        rx.vstack(
            rx.text(
                item['line_total_formatted'],
                font_size="1em",
                font_weight="bold"
            ),
            rx.badge(
                f"{item['line_pv']} PV",
                color_scheme="green",
                font_size="0.8em",
                border_radius="12px",
            ),
            align="end",
        ),
        bg=rx.color_mode_cond(
            light=Custom_theme().light_colors()["background"],
            dark=Custom_theme().dark_colors()["background"]
        ),
        border_radius="16px",
        padding="1em",
        width="100%",
        justify="between",
    )

def product_row_mobile(item: dict) -> rx.Component:
    """Renderiza una fila de producto en el detalle de orden (mobile)
    
    Args:
        item: Dict con datos del producto
    """
    return rx.box(
        rx.hstack(
            rx.text(
                f"{item['product_name']} {item.get('presentation', '')}",
                font_size="1em"
            ),
            spacing="1",
        ),
        rx.hstack(
            rx.vstack(
                rx.text(
                    f"Cantidad: {item['quantity']}",
                    font_size="0.9em",
                    color="gray",
                    margin_bottom="-1em"
                ),
                rx.text(
                    f"Precio: {item['unit_price_formatted']}",
                    font_size="0.9em",
                    color="gray",
                    margin_bottom="-1em"
                ),
                rx.hstack(
                    rx.text(
                        f"{item['unit_pv']} PV",
                        font_size="0.9em",
                        color=rx.color("green", 9)
                    ),
                    rx.text(
                        f"{item['unit_vn']} VN",
                        font_size="0.9em",
                        color=rx.color("blue", 9)
                    ),
                    spacing="2",
                )
            ),
            rx.vstack(
                rx.text(
                    item['line_total_formatted'],
                    font_size="0.9em",
                    font_weight="600",
                    margin_bottom="-1em"
                ),
                rx.text(
                    f"{item['line_pv']} PV",
                    font_size="0.9em",
                    color=rx.color("blue", 9),
                    margin_bottom="-1em"
                ),
                rx.text(
                    f"{item['line_vn']} VN",
                    font_size="0.9em",
                    color=rx.color("green", 9)
                ),
                align="end",
            ),
            align="center",
            justify="between",
        ),
        bg=rx.color_mode_cond(
            light=Custom_theme().light_colors()["tertiary"],
            dark=Custom_theme().dark_colors()["tertiary"]
        ),
        justify="between",
        border_radius="32px",
        padding="1em",
        width="100%",
        spacing="2",
    )

def order_details() -> rx.Component:
    return rx.center(
        rx.desktop_only(
            rx.vstack(
                header(),
                rx.hstack(
                    desktop_sidebar(),
                    main_container_derecha(
                        rx.vstack(
                            rx.text(
                                "Compras",
                                font_size="2rem",
                                font_weight="bold",
                            ),

                            # Mostrar loading, error o contenido
                            rx.cond(
                                OrderDetailState.is_loading,
                                # Estado: Cargando
                                rx.center(
                                    rx.vstack(
                                        rx.spinner(size="3"),
                                        rx.text("Cargando detalles de la orden...", font_size="1em", color="gray"),
                                        spacing="3",
                                        align="center"
                                    ),
                                    width="100%",
                                    padding="4em"
                                ),
                                rx.cond(
                                    OrderDetailState.error_message != "",
                                    # Estado: Error
                                    rx.center(
                                        rx.vstack(
                                            rx.icon("circle-x", size=48, color="red"),
                                            rx.heading("Error al cargar orden", size="5", color="red"),
                                            rx.text(OrderDetailState.error_message, font_size="1em", color="gray"),
                                            rx.button(
                                                "Volver a órdenes",
                                                on_click=lambda: rx.redirect("/orders"),
                                                variant="solid",
                                                color_scheme="blue"
                                            ),
                                            spacing="3",
                                            align="center"
                                        ),
                                        width="100%",
                                        padding="4em"
                                    ),
                                    # Estado: Contenido cargado
                                    rx.box(
                                        rx.hstack(
                                            rx.heading(
                                                f"Orden #{OrderDetailState.order_data['order_id']}",
                                                size="6",
                                            ),
                                            rx.heading(
                                                f"{OrderDetailState.order_data['total_formatted']} {OrderDetailState.order_data['currency']}",
                                                color=rx.color_mode_cond(
                                                    light=Custom_theme().light_colors()["secondary"],
                                                    dark=Custom_theme().light_colors()["secondary"],
                                                ),
                                                size="6",
                                            ),
                                            justify="between",
                                            margin_bottom="1em"
                                        ),
                                        rx.separator(
                                            orientation="horizontal",
                                            margin_bottom="1em"
                                        ),

                                        # Detalles de la compra y productos
                                        rx.vstack(
                                            # Tarjeta resumen (Desktop)
                                            rx.flex(
                                                rx.flex(
                                                    rx.hstack(
                                                        rx.icon("calendar", size=20, color="#6B7280"),
                                                        rx.text(
                                                            OrderDetailState.order_data['created_at_display'],
                                                            font_size="0.9em",
                                                            color="#6B7280"
                                                        ),
                                                    ),
                                                    rx.hstack(
                                                        rx.icon("map-pinned", size=20, color="#6B7280"),
                                                        rx.text(
                                                            OrderDetailState.order_data['address_alias'],
                                                            font_size="0.9em",
                                                            color="#6B7280"
                                                        ),
                                                    ),
                                                    rx.hstack(
                                                        rx.icon("credit-card", size=20, color="#6B7280"),
                                                        rx.text(
                                                            OrderDetailState.order_data['payment_method'],
                                                            font_size="0.9em",
                                                            color="#6B7280"
                                                        ),
                                                    ),
                                                    rx.hstack(
                                                        rx.icon("container", size=20, color="#6B7280"),
                                                        rx.text(
                                                            "CEDIS: Por definir",
                                                            font_size="0.9em",
                                                            color="#6B7280"
                                                        ),
                                                    ),
                                                    spacing="5",
                                                    direction="row",
                                                ),
                                                rx.flex(
                                                    rx.badge(
                                                        OrderDetailState.order_data['status'],
                                                        color_scheme=OrderDetailState.order_data['badge_color'],
                                                        font_size="0.8em",
                                                        border_radius="12px",
                                                        padding="0.2em 1em"
                                                    ),
                                                    rx.button(
                                                        rx.icon("download", size=16),
                                                        "PDF",
                                                        variant="outline",
                                                        color_scheme="blue",
                                                        font_size="0.8em",
                                                        border_radius="24px",
                                                    ),
                                                    spacing="3",
                                                    direction="column",
                                                ),
                                                justify="between",
                                                direction="row",
                                                margin_bottom="3em",
                                                width="100%"
                                            ),
                                            
                                            # Lista de productos (Iterador)
                                            rx.vstack(
                                                rx.foreach(
                                                    OrderDetailState.order_items,
                                                    product_row_desktop
                                                ),
                                                width="100%",
                                                spacing="4"
                                            ),
                                            
                                            width="100%"
                                        ),

                                # Estado del pedido
                                rx.flex(
                                    rx.vstack(
                                        rx.box(
                                            rx.icon("clipboard-check", size=24, color="#FFFFFF"),
                                            bg="#6B7280" + "70",
                                            border_radius="50%",
                                            padding="10px",
                                        ),
                                        rx.text("Programado", font_size="0.8em", color="#6B7280"),
                                        align="center",
                                    ),
                                    rx.vstack(
                                        rx.box(
                                            rx.icon("package-open", size=24, color="#FFFFFF"),
                                            bg="#6B7280" + "70",
                                            border_radius="50%",
                                            padding="10px",
                                        ),
                                        rx.text("En preparación", font_size="0.8em", color="#6B7280"),
                                        align="center",
                                    ),
                                    rx.vstack(
                                        rx.box(
                                            rx.icon("truck", size=24, color="#FFFFFF"),
                                            bg="#6B7280" + "70",
                                            border_radius="50%",
                                            padding="10px",
                                        ),
                                        rx.text("Enviado", font_size="0.8em", color="#6B7280"),
                                        align="center",
                                    ),
                                    rx.vstack(
                                        rx.box(
                                            rx.icon("package-check", size=24, color="#FFFFFF"),
                                            #bg="#0BD43A",
                                            bg="#6B7280" + "70",
                                            border_radius="50%",
                                            padding="10px",
                                        ),
                                        rx.text("Entregado", font_size="0.8em", color="#6B7280"),
                                        align="center",
                                    ),
                                    spacing="9",
                                    justify="center",
                                    width="100%",
                                    direction="row",
                                ),

                                rx.separator(
                                    margin="1em 0 1em 0"
                                ),

                                # Productos comprados
                                rx.text(
                                    "Productos",
                                    font_size="1rem",
                                    font_weight="bold",
                                    margin_bottom="1em",
                                ),

                                rx.vstack(
                                    rx.foreach(
                                        OrderDetailState.order_items,
                                        product_row_desktop
                                    ),
                                ),


                                        bg=rx.color_mode_cond(
                                            light=Custom_theme().light_colors()["tertiary"],
                                            dark=Custom_theme().dark_colors()["tertiary"]
                                        ),
                                        border_radius="24px",
                                        margin_bottom="32px",
                                        padding="16px",
                                        min_width="240px",
                                        width="100%",
                                    )  # Cierra rx.box del contenido
                                )  # Cierra rx.cond del error
                            ),  # Cierra rx.cond del loading

                            width="100%",
                        ),
                    )
                ),
                align="end",
                margin_top="8em",
                margin_bottom="0.2em",
                max_width="1920px",
            )
        ),

        rx.mobile_only(
            rx.vstack(
                # Header móvil
                mobile_header(),
                
                # Contenido principal móvil
                rx.cond(
                    OrderDetailState.is_loading,
                    # Estado: Cargando
                    rx.center(
                        rx.vstack(
                            rx.spinner(size="3"),
                            rx.text("Cargando...", font_size="1em", color="gray"),
                            spacing="3",
                            align="center"
                        ),
                        width="100%",
                        padding="4em"
                    ),
                    rx.cond(
                        OrderDetailState.error_message != "",
                        # Estado: Error
                        rx.center(
                            rx.vstack(
                                rx.icon("circle-x", size=48, color="red"),
                                rx.heading("Error", size="5", color="red"),
                                rx.text(OrderDetailState.error_message, font_size="1em", color="gray"),
                                rx.button(
                                    "Volver",
                                    on_click=lambda: rx.redirect("/orders"),
                                    variant="solid"
                                ),
                                spacing="3",
                                align="center"
                            ),
                            width="100%",
                            padding="4em"
                        ),
                        # Estado: Contenido
                        rx.vstack(
                            rx.text(
                                f"Detalles de orden #{OrderDetailState.order_data['order_id']}",
                                font_size="1.5rem",
                                font_weight="bold",
                                margin_bottom="1rem",
                                text_align="center"
                            ),
                            
                            rx.box(
                                rx.vstack(
                                    # Detalles de la orden
                                    rx.vstack(
                                        rx.vstack(
                                            rx.hstack(
                                                rx.text(
                                                    f"{OrderDetailState.order_data['total_formatted']} {OrderDetailState.order_data['currency']}",
                                                    font_weight="bold",
                                                    font_size="1.5em",
                                                    color=rx.color_mode_cond(
                                                        light=Custom_theme().light_colors()["primary"],
                                                        dark=Custom_theme().dark_colors()["primary"]
                                                    )
                                                ),
                                                rx.text(
                                                    f"{OrderDetailState.order_data['total_pv']} PV",
                                                    font_weight="bold",
                                                    font_size="1.5em",
                                                    color=rx.color_mode_cond(
                                                        light=Custom_theme().light_colors()["success"],
                                                        dark=Custom_theme().dark_colors()["success"]
                                                    )
                                                ),
                                            ),
                                            rx.badge(
                                                OrderDetailState.order_data['status'],
                                                color_scheme=OrderDetailState.order_data['badge_color'],
                                                size="2",
                                                radius="full"
                                            ),
                                            spacing="1",
                                            width="100%",
                                            align="end",
                                        ),

                                        rx.divider(margin_y="0.5em"),

                                        rx.hstack(
                                            rx.icon("calendar", size=16, color=rx.color("gray", 11)),
                                            rx.text(
                                                OrderDetailState.order_data['created_at_display'],
                                                font_size="1em",
                                                color=rx.color("gray", 11)
                                            ),
                                            align="center",
                                            spacing="1"
                                        ),
                                        rx.hstack(
                                            rx.icon("credit-card", size=16, color=rx.color("gray", 11)),
                                            rx.text(
                                                OrderDetailState.order_data['payment_method'],
                                                font_size="1em",
                                                color=rx.color("gray", 11)
                                            ),
                                            align="center",
                                            spacing="1"
                                        ),
                                        rx.hstack(
                                            rx.icon("map-pin", size=16, color=rx.color("gray", 11)),
                                            rx.text(
                                                OrderDetailState.order_data['shipping_address'],
                                                font_size="1em",
                                                color=rx.color("gray", 11),
                                                white_space="pre-line",
                                                margin_top="-0.2em"
                                            ),
                                            align="start",
                                            spacing="1"
                                        ),
                                        spacing="2",
                                        width="100%"
                                    ),
                                    
                                    rx.divider(margin_y="0.5em"),
                                    
                                    # Productos
                                    rx.text("Productos", font_weight="bold", font_size="1.25em"),
                                    rx.vstack(
                                        rx.foreach(
                                            OrderDetailState.order_items,
                                            product_row_mobile
                                        ),
                                        spacing="2",
                                        width="100%"
                                    ),
                                    
                                    # Botón de detalles
                                    rx.button(
                                        rx.icon("eye", size=20),
                                        "Ver PDF",
                                        margin_top="1rem",
                                        variant="outline",
                                        width="100%",
                                        size="3",
                                        font_size="1em",
                                        radius="full",
                                    ),
                                    spacing="2",
                                    width="100%"
                                ),
                                width="100%",
                            ),
                            spacing="4",
                            width="100%",
                            padding="1rem",
                            margin_top="80px",
                            margin_bottom="2rem",
                            height="100%",
                        ),
                    ),
                ),
                height="100%",
            ),
            height="100vh",
            width="100%",
        ),
        height="100%",
        bg=rx.color_mode_cond(
            light=Custom_theme().light_colors()["background"],
            dark=Custom_theme().dark_colors()["background"]
        ),
        width="100%",
        on_mount=OrderDetailState.load_order_from_url
    )