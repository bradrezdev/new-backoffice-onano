"""Nueva Backoffice NN Protect | Nuevo registro"""

import reflex as rx
import random

from ....components.shared_ui.theme import Custom_theme
from rxconfig import config
from ....components.shared_ui.layout import main_container_derecha, mobile_header, desktop_sidebar, mobile_sidebar, header

from ..state.auth_state import AuthState
# Countries manejado directamente por RegistrationManager

def register() -> rx.Component:
    # Welcome Page (Index)
    return rx.center(
        rx.desktop_only(
            rx.vstack(
                header(),  # Muestra el usuario logueado en la esquina superior derecha
                rx.hstack(
                    desktop_sidebar(),
                    # Container de la derecha. Contiene el formulario de registro.
                    main_container_derecha(
                        rx.vstack(
                            rx.text(
                                "Nuevo registro referido por Bryan Núñez",
                                font_size="2rem",  # --- Propiedades rx.text ---
                                font_weight="bold",
                                margin_bottom="0.5em"
                            ),
                            rx.hstack(
                                # --------- Información de contacto (Columna Izquierda) ---------
                                rx.vstack(
                                    rx.text(
                                        "Información de contacto",
                                        font_size="1.25rem",
                                        font_weight="bold",
                                        margin_bottom="0.5em"
                                    ),
                                    rx.text("Nombre(s)*", font_weight="medium"),
                                    rx.input(
                                        placeholder="Escribe tu(s) nombre(s)...",
                                        value=AuthState.new_user_firstname,
                                        on_change=AuthState.set_new_firstname,
                                        border_radius="12px",
                                        bg=rx.color_mode_cond(
                                            light=Custom_theme().light_colors()["tertiary"],
                                            dark=Custom_theme().dark_colors()["tertiary"]
                                        ),
                                        height="40px",
                                        width="100%",
                                    ),
                                    rx.text("Apellido(s)*", font_weight="medium"),
                                    rx.input(
                                        placeholder="Escribe tu(s) apellido(s)...",
                                        value=AuthState.new_user_lastname,
                                        on_change=AuthState.set_new_lastname,
                                        border_radius="12px",
                                        bg=rx.color_mode_cond(
                                            light=Custom_theme().light_colors()["tertiary"],
                                            dark=Custom_theme().dark_colors()["tertiary"]
                                        ),
                                        height="40px",
                                        width="100%",
                                    ),
                                    rx.text("Sexo*", font_weight="medium"),
                                    rx.select(
                                        ["Masculino", "Femenino"],
                                        placeholder="Seleccionar una opción",
                                        value=AuthState.new_gender,
                                        on_change=AuthState.set_new_gender,
                                        border_radius="12px",
                                        bg=rx.color_mode_cond(
                                            light=Custom_theme().light_colors()["tertiary"],
                                            dark=Custom_theme().dark_colors()["tertiary"]
                                        ),
                                        radius="large",
                                        size="3",
                                        width="100%",
                                    ),
                                    rx.text("Calle y número*", font_weight="medium"),
                                    rx.input(
                                        placeholder="Ejemplo: Av. Siempre Viva #742",
                                        value=AuthState.new_street_number,
                                        on_change=AuthState.set_new_street_number,
                                        border_radius="12px",
                                        bg=rx.color_mode_cond(
                                            light=Custom_theme().light_colors()["tertiary"],
                                            dark=Custom_theme().dark_colors()["tertiary"]
                                        ),
                                        height="40px",
                                        width="100%",
                                    ),
                                    rx.text("Colonia*", font_weight="medium"),
                                    rx.input(
                                        placeholder="Ejemplo: Centro",
                                        value=AuthState.new_neighborhood,
                                        on_change=AuthState.set_new_neighborhood,
                                        border_radius="12px",
                                        bg=rx.color_mode_cond(
                                            light=Custom_theme().light_colors()["tertiary"],
                                            dark=Custom_theme().dark_colors()["tertiary"]
                                        ),
                                        height="40px",
                                        width="100%",
                                    ),
                                    rx.text("Ciudad*", font_weight="medium"),
                                    rx.input(
                                        placeholder="Ejemplo: Colima",
                                        value=AuthState.new_city,
                                        on_change=AuthState.set_new_city,
                                        border_radius="12px",
                                        bg=rx.color_mode_cond(
                                            light=Custom_theme().light_colors()["tertiary"],
                                            dark=Custom_theme().dark_colors()["tertiary"]
                                        ),
                                        height="40px",
                                        width="100%",
                                    ),
                                    rx.text("País*", font_weight="medium"),
                                    rx.select(
                                        AuthState.country_options,
                                        placeholder="Seleccionar país",
                                        value=AuthState.new_country,
                                        on_change=AuthState.set_new_country,
                                        border_radius="14px",
                                        bg=rx.color_mode_cond(
                                            light=Custom_theme().light_colors()["tertiary"],
                                            dark=Custom_theme().dark_colors()["tertiary"]
                                        ),
                                        size="3",
                                        height="40px",
                                        width="100%",
                                    ),
                                    rx.text("Estado*", font_weight="medium"),
                                    rx.select(
                                        AuthState.state_options,
                                        placeholder="Seleccionar estado",
                                        value=AuthState.new_state,
                                        on_change=AuthState.set_new_state,
                                        disabled=(AuthState.new_country == ""),
                                        border_radius="14px",
                                        bg=rx.color_mode_cond(
                                            light=Custom_theme().light_colors()["tertiary"],
                                            dark=Custom_theme().dark_colors()["tertiary"]
                                        ),
                                        height="40px",
                                        width="100%",
                                    ),
                                    rx.text("Código postal*", font_weight="medium"),
                                    rx.input(
                                        placeholder="Ejemplo: 28000",
                                        value=AuthState.new_zip_code,
                                        on_change=AuthState.set_new_zip_code,
                                        type="tel",
                                        input_mode="numeric",
                                        pattern="[0-9]*",
                                        border_radius="14px",
                                        bg=rx.color_mode_cond(
                                            light=Custom_theme().light_colors()["tertiary"],
                                            dark=Custom_theme().dark_colors()["tertiary"]
                                        ),
                                        height="40px",
                                        width="100%",
                                    ),
                                    rx.text("Celular*", font_weight="medium"),
                                    rx.input(
                                        placeholder="Ejemplo: 3121234567",
                                        value=AuthState.new_phone_number,
                                        on_change=AuthState.set_new_phone_number,
                                        type="tel",
                                        input_mode="numeric",
                                        pattern="[0-9]*",
                                        border_radius="12px",
                                        bg=rx.color_mode_cond(
                                            light=Custom_theme().light_colors()["tertiary"],
                                            dark=Custom_theme().dark_colors()["tertiary"]
                                        ),
                                        height="40px",
                                        width="100%",
                                    ),
                                    spacing="3",
                                    width="48%",
                                ),
                                # --------- Acceso al sistema (Columna Derecha) ---------
                                rx.vstack(
                                    rx.text(
                                        "Acceso al sistema",
                                        font_size="1.25rem",
                                        font_weight="bold",
                                        margin_bottom="0.5em"
                                    ),
                                    rx.text("Usuario*", font_weight="medium"),
                                    rx.input(
                                        placeholder="Usuario único",
                                        value=AuthState.new_username,
                                        on_change=AuthState.set_new_username,
                                        border_radius="12px",
                                        bg=rx.color_mode_cond(
                                            light=Custom_theme().light_colors()["tertiary"],
                                            dark=Custom_theme().dark_colors()["tertiary"]
                                        ),
                                        height="40px",
                                        width="100%",
                                        font_size="16px",
                                    ),
                                    rx.text("Correo electrónico*", font_weight="medium"),
                                    rx.input(
                                        type="email",
                                        placeholder="Correo electrónico",
                                        value=AuthState.new_email,
                                        on_change=AuthState.set_new_email,
                                        border_radius="12px",
                                        bg=rx.color_mode_cond(
                                            light=Custom_theme().light_colors()["tertiary"],
                                            dark=Custom_theme().dark_colors()["tertiary"]
                                        ),
                                        height="40px",
                                        width="100%",
                                        font_size="16px",
                                    ),
                                    rx.input(
                                        type="password",
                                        placeholder="Crea una contraseña",
                                        value=AuthState.new_password,  # ✅ Cambiar
                                        on_change=AuthState.set_new_password,  # ✅ Cambiar
                                        border_radius="12px",
                                        bg=rx.color_mode_cond(
                                            light=Custom_theme().light_colors()["tertiary"],
                                            dark=Custom_theme().dark_colors()["tertiary"]
                                        ),
                                        height="40px",
                                        width="100%",
                                        font_size="16px",
                                    ),
                                    rx.input(
                                        type="password",
                                        placeholder="Confirmar contraseña",
                                        value=AuthState.new_confirmed_password,  # ✅ Cambiar
                                        on_change=AuthState.set_new_confirmed_password,  # ✅ Cambiar
                                        border_radius="12px",
                                        bg=rx.color_mode_cond(
                                            light=Custom_theme().light_colors()["tertiary"],
                                            dark=Custom_theme().dark_colors()["tertiary"]
                                        ),
                                        height="40px",
                                        width="100%",
                                        font_size="16px",
                                    ),

                                    # Continuar con todos los demás campos usando new_...
                                    rx.text("Nombres*", font_weight="medium"),
                                    rx.input(
                                        placeholder="Nombres completos",
                                        value=AuthState.new_user_firstname,
                                        on_change=AuthState.set_new_firstname,
                                        border_radius="12px",
                                        bg=rx.color_mode_cond(
                                            light=Custom_theme().light_colors()["tertiary"],
                                            dark=Custom_theme().dark_colors()["tertiary"]
                                        ),
                                        height="40px",
                                        width="100%",
                                        font_size="16px",
                                    ),
                                    rx.text("Apellidos*", font_weight="medium"),
                                    rx.input(
                                        placeholder="Apellidos completos",
                                        value=AuthState.new_user_lastname,
                                        on_change=AuthState.set_new_lastname,
                                        border_radius="12px",
                                        bg=rx.color_mode_cond(
                                            light=Custom_theme().light_colors()["tertiary"],
                                            dark=Custom_theme().dark_colors()["tertiary"]
                                        ),
                                        height="40px",
                                        width="100%",
                                        font_size="16px",
                                    ),

                                    # Continuar actualizando TODOS los campos en la versión móvil también...
                                    rx.text("Información Personal", font_weight="bold", font_size="1.1em", margin_bottom="0.5em"),
                                    
                                    rx.text(
                                        "Nombre(s)*",
                                        font_weight="medium",
                                        font_size="1em",
                                        ),
                                    rx.input(
                                        placeholder="Escribe tu(s) nombre(s)...",
                                        value=AuthState.new_user_firstname,
                                        on_change=AuthState.set_new_firstname,
                                        required=True,
                                        reset_on_submit=True,
                                        border_radius="15px",
                                        bg=rx.color_mode_cond(
                                            light=Custom_theme().light_colors()["tertiary"],
                                            dark=Custom_theme().dark_colors()["tertiary"]
                                        ),
                                        height="48px",
                                        width="100%",
                                        font_size="1em",
                                    ),

                                    rx.text(
                                        "Apellido(s)*",
                                        font_weight="medium",
                                        font_size="1em",
                                        ),
                                    rx.input(
                                        placeholder="Escribe tu(s) apellido(s)...",
                                        value=AuthState.new_user_lastname,
                                        on_change=AuthState.set_new_lastname,
                                        required=True,
                                        reset_on_submit=True,
                                        border_radius="15px",
                                        bg=rx.color_mode_cond(
                                            light=Custom_theme().light_colors()["tertiary"],
                                            dark=Custom_theme().dark_colors()["tertiary"]
                                        ),
                                        height="48px",
                                        width="100%",
                                        font_size="1em",
                                    ),

                                    rx.text("Sexo*", font_weight="medium", font_size="1em"),
                                    rx.select(
                                        ["Masculino", "Femenino"],
                                        placeholder="Seleccionar una opción",
                                        radius="large",
                                        bg=rx.color_mode_cond(
                                            light=Custom_theme().light_colors()["tertiary"],  # Corregido
                                            dark=Custom_theme().dark_colors()["tertiary"]     # Corregido
                                        ),
                                        width="100%",
                                        size="3",
                                        required=True,
                                        value=AuthState.new_gender,
                                        on_change=AuthState.set_new_gender,
                                    ),

                                    rx.text("Celular*", font_weight="medium", font_size="1em"),
                                    rx.input(
                                        placeholder="Ejemplo: 3121234567",
                                        value=AuthState.new_phone_number,
                                        on_change=AuthState.set_new_phone_number,
                                        type="tel",
                                        input_mode="numeric",
                                        pattern="[0-9]*",
                                        border_radius="15px",
                                        bg=rx.color_mode_cond(
                                            light=Custom_theme().light_colors()["tertiary"],  # Corregido
                                            dark=Custom_theme().dark_colors()["tertiary"]     # Corregido
                                        ),
                                        height="48px",
                                        width="100%",
                                        font_size="1em",
                                        margin_bottom="1rem"
                                    ),

                                    # Dirección
                                    rx.text("Dirección", font_weight="bold", font_size="1.1em", margin_bottom="0.5em"),

                                    rx.text("Calle y número*", font_weight="medium", font_size="1em"),
                                    rx.input(
                                        placeholder="Ejemplo: Av. Siempre Viva #742",
                                        value=AuthState.new_street_number,
                                        on_change=AuthState.set_new_street_number,
                                        border_radius="15px",
                                        bg=rx.color_mode_cond(
                                            light=Custom_theme().light_colors()["tertiary"],
                                            dark=Custom_theme().dark_colors()["tertiary"]
                                        ),
                                        height="48px",
                                        width="100%",
                                        font_size="1em",
                                    ),

                                    rx.text("Colonia*", font_weight="medium", font_size="1em"),
                                    rx.input(
                                        placeholder="Ejemplo: Centro",
                                        value=AuthState.new_neighborhood,
                                        on_change=AuthState.set_new_neighborhood,
                                        border_radius="15px",
                                        bg=rx.color_mode_cond(
                                            light=Custom_theme().light_colors()["tertiary"],
                                            dark=Custom_theme().dark_colors()["tertiary"]
                                        ),
                                        height="48px",
                                        width="100%",
                                        font_size="1em",
                                    ),

                                    rx.hstack(
                                        rx.vstack(
                                            rx.text("Ciudad*", font_weight="medium", font_size="1em"),
                                            rx.input(
                                                placeholder="Ciudad",
                                                value=AuthState.new_city,
                                                on_change=AuthState.set_new_city,
                                                border_radius="15px",
                                                bg=rx.color_mode_cond(
                                                    light=Custom_theme().light_colors()["tertiary"],
                                                    dark=Custom_theme().dark_colors()["tertiary"]
                                                ),
                                                height="48px",
                                                width="100%",
                                                font_size="1em",
                                            ),
                                            width="48%"
                                        ),
                                        rx.vstack(
                                            rx.text("C.P.*", font_weight="medium", font_size="1em"),
                                            rx.input(
                                                placeholder="28000",
                                                value=AuthState.new_zip_code,
                                                on_change=AuthState.set_new_zip_code,
                                                type="tel",
                                                input_mode="numeric",
                                                pattern="[0-9]*",
                                                border_radius="15px",
                                                bg=rx.color_mode_cond(
                                                    light=Custom_theme().light_colors()["tertiary"],
                                                    dark=Custom_theme().dark_colors()["tertiary"]
                                                ),
                                                height="48px",
                                                width="100%",
                                                font_size="1em",
                                            ),
                                            width="50%"
                                        ),
                                        justify="between",
                                        width="100%",
                                    ),

                                    rx.text("País*", font_weight="medium", font_size="1em"),
                                    rx.select(
                                        AuthState.country_options,
                                        placeholder="Seleccionar país",
                                        value=AuthState.new_country,
                                        on_change=AuthState.set_new_country,
                                        radius="large",
                                        bg=rx.color_mode_cond(
                                            light=Custom_theme().light_colors()["tertiary"],
                                            dark=Custom_theme().dark_colors()["tertiary"]
                                        ),
                                        width="100%",
                                        size="3",
                                        required=True,
                                    ),

                                    rx.text("Estado*", font_weight="medium", font_size="1em"),
                                    rx.select(
                                        AuthState.state_options,
                                        placeholder="Seleccionar estado",
                                        value=AuthState.new_state,
                                        on_change=AuthState.set_new_state,
                                        disabled=(AuthState.new_country == ""),
                                        radius="large",
                                        bg=rx.color_mode_cond(
                                            light=Custom_theme().light_colors()["tertiary"],
                                            dark=Custom_theme().dark_colors()["tertiary"]
                                        ),
                                        width="100%",
                                        size="3",
                                        required=True,
                                    ),

                                    # Acceso al sistema
                                    rx.text("Acceso al Sistema", font_weight="bold", font_size="1.1em", margin_bottom="0.5rem"),

                                    rx.text("Usuario*", font_weight="medium", font_size="1em"),
                                    rx.input(
                                        placeholder="Usuario único",
                                        value=AuthState.new_username,
                                        on_change=AuthState.set_new_username,
                                        required=True,
                                        reset_on_submit=True,
                                        border_radius="15px",
                                        bg=rx.color_mode_cond(
                                            light=Custom_theme().light_colors()["tertiary"],
                                            dark=Custom_theme().dark_colors()["tertiary"]
                                        ),
                                        height="48px",
                                        width="100%",
                                        font_size="1em",
                                    ),

                                    rx.text("Correo electrónico*", font_weight="medium", font_size="1em"),
                                    rx.input(
                                        type="email",
                                        placeholder="Correo electrónico",
                                        value=AuthState.new_email,
                                        on_change=AuthState.set_new_email,
                                        required=True,
                                        reset_on_submit=True,
                                        border_radius="15px",
                                        bg=rx.color_mode_cond(
                                            light=Custom_theme().light_colors()["tertiary"],
                                            dark=Custom_theme().dark_colors()["tertiary"]
                                        ),
                                        height="48px",
                                        width="100%",
                                        font_size="1em",
                                    ),

                                    rx.text("Contraseña*", font_weight="medium", font_size="1em"),
                                    rx.input(
                                        type="password",
                                        placeholder="Crea una contraseña",
                                        value=AuthState.new_password,  # ✅ Cambiar
                                        on_change=AuthState.set_new_password,  # ✅ Cambiar
                                        required=True,
                                        reset_on_submit=True,
                                        border_radius="15px",
                                        bg=rx.color_mode_cond(
                                            light=Custom_theme().light_colors()["tertiary"],
                                            dark=Custom_theme().dark_colors()["tertiary"]
                                        ),
                                        height="48px",
                                        width="100%",
                                        font_size="1em",
                                    ),
                                    
                                    # ✅ CORRECCIÓN: Eliminar el `rx.form` que envolvía este vstack.
                                    rx.vstack(
                                        requirement_item("Debe contener mínimo 8 caracteres.", AuthState.password_has_length),
                                        requirement_item("Debe incluir mínimo 1 letra mayúscula.", AuthState.password_has_uppercase),
                                        requirement_item("Debe incluir mínimo 1 letra minúscula.", AuthState.password_has_lowercase),
                                        requirement_item("Debe incluir mínimo 1 número.", AuthState.password_has_number),
                                        requirement_item("Debe incluir mínimo 1 carácter especial.", AuthState.password_has_special),
                                        spacing="1",
                                        align_items="flex-start",
                                        width="100%",
                                        padding_y="0.5rem"
                                    ),

                                    rx.text("Confirmar contraseña*", font_weight="medium", font_size="1em"),
                                    rx.input(
                                        type="password",
                                        placeholder="Confirma la contraseña",
                                        value=AuthState.new_confirmed_password,  # ✅ Cambiar
                                        on_change=AuthState.set_new_confirmed_password,  # ✅ Cambiar
                                        required=True,
                                        reset_on_submit=True,
                                        border_radius="15px",
                                        bg=rx.color_mode_cond(
                                            light=Custom_theme().light_colors()["tertiary"],
                                            dark=Custom_theme().dark_colors()["tertiary"]
                                        ),
                                        height="48px",
                                        width="100%",
                                        font_size="1em",
                                    ),
                                    
                                    # Términos y condiciones
                                    rx.hstack(
                                        rx.checkbox(
                                            checked=AuthState.new_terms_accepted,
                                            on_change=AuthState.set_new_terms_accepted,
                                            required=True,
                                        ),
                                        rx.text(
                                            "He leído los ", rx.link("terminos y condiciones.", href="#"),
                                            font_size="0.85em"  # --- Propiedades rx.text ---
                                        ),
                                        margin_bottom="1.5rem",
                                        spacing="1"  # --- Propiedades rx.hstack ---
                                    ),
                                    
                                    rx.button(
                                        "Registrarse",
                                        bg=rx.color_mode_cond(
                                            light=Custom_theme().light_colors()["primary"],
                                            dark=Custom_theme().dark_colors()["primary"]
                                        ),
                                        color="white",
                                        border_radius="24px",
                                        width="100%",
                                        height="64px",
                                        font_size="1.1rem",
                                        font_weight="bold",
                                        type="submit",
                                        on_click=AuthState.new_register_sponsor,
                                    ),
                                    
                                    spacing="3",
                                    width="100%"
                                ),
                                width="48%",
                                spacing="3",
                            ),
                            # Propiedades @Main container de la derecha
                            width="100%", # Ancho total del contenido de la página
                        ),
                    ),
                    width="100%", # Propiedad necesaria para que el contenedor quede centrado no importa si la ventana es muy grande.
                ),
                # Propiedades vstack que contiene el contenido de la página.
                align="end",
                margin_top="8em",
                margin_bottom="2em",
                width="100%",
                max_width="1920px",
            )
        ),
        
        # Versión móvil
        rx.mobile_only(
            rx.vstack(
                # Habrá un header móvil si el usuario ya está logueado
                rx.cond(
                    AuthState.profile_data.get("member_id"),
                    mobile_header(),
                ),
                # Espaciado extra si el usuario ya está logueado
                rx.cond(
                    AuthState.profile_data.get("member_id"),
                    rx.box(margin_bottom="80px"),
                    rx.box(margin_bottom="1em")
                ),
                # Contenido principal móvil
                rx.form(
                    rx.vstack(
                        rx.text(
                            f"Referido por {AuthState.sponsor_display_name}",
                            font_size="1em",
                            color=rx.color_mode_cond(
                                light=Custom_theme().light_colors()["primary"],
                                dark=Custom_theme().dark_colors()["primary"]
                            ),
                            font_weight="bold",
                            margin_bottom="1em"
                        ),
                        
                        # Información personal
                        rx.text("Información Personal", font_weight="bold", font_size="1.1em", margin_bottom="0.5em"),
                        
                        rx.text(
                            "Nombre(s)*",
                            font_weight="medium",
                            font_size="1em",
                            ),
                        rx.input(
                            placeholder="Ejemplo: Juan Carlos",
                            value=AuthState.new_user_firstname,
                            on_change=AuthState.set_new_firstname,
                            required=True,
                            reset_on_submit=True,
                            border_radius="15px",
                            bg=rx.color_mode_cond(
                                light=Custom_theme().light_colors()["tertiary"],
                                dark=Custom_theme().dark_colors()["tertiary"]
                            ),
                            height="48px",
                            width="100%",
                            font_size="1em",
                        ),

                        rx.text(
                            "Apellido(s)*",
                            font_weight="medium",
                            font_size="1em",
                            ),
                        rx.input(
                            placeholder="Ejemplo: Pérez Quiroz",
                            value=AuthState.new_user_lastname,
                            on_change=AuthState.set_new_lastname,
                            required=True,
                            reset_on_submit=True,
                            border_radius="15px",
                            bg=rx.color_mode_cond(
                                light=Custom_theme().light_colors()["tertiary"],
                                dark=Custom_theme().dark_colors()["tertiary"]
                            ),
                            height="48px",
                            width="100%",
                            font_size="1em",
                        ),

                        rx.text("Sexo*", font_weight="medium", font_size="1em"),
                        rx.select(
                            ["Masculino", "Femenino"],
                            placeholder="Seleccionar una opción",
                            radius="large",
                            bg=rx.color_mode_cond(
                                light=Custom_theme().light_colors()["tertiary"],  # Corregido
                                dark=Custom_theme().dark_colors()["tertiary"]     # Corregido
                            ),
                            width="100%",
                            size="3",
                            required=True,
                            value=AuthState.new_gender,
                            on_change=AuthState.set_new_gender,
                        ),

                        rx.text("Celular*", font_weight="medium", font_size="1em"),
                        rx.input(
                            placeholder="Ejemplo: 3121234567",
                            value=AuthState.new_phone_number,
                            on_change=AuthState.set_new_phone_number,
                            type="tel",
                            border_radius="15px",
                            bg=rx.color_mode_cond(
                                light=Custom_theme().light_colors()["tertiary"],  # Corregido
                                dark=Custom_theme().dark_colors()["tertiary"]     # Corregido
                            ),
                            height="48px",
                            width="100%",
                            font_size="1em",
                            margin_bottom="1rem"
                        ),

                        # Dirección
                        rx.text("Dirección", font_weight="bold", font_size="1.1em", margin_bottom="0.5em"),

                        rx.text("País*", font_weight="medium", font_size="1em"),
                        rx.select(
                            AuthState.country_options,
                            placeholder="Seleccionar país",
                            value=AuthState.new_country,
                            on_change=AuthState.set_new_country,
                            radius="large",
                            bg=rx.color_mode_cond(
                                light=Custom_theme().light_colors()["tertiary"],
                                dark=Custom_theme().dark_colors()["tertiary"]
                            ),
                            width="100%",
                            size="3",
                            required=True,
                        ),

                        rx.text("Calle y número*", font_weight="medium", font_size="1em"),
                        rx.input(
                            placeholder="Ejemplo: Siempre Viva #742",
                            value=AuthState.new_street_number,
                            on_change=AuthState.set_new_street_number,
                            border_radius="15px",
                            bg=rx.color_mode_cond(
                                light=Custom_theme().light_colors()["tertiary"],
                                dark=Custom_theme().dark_colors()["tertiary"]
                            ),
                            height="48px",
                            width="100%",
                            font_size="1em",
                        ),

                        rx.text("Colonia*", font_weight="medium", font_size="1em"),
                        rx.input(
                            placeholder="Ejemplo: Centro",
                            value=AuthState.new_neighborhood,
                            on_change=AuthState.set_new_neighborhood,
                            border_radius="15px",
                            bg=rx.color_mode_cond(
                                light=Custom_theme().light_colors()["tertiary"],
                                dark=Custom_theme().dark_colors()["tertiary"]
                            ),
                            height="48px",
                            width="100%",
                            font_size="1em",
                        ),

                        rx.hstack(
                            rx.vstack(
                                rx.text("Ciudad*", font_weight="medium", font_size="1em"),
                                rx.input(
                                    placeholder="Ciudad",
                                    value=AuthState.new_city,
                                    on_change=AuthState.set_new_city,
                                    border_radius="15px",
                                    bg=rx.color_mode_cond(
                                        light=Custom_theme().light_colors()["tertiary"],
                                        dark=Custom_theme().dark_colors()["tertiary"]
                                    ),
                                    height="48px",
                                    width="100%",
                                    font_size="1em",
                                ),
                                width="48%"
                            ),
                            rx.vstack(
                                rx.text("C.P.*", font_weight="medium", font_size="1em"),
                                rx.input(
                                    placeholder="28000",
                                    value=AuthState.new_zip_code,
                                    on_change=AuthState.set_new_zip_code,
                                    type="tel",
                                    input_mode="numeric",
                                    pattern="[0-9]*",
                                    border_radius="15px",
                                    bg=rx.color_mode_cond(
                                        light=Custom_theme().light_colors()["tertiary"],
                                        dark=Custom_theme().dark_colors()["tertiary"]
                                    ),
                                    height="48px",
                                    width="100%",
                                    font_size="1em",
                                ),
                                width="50%"
                            ),
                            justify="between",
                            width="100%",
                        ),

                        rx.text("Estado*", font_weight="medium", font_size="1em"),
                        rx.select(
                            AuthState.state_options,
                            placeholder="Seleccionar estado",
                            value=AuthState.new_state,
                            on_change=AuthState.set_new_state,
                            disabled=(AuthState.new_country == ""),
                            radius="large",
                            bg=rx.color_mode_cond(
                                light=Custom_theme().light_colors()["tertiary"],
                                dark=Custom_theme().dark_colors()["tertiary"]
                            ),
                            width="100%",
                            size="3",
                            required=True,
                        ),

                        # Acceso al sistema
                        rx.text("Acceso al Sistema", font_weight="bold", font_size="1.1em", margin_bottom="0.5rem"),

                        rx.text("Usuario*", font_weight="medium", font_size="1em"),
                        rx.input(
                            rx.button(
                                "Sugerir",
                                size="3",
                                border_radius="11px",
                                variant="surface",
                                on_click=AuthState.random_username,
                            ),
                            placeholder="Usuario único",
                            value=AuthState.new_username,
                            on_change=AuthState.set_new_username,
                            required=True,
                            reset_on_submit=True,
                            border_radius="15px",
                            bg=rx.color_mode_cond(
                                light=Custom_theme().light_colors()["tertiary"],
                                dark=Custom_theme().dark_colors()["tertiary"]
                            ),
                            height="48px",
                            width="100%",
                            padding="4px",
                            font_size="1em",
                        ),

                        rx.text("Correo electrónico*", font_weight="medium", font_size="1em"),
                        rx.input(
                            type="email",
                            placeholder="Correo electrónico",
                            value=AuthState.new_email,
                            on_change=AuthState.set_new_email,
                            required=True,
                            reset_on_submit=True,
                            border_radius="15px",
                            bg=rx.color_mode_cond(
                                light=Custom_theme().light_colors()["tertiary"],
                                dark=Custom_theme().dark_colors()["tertiary"]
                            ),
                            height="48px",
                            width="100%",
                            font_size="1em",
                        ),

                        rx.text("Contraseña*", font_weight="medium", font_size="1em"),
                        rx.input(
                            type="password",
                            placeholder="Crea una contraseña",
                            value=AuthState.new_password,  # ✅ Cambiar
                            on_change=AuthState.set_new_password,  # ✅ Cambiar
                            required=True,
                            reset_on_submit=True,
                            border_radius="15px",
                            bg=rx.color_mode_cond(
                                light=Custom_theme().light_colors()["tertiary"],
                                dark=Custom_theme().dark_colors()["tertiary"]
                            ),
                            height="48px",
                            width="100%",
                            font_size="1em",
                        ),
                        
                        # ✅ REEMPLAZAR LA LISTA ESTÁTICA CON ESTE BLOQUE DINÁMICO
                        rx.vstack(
                            requirement_item("Debe contener mínimo 8 caracteres.", AuthState.password_has_length),
                            requirement_item("Debe incluir mínimo 1 letra mayúscula.", AuthState.password_has_uppercase),
                            requirement_item("Debe incluir mínimo 1 letra minúscula.", AuthState.password_has_lowercase),
                            requirement_item("Debe incluir mínimo 1 número.", AuthState.password_has_number),
                            requirement_item("Debe incluir mínimo 1 carácter especial.", AuthState.password_has_special),
                            spacing="1",
                            align_items="flex-start",
                            width="100%",
                            padding_y="0.5rem"
                        ),

                        rx.text("Confirmar contraseña*", font_weight="medium", font_size="1em"),
                        rx.input(
                            type="password",
                            placeholder="Confirma la contraseña",
                            value=AuthState.new_confirmed_password,  # ✅ Cambiar
                            on_change=AuthState.set_new_confirmed_password,  # ✅ Cambiar
                            required=True,
                            reset_on_submit=True,
                            border_radius="15px",
                            bg=rx.color_mode_cond(
                                light=Custom_theme().light_colors()["tertiary"],
                                dark=Custom_theme().dark_colors()["tertiary"]
                            ),
                            height="48px",
                            width="100%",
                            font_size="1em",
                        ),
                        
                        # Términos y condiciones
                        rx.hstack(
                            rx.checkbox(
                                checked=AuthState.new_terms_accepted,
                                on_change=AuthState.set_new_terms_accepted,
                                required=True,
                            ),
                            rx.text(
                                "He leído los ", rx.link("terminos y condiciones.", href="#"),
                                font_size="0.85em"  # --- Propiedades rx.text ---
                            ),
                            margin_bottom="2rem",
                            spacing="1"  # --- Propiedades rx.hstack ---
                        ),
                        
                        rx.button(
                            "Registrarse",
                            bg=rx.color_mode_cond(
                                light=Custom_theme().light_colors()["primary"],
                                dark=Custom_theme().dark_colors()["primary"]
                            ),
                            color="white",
                            border_radius="32px",
                            width="100%",
                            height="64px",
                            font_size="1.1rem",
                            font_weight="bold",
                            type="submit",
                            on_click=AuthState.new_register_sponsor,
                            disabled=~AuthState.can_register,  # ✅ Deshabilitar si no hay sponsor
                        ),
                        
                        spacing="3",
                        width="100%"
                    ),
                    width="100%",
                    margin_bottom="1em"
                ),
                align="center",
                padding="0 1em 1em 1em",
                width="100%",
                min_height="100vh",
                bg=rx.color_mode_cond(
                    light=Custom_theme().light_colors()["background"],
                    dark=Custom_theme().dark_colors()["background"]
                )
            )
        ),
        
        # Propiedades del contenedor principal.
        bg=rx.color_mode_cond(
            light=Custom_theme().light_colors()["background"],
            dark=Custom_theme().dark_colors()["background"]
        ),
        position="absolute",
        width="100%",
        on_mount=AuthState.on_load_register_page,
    )


def requirement_item(text: str, is_met: rx.Var[bool]) -> rx.Component:
    """Muestra un requisito de la checklist con un icono y color dinámicos."""
    return rx.hstack(
        rx.cond(
            is_met,
            rx.icon("circle-check", color="green", size=16),
            rx.icon("circle", color=rx.color_mode_cond("gray.300", "gray.600"), size=16)
        ),
        rx.text(
            text,
            color=rx.cond(is_met, "green", rx.color_mode_cond("gray.500", "gray.400")),
            font_size="0.85rem"
        ),
        spacing="2",
        align="center"
    )