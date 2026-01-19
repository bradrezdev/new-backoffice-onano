"""Proyecto Final | Programación Avanzada | Log in Page"""

import reflex as rx
from rxconfig import config
#from ..state import Login
from ....components.shared_ui.theme import Custom_theme
from ..state.auth_state import AuthState

def login() -> rx.Component:
    # Contenedor principal
    return rx.box(
        # Versión escritorio
        rx.desktop_only(
            rx.flex(
                
                # Contenedor izquierdo | Formulario
                rx.vstack(
                    
                    rx.image(src="/logotipo.png", width="200px", height="200px"),

                    # Formulario de inicio de sesión
                    rx.form(
                        
                        # Inputs del formulario
                        rx.vstack(

                            rx.heading("Bienvenido de vuelta", size="8"),

                            rx.text("Qué gusto volverte a ver. Por favor, ingresa los datos de tu cuenta:"),
                            
                            rx.spacer(),

                            rx.text("Nombre de usuario"),
                            rx.input(
                                placeholder="Escribe tu nombre de usuario",
                                type="text",
                                value=AuthState.username,
                                on_change=AuthState.set_username,
                                required=True,
                                style={"border": "1px solid black"},
                                border_color=rx.color_mode_cond(
                                    light=Custom_theme().light_colors()["primary"],
                                    dark=Custom_theme().dark_colors()["primary"]
                                ),
                                border_radius="8px",
                                height="40px",
                                width="25vw",
                            ),

                            rx.text("Contraseña"),
                            rx.input(
                                placeholder="Escribe tu contraseña",
                                type="password",
                                value=AuthState.password,
                                on_change=AuthState.set_password,
                                required=True,
                                style={"border": "1px solid black"},
                                border_color=rx.color_mode_cond(
                                    light=Custom_theme().light_colors()["primary"],
                                    dark=Custom_theme().dark_colors()["primary"]
                                ),
                                border_radius="8px",
                                height="40px",
                                width="25vw",
                            ),

                            rx.link("Olvidé mi contraseña", href="/reset-password", color=rx.color_mode_cond(
                                light=Custom_theme().light_colors()["primary"],
                                dark=Custom_theme().dark_colors()["primary"]
                            ), size="1"),

                            rx.button(
                                rx.text("Iniciar sesión"),
                                height="47px",
                                width="25vw",
                                type="submit",
                                bg=rx.color_mode_cond(
                                    light=Custom_theme().light_colors()["primary"],
                                    dark=Custom_theme().dark_colors()["primary"]
                                ),
                                border_radius="8px",
                                loading=AuthState.is_loading,
                            ),
                        ),

                        # Propiedades del formulario
                        on_submit=AuthState.login_user,
                        padding="20%",
                        width="100%",
                    ),

                    # Propiedades del contenedor izquierdo
                    justify="center",
                    padding="4%",
                    width="50%",
                ),

                # Contenedor derecho | Imagen
                rx.center(
                    rx.image(src="/image_login.png", width="80%", height="auto", align="center"),
                    width="50%",
                ),

                # Propiedades contenedor principal
                height="100vh",
                max_width="1920",
                width="100%",
            )
        ),
        
        # Versión móvil
        rx.mobile_only(
            rx.center(
                rx.vstack(
                    # Logo centrado
                    rx.center(
                        rx.image(src="/logo_login.svg", width="75%", height="auto"),
                        width="100%",
                        top="0",
                    ),
                    
                    # Formulario móvil
                    rx.form(
                        rx.vstack(
                            rx.heading("Bienvenido de nuevo", size="6"),
                            
                            rx.text(
                                "Por favor, ingresa los datos de tu cuenta para iniciar sesión:",
                                font_size="0.9rem",
                                margin_bottom="1rem"
                            ),
                            
                            rx.input(
                                placeholder="Escribe tu correo electrónico",
                                type="text",
                                value=AuthState.email,
                                on_change=AuthState.set_email,
                                required=True,
                                border_color=rx.color_mode_cond(
                                    light=Custom_theme().light_colors()["primary"],
                                    dark=Custom_theme().dark_colors()["primary"]
                                ),
                                border_radius="15px",
                                height="45px",
                                width="100%",
                                font_size="16px",
                            ),

                            rx.input(
                                placeholder="Escribe tu contraseña",
                                type="password",
                                value=AuthState.password,
                                on_change=AuthState.set_password,
                                required=True,
                                border_color=rx.color_mode_cond(
                                    light=Custom_theme().light_colors()["primary"],
                                    dark=Custom_theme().dark_colors()["primary"]
                                ),
                                border_radius="15px",
                                height="45px",
                                width="100%",
                                font_size="16px",
                                #margin_bottom="0.5rem"
                            ),
                            
                            rx.link(
                                "¿Olvidaste tu contraseña?", 
                                href="/reset-password",
                                color=rx.color_mode_cond(
                                    light=Custom_theme().light_colors()["primary"],
                                    dark=Custom_theme().dark_colors()["primary"]
                                ), 
                                size="2",
                                #text_align="center",
                                width="100%",
                                margin_bottom="2.5em"
                            ),
                            
                            rx.button(
                                "Iniciar sesión",
                                bg=rx.color_mode_cond(
                                    light=Custom_theme().light_colors()["primary"],
                                    dark=Custom_theme().dark_colors()["primary"]
                                ),
                                color="white",
                                size="4",
                                border_radius="15px",
                                padding="16px",
                                width="100%",
                                _hover={"opacity": 0.9, "transform": "translateY(-1px)"},
                                transition="all 0.2s ease",
                                loading=AuthState.is_loading,
                            ),
                            
                            spacing="3",
                            width="100%"
                        ),
                        on_submit=AuthState.login_user,
                        width="100%",
                        padding="1rem"
                    ),
                    width="100%",
                    padding="0 1em"
                ),
                height="100vh",
                bg=rx.color_mode_cond(
                    light=Custom_theme().light_colors()["background"],
                    dark=Custom_theme().dark_colors()["background"]
                )
            )
        ),
        
        width="100%",
        height="100vh"
    )