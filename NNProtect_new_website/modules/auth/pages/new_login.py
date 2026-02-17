"""Proyecto Final | Programación Avanzada | Log in Page"""

import reflex as rx
from rxconfig import config

# Imports de componentes y estado
from ....components.inputs import Input
from ..components.login_button import login_button
from ....components.shared_ui.fonts import FontStyle
from ....components.shared_ui.theme import Custom_theme
from ..state.auth_state import AuthState

def new_login() -> rx.Component:
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

                            Input.user(
                                value=AuthState.username,
                                on_change=AuthState.set_username,
                                width="25vw",
                                height="40px",
                                style={"border": "1px solid black"},
                                border_color=rx.color_mode_cond(
                                    light=Custom_theme().light_colors()["primary"],
                                    dark=Custom_theme().dark_colors()["primary"]
                                ),
                            ),

                            Input.password(
                                value=AuthState.password,
                                on_change=AuthState.set_password,
                                width="25vw",
                                height="40px",
                                style={"border": "1px solid black"},
                                border_color=rx.color_mode_cond(
                                    light=Custom_theme().light_colors()["primary"],
                                    dark=Custom_theme().dark_colors()["primary"]
                                ),
                            ),

                            rx.link("Olvidé mi contraseña", href="/reset-password", color=rx.color_mode_cond(
                                light=Custom_theme().light_colors()["primary"],
                                dark=Custom_theme().dark_colors()["primary"]
                            ), size="1"),

                            login_button(),
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
                            rx.text("Bienvenido de nuevo", **FontStyle.TITLE),
                            
                            rx.text(
                                "Por favor, ingresa los datos de tu cuenta para iniciar sesión:", **FontStyle.COMPACT_BODY,
                                margin_bottom="1rem"
                            ),
                            
                            rx.flex(
                                Input.email(AuthState.email, AuthState.set_email),
                                Input.password(AuthState.password, AuthState.set_password),
                                bg=rx.color_mode_cond(
                                    light="#ffffff",
                                ),
                                border_radius="24px",
                                direction="column",
                                padding="8px 16px",
                                spacing="1",
                                width="100%",
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
                            
                            login_button(),
                            
                            spacing="3",
                            width="100%"
                        ),
                        on_submit=AuthState.login_user,
                        width="100%",
                    ),
                    width="100%",
                    padding="0 1em"
                ),
                height="100dvh",
                bg=rx.color_mode_cond(
                    light=Custom_theme().light_colors()["background"],
                    dark=Custom_theme().dark_colors()["background"]
                )
            )
        ),
        width="100%",
        height="100vh"
    )