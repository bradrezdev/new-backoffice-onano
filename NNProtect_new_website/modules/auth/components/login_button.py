"""Botón Iniciar sesión | Componente"""

import reflex as rx

from ....components.inputs import Input
from ....components.shared_ui.fonts import FontStyle
from ..state.auth_state import AuthState

def login_button() -> rx.Component:
    # Botón de inicio de sesión
    return rx.button(
            rx.text("Iniciar sesión", **FontStyle.CTA),
            height="64px",
            width="100%",
            type="submit",
            bg=rx.color_mode_cond(
                light="#062A63",
            ),
            border_radius="32px",
            loading=AuthState.is_loading,
        )