import reflex as rx
from typing import Any, Optional

# Import de fonts y estilos compartidos
from .shared_ui.fonts import FontStyle
from .shared_ui.theme import Custom_theme

def only_email_input(value: str, on_change: Any, **props):
    input_props = {
        "placeholder": "personal@email.com",
        "type": "email",
        "required": True,
        "border_radius": "24px",
        "bg": rx.color_mode_cond(light="#ffffff"),
        "variant": "soft",
        "width": "193px",
        **FontStyle.BODY,
    }
    input_props.update(props)

    return rx.flex(
        rx.text(
            "Correo electrónico:",
            **FontStyle.BODY,
            width="145px"
            ),
        rx.input(
            value=value,
            on_change=on_change,
            **input_props
        ),
        bg=rx.color_mode_cond(
            light="#ffffff",
        ),
        align="center",
        border_radius="24px",
        padding="8px 16px",
    )

class Input:
    @staticmethod
    def email(value: str, on_change: Any, **props):
        input_props = {
            "placeholder": "personal@email.com",
            "type": "email",
            "required": True,
            "border_radius": "24px",
            "bg": rx.color_mode_cond(light="#ffffff"),
            "variant": "soft",
            "width": "193px",
            **FontStyle.BODY,
        }
        input_props.update(props)

        return rx.flex(
            rx.text(
                "Correo electrónico:",
                **FontStyle.BODY,
                margin_right="8px",
                width="145px"
            ),
            rx.input(
                value=value,
                on_change=on_change,
                **input_props
            ),
            align="center",
        )

    @staticmethod
    def password(value: str, on_change: Any, **props):
        input_props = {
            "placeholder": "********",
            "type": "password",
            "required": True,
            "border_radius": "24px",
            "bg": rx.color_mode_cond(light="#ffffff"),
            "variant": "soft",
            "width": "246px",
            **FontStyle.BODY,
        }
        input_props.update(props)

        return rx.flex(
            rx.text(
                "Contraseña:",
                **FontStyle.BODY,
                margin_right="8px",
                width="92px"
            ),
            rx.input(
                value=value,
                on_change=on_change,
                **input_props
            ),
            align="center",
        )

    @staticmethod
    def confirm_password(value: str, on_change: Any, **props):
        input_props = {
            "placeholder": "********",
            "type": "password",
            "required": True,
            "border_radius": "24px",
            "bg": rx.color_mode_cond(light="#ffffff"),
            "variant": "soft",
            "width": "173px",
            **FontStyle.BODY,
        }
        input_props.update(props)

        return rx.flex(
            rx.text(
                "Confirmar contraseña:",
                **FontStyle.BODY,
                margin_right="8px",
                width="169px"
            ),
            rx.input(
                value=value,
                on_change=on_change,
                **input_props
            ),
            align="center",
        )

    @staticmethod
    def names(value: str, on_change: Any, **props):
        input_props = {
            "placeholder": "Logan Gael",
            "type": "text",
            "required": True,
            "border_radius": "24px",
            "bg": rx.color_mode_cond(light="#ffffff"),
            "variant": "soft",
            "width": "257px",
            **FontStyle.BODY,
        }
        input_props.update(props)

        return rx.flex(
            rx.text(
                "Nombre(s):",
                **FontStyle.BODY,
                margin_right="8px",
                width="85px"
            ),
            rx.input(
                value=value,
                on_change=on_change,
                **input_props
            ),
            align="center",
        )

    @staticmethod
    def lastname(value: str, on_change: Any, **props):
        input_props = {
            "placeholder": "Nùñez Pérez",
            "type": "text",
            "required": True,
            "border_radius": "24px",
            "bg": rx.color_mode_cond(light="#ffffff"),
            "variant": "soft",
            "width": "256px",
            **FontStyle.BODY,
        }
        input_props.update(props)

        return rx.flex(
            rx.text(
                "Apellido(s):",
                **FontStyle.BODY,
                margin_right="8px",
                width="86px"
            ),
        rx.input(
            value=value,
            on_change=on_change,
            **input_props
        ),
        align="center",
    )

    @staticmethod
    def gender(value: str, on_change: Any, **props):
        # Extract width from props if present to avoid conflict if passed to root, 
        # but here we want to likely control the trigger width if user specifies width.
        # Actually, for Select, width usually applies to the Trigger or the Root acting as container.
        # Let's check original code: Trigger had width="272px". Root had **props.
        # If user passes width="100%" to Input.gender, it goes to Root.
        # Trigger keeps "272px". This might look weird (container wide, trigger fixed).
        # Assuming we want the trigger to adapt to the passed width if provided.
        
        trigger_props = {
            "placeholder": "Selecciona tu género",
            "width": "272px",
            "border_radius": "24px",
            "variant": "soft",
            "bg": rx.color_mode_cond(light="#ffffff"),
            **FontStyle.BODY,
        }
        
        # If width is in props, use it for trigger too, or let it cascade?
        # Reflex Select Root handles open state. Trigger handles visual.
        # If width passed to root, root takes space. Trigger might need width="100%" to fill root.
        # Let's apply width to trigger if passed, and remove from props passed to root to avoid issues 
        # (though Select.Root might not complain about width, but it's cleaner).
        
        if "width" in props:
            trigger_props["width"] = props["width"]
            # We keep it in props for Root as well, or remove? 
            # Usually Root is just logic context, but can be styled.
            # Let's leave it in props for Root if it was there, assuming Root is a Box/Flex. 
            # Wait, Select.Root is often a fragment or minimal wrapper in some libraries, but in Radix/Reflex it wraps.
            # Safe bet: Update trigger width.
            
        return rx.flex(
            rx.text(
                "Género:",
                **FontStyle.BODY,
                margin_right="8px",
                width="58px"
            ),
        rx.select.root(
            rx.select.trigger(
                **trigger_props
            ),
            rx.select.content(
                rx.select.group(
                    rx.select.item(
                        "Masculino",
                        value="male",
                        ),
                    rx.select.item(
                        "Femenino",
                        value="female",
                        ),
                    rx.select.item(
                        "Prefiero no decirlo",
                        value="other",
                        ),
                ),
            ),
            value=value,
            on_change=on_change,
            required=True,
            **props
        ),
        align="center",
    )

    @staticmethod
    def cellphone(value: str, on_change: Any, **props):
        input_props = {
            "placeholder": "+52 2345678901",
            "type": "tel",
            "required": True,
            "border_radius": "24px",
            "bg": rx.color_mode_cond(light="#ffffff"),
            "variant": "soft",
            "width": "284px",
            **FontStyle.BODY,
        }
        input_props.update(props)

        return rx.flex(
            rx.text(
                "Celular:",
                **FontStyle.BODY,
                margin_right="8px",
                width="58px"
            ),
        rx.input(
            value=value,
            on_change=on_change,
            **input_props
        ),
        align="center",
    )

    @staticmethod
    def country(value: str, on_change: Any, **props):
        input_props = {
            "placeholder": "México",
            "type": "text",
            "required": True,
            "border_radius": "24px",
            "bg": rx.color_mode_cond(light="#ffffff"),
            "variant": "soft",
            "width": "306px",
            **FontStyle.BODY,
        }
        input_props.update(props)

        return rx.flex(
            rx.text(
                "País:",
                **FontStyle.BODY,
                margin_right="8px",
                width="37px"
            ),
        rx.input(
            value=value,
            on_change=on_change,
            **input_props
        ),
        align="center",
    )

    @staticmethod
    def user(value: str, on_change: Any, **props):
        input_props = {
            "placeholder": "logan_nunez",
            "type": "text",
            "required": True,
            "border_radius": "24px",
            "bg": rx.color_mode_cond(light="#ffffff"),
            "variant": "soft",
            "width": "246px",
            **FontStyle.BODY,
        }
        input_props.update(props)

        return rx.flex(
            rx.text(
                "Usuario:",
                **FontStyle.BODY,
                width="92px"
            ),
        rx.input(
            value=value,
            on_change=on_change,
            **input_props
        ),
        align="center",
    )

    @staticmethod
    def user_button(value: str, on_change: Any, on_click_suggest: Any = None, **props):
        input_props = {
            "placeholder": "logan_nunez",
            "type": "text",
            "required": True,
            "border_radius": "24px",
            "bg": rx.color_mode_cond(light="#ffffff"),
            "variant": "soft",
            "margin_right": "8px",
            "width": "131px",
            **FontStyle.BODY,
        }
        input_props.update(props)

        return rx.flex(
            rx.text(
                "Usuario:",
                **FontStyle.BODY,
                margin_right="8px",
                width="63px"
            ),
        rx.input(
            value=value,
            on_change=on_change,
            **input_props
        ),
        rx.button(
            "Sugerir usuario",
            on_click=on_click_suggest,
            bg=rx.color_mode_cond(
                light="#355078",
            ),
            border_radius="24px",
            color="white",
            height="40px",
            width="140px",
            **FontStyle.BODY,
        ),
        align="center",
    )