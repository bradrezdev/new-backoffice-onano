import reflex as rx

from ..state.auth_state import AuthState

from ....components.shared_ui.theme import Custom_theme
from ....components.shared_ui.layout import main_container_derecha, mobile_header, desktop_sidebar, mobile_sidebar, header


def welcome_page() -> rx.Component:
        return rx.center(
                rx.mobile_only(
                # Habrá un header móvil si el usuario ya está autenticado
                    rx.cond(
                        AuthState.profile_data.get("member_id"),
                        mobile_header(),
                    ),
                    rx.cond(
                        AuthState.profile_data.get("member_id"),
                        rx.box(margin_bottom="80px"),
                        rx.box(margin_bottom="1em"),
                    ),
                    rx.vstack(
                        rx.vstack(
                            rx.heading("¡Bienvenido a NN Protect!", size="8"),
                            rx.cond(
                                AuthState.profile_data.get("member_id"),
                                rx.text(
                                    "Gracias por registrar a un nuevo miembro en nuestra familia NN Protect.",
                                ),
                                rx.text(
                                    "Muchas gracias por unirte a nuestra familia NN Protect. Estamos encantados de tenerte con nosotros.",
                                    size="4",
                                ),
                            ),
                            margin_bottom="3em",
                        ),
                        rx.cond(
                                AuthState.profile_data.get("member_id"),
                                rx.link(
                                        rx.button(
                                            "Ver reporte de usuarios",
                                            bg=rx.color_mode_cond(
                                                    light=Custom_theme().light_colors()["primary"],
                                                    dark=Custom_theme().dark_colors()["primary"],
                                            ),
                                            width="100%",
                                            size="4",
                                            border_radius="30px",
                                        ),
                                        href="/network_reports",
                                ),
                                rx.link(
                                        rx.button(
                                            "Iniciar sesión",
                                            bg=rx.color_mode_cond(
                                                    light=Custom_theme().light_colors()["primary"],
                                                    dark=Custom_theme().dark_colors()["primary"],
                                            ),
                                            width="100%",
                                            size="4",
                                            border_radius="30px",
                                        ),
                                        href="/",
                                        width="100%",
                                ),
                        ),
                        padding="0 1em",
                    ),
                ),
            bg=rx.color_mode_cond(
                light=Custom_theme().light_colors()["background"],
                dark=Custom_theme().dark_colors()["background"],
            ),
            position="absolute",
            width="100%",
            height="100vh",
        )