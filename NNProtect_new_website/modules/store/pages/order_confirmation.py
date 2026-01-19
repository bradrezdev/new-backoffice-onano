import reflex as rx

from ...auth.auth_state import AuthState

from ....components.shared_ui.theme import Custom_theme
from ....components.shared_ui.layout import main_container_derecha, mobile_header, desktop_sidebar, header


def order_confirmation() -> rx.Component:
        return rx.center(
                rx.mobile_only(
                    rx.vstack(
                        rx.vstack(
                            rx.heading("¡Muchas gracias por tu compra!", size="8"),
                            rx.text(
                                "Tu orden ha sido procesada exitosamente. Puedes revisar los detalles de tu compra en tu perfil.\n\nTe agradecemos por confiar en NN Protect para tu salud.",
                            ),
                            margin_bottom="3em",
                        ),
                            rx.link(
                                    rx.button(
                                        "Ver mis órdenes",
                                        bg=rx.color_mode_cond(
                                                light=Custom_theme().light_colors()["primary"],
                                                dark=Custom_theme().dark_colors()["primary"],
                                        ),
                                        width="100%",
                                        size="4",
                                        border_radius="30px",
                                    ),
                                    href="/orders",
                                    width="100%",
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