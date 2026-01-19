"""Nueva Backoffice NN Protect | Nuevo registro"""

import reflex as rx
from NNProtect_new_website.components.shared_ui.theme import Custom_theme
from rxconfig import config
from NNProtect_new_website.components.shared_ui.layout import main_container_derecha, mobile_header, desktop_sidebar, mobile_sidebar

def network() -> rx.Component:
    # Welcome Page (Index)
    return rx.center(
        rx.desktop_only(
            rx.vstack(
                rx.hstack(
                    desktop_sidebar(),
                    # Container de la derecha. Contiene el formulario de registro.
                    main_container_derecha(
                        rx.vstack(
                            # Encabezado de la página
                            rx.text(
                                "Red de negocio",
                                font_size="2rem",
                                font_weight="bold",
                                margin_bottom="0.5em"
                            ),
                            # Contenedor de la red
                            rx.box(
                                rx.html(
                                    '<iframe src="/red.html" width="100%" height="552px" style="border:none;"></iframe>'
                                ),
                                bg=rx.color_mode_cond(
                                    light=Custom_theme().light_colors()["tertiary"],
                                    dark=Custom_theme().dark_colors()["tertiary"]
                                ),
                                border_radius="24px",
                                margin_bottom="32px",
                                padding="32px",
                                min_width="240px",
                                width="100%",
                            ),
                            # Propiedades @Main container de la derecha
                            width="100%",
                        ),
                    )
                ),
                # Propiedades vstack que contiene el contenido de la página.
                justify="center",
                margin_top="120px",
                margin_bottom="2em",
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
                    # Visualización de red móvil
                    rx.box(
                        rx.html(
                            '<iframe src="/red.html" width="100%" height="400px" style="border:none;"></iframe>'
                        ),
                        bg=rx.color_mode_cond(
                            light=Custom_theme().light_colors()["tertiary"],
                            dark=Custom_theme().dark_colors()["tertiary"]
                        ),
                        border_radius="16px",
                        padding="1rem",
                        width="100%",
                        margin_bottom="1rem"
                    ),
                    
                    # Información adicional móvil
                    rx.vstack(
                        rx.text(
                            "Visualización de Red",
                            font_size="1.2rem",
                            font_weight="bold",
                            color=rx.color_mode_cond(
                                light=Custom_theme().light_colors()["primary"],
                                dark=Custom_theme().dark_colors()["primary"]
                            )
                        ),
                        rx.text(
                            "Aquí puedes ver la estructura completa de tu red de negocio, incluyendo todos los miembros y sus conexiones.",
                            font_size="0.9rem",
                            text_align="center",
                            color=rx.color_mode_cond(
                                light=Custom_theme().light_colors()["text"],
                                dark=Custom_theme().dark_colors()["text"]
                            )
                        ),
                        spacing="2",
                        width="100%"
                    ),
                    
                    spacing="4",
                    width="100%",
                    padding="1rem",
                    margin_top="80px"  # Espacio para el header fijo
                ),
                
                width="100%",
                height="100vh"
            )
        ),
        
        # Propiedades del contenedor principal.
        bg=rx.color_mode_cond(
            light=Custom_theme().light_colors()["background"],
            dark=Custom_theme().dark_colors()["background"]
        ),
        position="absolute",
        width="100%",
    )