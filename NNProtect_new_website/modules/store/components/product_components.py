"""
Componentes de productos para la tienda NN Protect.
Genera tarjetas de productos con datos reales de la base de datos.
"""
import reflex as rx
from typing import Dict
from ....components.shared_ui.theme import Custom_theme

from ....modules.store.state.store_state import CountProducts

def plusminus_buttons(product_id: int):
    """
    Botones con contador reactivo directo.
    Principio KISS: acceso directo a variables de estado.
    Reflex 0.6+: Event handlers con parámetros se pasan directamente.
    """
    return rx.hstack(
        rx.button(
            "-",
            size="1",
            variant=rx.color_mode_cond(
                light="soft",
                dark="outline",
            ),
            border_radius="100px",
            min_width="36px",
            height="36px",
            on_click=CountProducts.decrement(product_id)  # ✅ CORREGIDO: sin lambda
        ),
        rx.text(
            CountProducts.get_count_reactive.get(str(product_id), 0),
            font_size="0.9rem",
            font_weight="bold",
            min_width="40px",
            text_align="center"
        ),
        rx.button(
            "+",
            size="1",
            bg=rx.color_mode_cond(
                light=Custom_theme().light_colors()["primary"],
                dark=Custom_theme().dark_colors()["primary"]
            ),
            border_radius="100px",
            min_width="36px",
            height="36px",
            on_click=CountProducts.increment(product_id)  # ✅ CORREGIDO: sin lambda
        ),
        justify="center",
        spacing="2",
        align="center",
        margin_bottom="2em"
    )


def product_card(product_data: Dict, is_popular: bool = False) -> rx.Component:
    """
    Crea una tarjeta de producto con datos reales.
    Principio KISS: diseño simple y funcional.
    
    Args:
        product_data: Diccionario con datos del producto
        is_popular: Si mostrar badge de popular
        
    Returns:
        rx.Component: Tarjeta del producto
    """
    return rx.box(
        rx.vstack(
            # Badge de popular si aplica
            rx.cond(
                is_popular,
                rx.badge(
                    "⭐ Popular",
                    color_scheme="orange",
                    size="1",
                    position="absolute",
                    top="8px",
                    right="8px",
                    z_index="10"
                )
            ),

            # Imagen del producto (usar ID para consistencia)
            rx.image(
                src="image",
                #src=f"/product_{product_data.get('id', 1)}.jpg",
                height="100%",
                width="100%",
                object_fit="cover",
                border_radius="19px",
                bg="rgba(0,0,0,0.05)",
                margin_bottom="0.5em",
                loading="lazy"  # Optimización de carga
            ),

            # Información del producto
            rx.vstack(
                rx.text(
                    product_data.get("name", "Producto"),
                    font_weight="bold",
                    font_size="0.9rem",
                    text_align="center",
                    no_of_lines=2
                ),
                rx.text(
                    product_data.get("formatted_price", "$0.00"),
                    font_weight="600",
                    font_size="0.9rem",
                    color=rx.color_mode_cond(
                        light=Custom_theme().light_colors()["primary"],
                        dark=Custom_theme().dark_colors()["primary"]
                    ),
                    text_align="center"
                ),
                # Mostrar PV si está disponible
                rx.cond(
                    product_data.get("pv", 0) > 0,
                    rx.text(
                        f"PV: {product_data.get('pv', 0)}",
                        font_size="0.8rem",
                        color="gray",
                        text_align="center"
                    )
                ),
                spacing="1",
                align="center",
                width="100%"
            ),

            # Controles de cantidad
            plusminus_buttons(product_data.get("id", 1)),  # ✅ CORREGIDO: agregar paréntesis y product_id

            # Botón agregar
            rx.button(
                "Agregar",
                size="3",
                width="100%",
                variant="solid",
                border_radius="19px",
                bg=rx.color_mode_cond(
                    light=Custom_theme().light_colors()["primary"],
                    dark=Custom_theme().dark_colors()["primary"]
                ),
                color="white",
                _hover={"opacity": 0.9},
                on_click=CountProducts.add_to_cart(product_data.get("id", 1))
            ),

            spacing="3",
            align="center",
            width="100%"
        ),
        bg=rx.color_mode_cond(
            light=Custom_theme().light_colors()["tertiary"],
            dark=Custom_theme().dark_colors()["tertiary"]
        ),
        border_radius="29px",
        padding="10px",
        width="45vw",  # Ancho consistente con diseño existente
        position="relative"
    )



def _mobile_product_card_base(product_data: Dict, badge_text: str = None, badge_color: str = "blue", width: str = "100%", min_height: str = "360px") -> rx.Component:
    """
    Componente base unificado para tarjetas móviles.
    Garantiza consistencia visual en todas las secciones.
    """
    return rx.box(
        # Badge
        rx.cond(
            badge_text is not None,
            rx.badge(
                badge_text,
                color_scheme=badge_color,
                size="2",
                border_radius="12px",
                position="absolute",
                top="6px",
                right="6px",
                z_index="10"
            )
        ),

        rx.vstack(
            # Imagen - Fixed height container
            rx.box(
                rx.image(
                    src="image",
                    height="100%",
                    width="100%",
                    object_fit="contain",
                    border_radius="15px",
                    bg="white", # Ensure image has background if transparent
                    loading="lazy"
                ),
                height="160px",
                width="100%",
                bg="rgba(0,0,0,0.05)",
                border_radius="15px",
                margin_bottom="0.5em",
                padding="6px",
                overflow="hidden"
            ),

            # Info
            rx.vstack(
                rx.text(
                    product_data.get("name"),
                    font_weight="bold",
                    font_size="1em",
                    text_align="center",
                    no_of_lines=2,
                    height="2.5em"
                ),
                rx.text(
                    product_data.get("formatted_price"),
                    font_weight="600",
                    font_size="0.9em",
                    color=rx.color_mode_cond(
                        light=Custom_theme().light_colors()["primary"],
                        dark=Custom_theme().dark_colors()["secondary"]
                    ),
                    text_align="center"
                ),
                rx.text(
                    f"{product_data.get('pv')} PV",
                    font_size="0.9em",
                    color="gray",
                    text_align="center",
                ),
                spacing="1",
                align="center",
                width="100%"
            ),

            # Controls
            plusminus_buttons(product_data.get("id", 1)),

            # Button
            rx.button(
                "Agregar",
                size="3",
                width="100%",
                variant="solid",
                border_radius="19px",
                bg=rx.color_mode_cond(
                    light=Custom_theme().light_colors()["primary"],
                    dark=Custom_theme().dark_colors()["primary"]
                ),
                color="white",
                _hover={"opacity": 0.9},
                on_click=CountProducts.add_to_cart(product_data.get("id", 1))
            ),
            
            width="100%",
            spacing="2",
            align="center"
        ),

        bg=rx.color_mode_cond(
            light=Custom_theme().light_colors()["tertiary"],
            dark=Custom_theme().dark_colors()["tertiary"]
        ),
        border_radius="19px",
        padding="8px",
        min_height=min_height,
        width=width,
        flex_shrink="0",
        position="relative"
    )

def product_card_horizontal(product_data: Dict) -> rx.Component:
    """
    Tarjeta de producto para scroll horizontal (últimas novedades).
    Principio DRY: reutiliza estilos de product_card.
    """
    return rx.box(
        rx.vstack(
            # Imagen del producto
            rx.image(
                src="image",
                #src=f"/product_{product_data.get('id', 4)}.jpg",
                height="100%",
                width="100%",
                object_fit="cover",
                border_radius="19px",
                bg="rgba(0,0,0,0.05)",
                margin_bottom="0.5em"
            ),

            # Información del producto
            rx.vstack(
                rx.text(
                    product_data.get("name"),
                    font_weight="bold",
                    font_size="1em",
                    text_align="center",
                    no_of_lines=2,
                ),
                rx.text(
                    product_data.get("formatted_price"),
                    font_weight="600",
                    font_size="0.9em",
                    color=rx.color_mode_cond(
                        light=Custom_theme().light_colors()["primary"],
                        dark=Custom_theme().dark_colors()["secondary"]
                    ),
                    text_align="center"
                ),
                z_index=1,
                spacing="1",
                align="center",
                width="100%"
            ),

            # Controles de cantidad
            plusminus_buttons(product_data.get("id", 1)),  # ✅ CORREGIDO: agregar paréntesis y product_id

            # Botón agregar más pequeño
            rx.button(
                "Agregar",
                size="3",
                width="100%",
                variant="solid",
                border_radius="19px",
                bg=rx.color_mode_cond(
                    light=Custom_theme().light_colors()["primary"],
                    dark=Custom_theme().dark_colors()["primary"]
                ),
                color="white",
                _hover={"opacity": 0.9},
                on_click=CountProducts.add_to_cart(product_data.get("id", 1))
            ),
            spacing="3",
            align="center",
            width="100%"
        ),
        bg=rx.color_mode_cond(
            light=Custom_theme().light_colors()["tertiary"],
            dark=Custom_theme().dark_colors()["tertiary"]
        ),
        border_radius="19px",
        padding="8px",
        min_height="360px",
        width="65vw",
        flex_shrink="0"  # Importante para scroll horizontal
    )


def new_products_card(product_data: Dict) -> rx.Component:
    """
    Tarjeta de producto para la sección "Últimas novedades".
    Principio DRY: hereda propiedades de product_card_horizontal.
    """
    return rx.box(
        # Badge de nuevo
        rx.badge(
            "Nuevo producto",
            color_scheme="green",
            size="2",
            border_radius="12px",
            position="absolute",
            top="6px",
            right="6px",
            z_index="10"
        ),

        # Imagen del producto
        rx.image(
            src="image",
            #src=f"/product_{product_data.get('id', 4)}.jpg",
            height="100%",
            width="100%",
            object_fit="cover",
            border_radius="15px",
            bg="rgba(0,0,0,0.05)",
            margin_bottom="0.5em"
        ),

        # Información del producto
        rx.vstack(
            rx.text(
                product_data.get("name"),
                font_weight="bold",
                font_size="1em",
                text_align="center",
                no_of_lines=2,
            ),
            rx.text(
                product_data.get("formatted_price"),
                font_weight="600",
                font_size="0.9em",
                color=rx.color_mode_cond(
                    light=Custom_theme().light_colors()["primary"],
                    dark=Custom_theme().dark_colors()["secondary"]
                ),
                text_align="center"
            ),
            rx.text(
                f"{product_data.get('pv')} PV",
                font_size="0.9em",
                color="gray",
                text_align="center",
            ),
            spacing="1",
            align="center",
            width="100%"
        ),

        # Controles de cantidad
        plusminus_buttons(product_data.get("id", 1)),

        # Botón agregar
        rx.button(
            rx.icon("shopping-cart", size=18),
            "Agregar",
            size="3",
            width="100%",
            variant="solid",
            border_radius="19px",
            bg=rx.color_mode_cond(
                light=Custom_theme().light_colors()["primary"],
                dark=Custom_theme().dark_colors()["primary"]
            ),
            color="white",
            _hover={"opacity": 0.9},
            on_click=CountProducts.add_to_cart(product_data.get("id", 1))
        ),
        #bg=rx.color_mode_cond(
        #   light=Custom_theme().light_colors()["tertiary"],
        #   dark=Custom_theme().dark_colors()["tertiary"]
        #),
        #border_radius="19px",
        #padding="16px",
        min_height="360px",
        width="50vw",
        flex_shrink="0",
        position="relative"
    )


def most_requested_products_card(product_data: Dict) -> rx.Component:
    """
    Tarjeta de producto para la sección "Productos más pedidos".
    Principio DRY: hereda propiedades de product_card_horizontal.
    """
    return rx.box(
        # Badge de más pedido
        rx.badge(
            "🔥 Popular",
            color_scheme="red",
            size="2",
            border_radius="12px",
            position="absolute",
            top="6px",
            right="6px",
            z_index="10"
        ),

        # Imagen del producto
        rx.image(
            src="image",
            #src=f"/product_{product_data.get('id', 4)}.jpg",
            height="100%",
            width="100%",
            object_fit="cover",
            border_radius="15px",
            bg="rgba(0,0,0,0.05)",
            margin_bottom="0.5em"
        ),

        # Información del producto
        rx.vstack(
            rx.text(
                product_data.get("name"),
                font_weight="bold",
                font_size="1em",
                text_align="center",
                no_of_lines=2,
            ),
            rx.text(
                product_data.get("formatted_price"),
                font_weight="600",
                font_size="0.9em",
                color=rx.color_mode_cond(
                    light=Custom_theme().light_colors()["primary"],
                    dark=Custom_theme().dark_colors()["secondary"]
                ),
                text_align="center"
            ),
            rx.text(
                f"{product_data.get('pv')} PV",
                font_size="0.9em",
                color="gray",
                text_align="center",
            ),
            spacing="1",
            align="center",
            width="100%"
        ),

        # Controles de cantidad
        plusminus_buttons(product_data.get("id", 1)),

        # Botón agregar
        rx.button(
            rx.icon("shopping-cart", size=18),
            "Agregar",
            size="3",
            width="100%",
            variant="solid",
            border_radius="19px",
            bg=rx.color_mode_cond(
                light=Custom_theme().light_colors()["primary"],
                dark=Custom_theme().dark_colors()["primary"]
            ),
            color="white",
            _hover={"opacity": 0.9},
            on_click=CountProducts.add_to_cart(product_data.get("id", 1))
        ),
        #bg=rx.color_mode_cond(
        #    light=Custom_theme().light_colors()["tertiary"],
        #    dark=Custom_theme().dark_colors()["tertiary"]
        #),
        #border_radius="19px",
        #padding="6px",
        min_height="360px",
        width="50vw",
        flex_shrink="0",
        position="relative"
    )


def supplement_products_card(product_data: Dict) -> rx.Component:
    """
    Tarjeta de producto para la sección "Suplementos".
    GRID LAYOUT: Imagen contenida para evitar tamaño excesivo.
    """
    return rx.box(
        # Badge de suplemento
        rx.badge(
            "Suplemento",
            color_scheme="blue",
            size="2",
            border_radius="12px",
            position="absolute",
            top="6px",
            right="6px",
            z_index="10"
        ),

        # Imagen del producto
        rx.image(
            src="image",
            #src=f"/product_{product_data.get('id', 4)}.jpg",
            height="100%",
            width="100%",
            object_fit="cover",
            border_radius="15px",
            bg="rgba(0,0,0,0.05)",
            margin_bottom="0.5em"
        ),

        # Información del producto con PV destacado
        rx.vstack(
            rx.text(
                product_data.get("name"),
                font_weight="bold",
                font_size="1em",
                text_align="center",
                no_of_lines=2,
                height="2.5em" # Altura fija para texto
            ),
            rx.text(
                product_data.get("formatted_price"),
                font_weight="600",
                font_size="1em",
                color=rx.color_mode_cond(
                    light=Custom_theme().light_colors()["primary"],
                    dark=Custom_theme().dark_colors()["secondary"]
                ),
                text_align="center"
            ),
            rx.text(
                f"{product_data.get('pv')} PV",
                font_size="0.9em",
                color="gray",
                text_align="center"
            ),
            spacing="1",
            align="center",
            width="100%"
        ),

        # Controles de cantidad
        plusminus_buttons(product_data.get("id", 1)),

        # Botón agregar
        rx.button(
            rx.icon("shopping-cart", size=18),
            "Agregar",
            size="3",
            width="100%",
            variant="solid",
            border_radius="19px",
            bg=rx.color_mode_cond(
                light=Custom_theme().light_colors()["primary"],
                dark=Custom_theme().dark_colors()["primary"]
            ),
            color="white",
            _hover={"opacity": 0.9},
            on_click=CountProducts.add_to_cart(product_data.get("id", 1))
        ),
        padding="0 0 32px 0",
        height="100%", # Altura completa del grid cell
        width="100%",
        display="flex",
        flex_direction="column",
        position="relative"
    )


def skincare_products_card(product_data: Dict) -> rx.Component:
    """
    Tarjeta de producto para la sección "Cuidado de la piel".
    GRID LAYOUT: Imagen contenida para evitar tamaño excesivo.
    """
    return rx.box(
        # Badge de cuidado de la piel
        rx.badge(
            "Cuidado de la piel",
            color_scheme="violet",
            size="2",
            border_radius="12px",
            position="absolute",
            top="6px",
            right="6px",
            z_index="10"
        ),

        # Imagen del producto
        rx.image(
            src="image",
            #src=f"/product_{product_data.get('id', 4)}.jpg",
            height="100%",
            width="100%",
            object_fit="cover",
            border_radius="15px",
            bg="rgba(0,0,0,0.05)",
            margin_bottom="0.5em"
        ),

        # Información del producto con PV destacado
        rx.vstack(
            rx.text(
                product_data.get("name"),
                font_weight="bold",
                font_size="1em",
                text_align="center",
                no_of_lines=2,
                height="2.5em"
            ),
            rx.text(
                product_data.get("formatted_price"),
                font_weight="600",
                font_size="1em",
                color=rx.color_mode_cond(
                    light=Custom_theme().light_colors()["primary"],
                    dark=Custom_theme().dark_colors()["secondary"]
                ),
                text_align="center"
            ),
            rx.text(
                f"{product_data.get('pv')} PV",
                font_size="0.9em",
                color="gray",
                text_align="center"
            ),
            spacing="1",
            align="center",
            width="100%"
        ),

        # Controles de cantidad
        plusminus_buttons(product_data.get("id", 1)),

        # Botón agregar
        rx.button(
            rx.icon("shopping-cart", size=18),
            "Agregar",
            size="3",
            width="100%",
            variant="solid",
            border_radius="19px",
            bg=rx.color_mode_cond(
                light=Custom_theme().light_colors()["primary"],
                dark=Custom_theme().dark_colors()["primary"]
            ),
            color="white",
            _hover={"opacity": 0.9},
            on_click=CountProducts.add_to_cart(product_data.get("id", 1))
        ),
        padding="0 0 32px 0",
        height="100%", # Altura completa del grid cell
        width="100%",
        display="flex",
        flex_direction="column",
        position="relative"
    )

def sanitized_products_card(product_data: Dict) -> rx.Component:
    """
    Tarjeta de producto para productos desinfectantes.
    GRID LAYOUT: Imagen contenida para evitar tamaño excesivo.
    """
    return rx.box(
        # Badge de desinfectante
        rx.badge(
            "Desinfectante",
            color_scheme="green",
            size="2",
            border_radius="12px",
            position="absolute",
            top="12px",
            right="12px",
            z_index="10"
        ),

        # Imagen del producto - Fixed height container
        rx.box(
            rx.image(
                src="image",
                #src=f"/product_{product_data.get('id', 4)}.jpg",
                height="100%",
                width="100%",
                object_fit="contain",
                border_radius="15px",
                bg="white",
                loading="lazy"
            ),
            height="160px",
            width="100%",
            bg="rgba(0,0,0,0.05)",
            border_radius="15px",
            margin_bottom="0.5em",
            padding="6px",
            overflow="hidden"
        ),

        # Información del producto con PV destacado
        rx.vstack(
            rx.text(
                product_data.get("name"),
                font_weight="bold",
                font_size="1em",
                text_align="center",
                no_of_lines="2",
                height="2.5em"
            ),
            rx.text(
                product_data.get("formatted_price"),
                font_weight="600",
                font_size="1em",
                color=rx.color_mode_cond(
                    light=Custom_theme().light_colors()["primary"],
                    dark=Custom_theme().dark_colors()["secondary"]
                ),
                text_align="center"
            ),
            rx.text(
                f"{product_data.get('pv')} PV",
                font_size="0.9em",
                color="gray",
                text_align="center"
            ),
            spacing="1",
            align="center",
            width="100%"
        ),

        # Controles de cantidad
        plusminus_buttons(product_data.get("id", 1)),

        # Botón agregar
        rx.button(
            rx.icon("shopping-cart", size=18),
            "Agregar",
            size="3",
            width="100%",
            variant="solid",
            border_radius="19px",
            bg=rx.color_mode_cond(
                light=Custom_theme().light_colors()["primary"],
                dark=Custom_theme().dark_colors()["primary"]
            ),
            color="white",
            _hover={"opacity": 0.9},
            on_click=CountProducts.add_to_cart(product_data.get("id", 1))
        ),
        
        bg=rx.color_mode_cond(
            light=Custom_theme().light_colors()["tertiary"],
            dark=Custom_theme().dark_colors()["tertiary"]
        ),
        border_radius="19px",
        padding="8px",
        height="100%",
        width="100%",
        display="flex",
        flex_direction="column",
        justify_content="space-between",
        position="relative"
    )
def product_card_desktop(product_data: Dict) -> rx.Component:
    """
    Tarjeta de producto para la vista de escritorio del grid.
    Adaptada para un diseño limpio y funcional en desktop.
    """
    return rx.vstack(
        # Imagen
        rx.image(
            src="image",
            #src=f"/product_{product_data.get('id', 1)}.png", 
            # Fallback a jpg si es necesario en la logica real, pero aqui simplificamos como el resto
            height="90px", 
            object_fit="contain"
        ),
        
        # Nombre
        rx.text(
            product_data.get("name", "Producto"), 
            font_weight="bold", 
            font_size="1rem",
            text_align="center",
            no_of_lines=2,
            height="3em" # Altura fija para alineacion
        ),
        
        # Precio
        rx.text(
            product_data.get("formatted_price", "/bin/zsh.00"), 
            font_weight="medium", 
            font_size="1rem",
            color=rx.color_mode_cond(
                light=Custom_theme().light_colors()["primary"],
                dark=Custom_theme().dark_colors()["primary"]
            ),
        ),
        
        # PV
        rx.text(
            f"{product_data.get('pv', 0)} PV",
            font_size="0.8rem",
            color="gray",
            text_align="center"
        ),

        # Controles + -
        rx.hstack(
            rx.button(
                "-", 
                width="28px", 
                height="28px", 
                border_radius="50%", 
                bg=rx.color_mode_cond(light="#f0f0f0", dark="rgba(255,255,255,0.1)"),
                color=rx.color_mode_cond(light="black", dark="white"),
                on_click=CountProducts.decrement(product_data.get("id", 1))
            ),
            rx.text(
                CountProducts.get_count_reactive.get(str(product_data.get("id", 1)), 0),
                font_size="1rem", 
                margin_x="0.5em"
            ),
            rx.button(
                "+", 
                width="28px", 
                height="28px", 
                border_radius="50%", 
                bg=rx.color_mode_cond(light="#f0f0f0", dark="rgba(255,255,255,0.1)"),
                color=rx.color_mode_cond(light="black", dark="white"),
                on_click=CountProducts.increment(product_data.get("id", 1))
            ),
            padding_y="8px",
            align="center",
            justify="center"
        ),
        
        # Botón Agregar
        rx.button(
            "Agregar al carrito", 
            bg=rx.color_mode_cond(
                light="#0039F2", 
                dark=Custom_theme().dark_colors()["primary"]
            ), 
            color="white", 
            border_radius="14px", 
            margin_top="0.6em",
            width="100%",
            on_click=CountProducts.add_to_cart(product_data.get("id", 1))
        ),
        
        margin="10px",
        spacing="2",
        align="center",
        justify="between",
        width="100%", 
        height="100%",
        #padding="16px",
    )
