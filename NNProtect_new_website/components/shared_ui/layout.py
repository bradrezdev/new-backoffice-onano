import reflex as rx
from .theme import Custom_theme
from NNProtect_new_website.modules.auth.state.auth_state import AuthState
from NNProtect_new_website.modules.store.state.store_state import CountProducts

############################################
# --- Componente links + cuenta activa --- #
############################################

def header() -> rx.Component:
    return rx.hstack(
        rx.spacer(),
        #quick_links(),
        logged_in_user(),
        width="95%",
        position="fixed",
        top="24px",
        #left="13%",
        z_index="10",
        justify="between",
    )

##########################################
# --- Componentes para links rápidos --- #
##########################################
"""
def quick_links() -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.link(
                rx.button(
                    "Nuevo registro",
                    height="40px",
                    variant="solid",
                    border_radius="32px",
                    padding="24px 12px",
                    _hover={"opacity": 0.9},
                )
            ),
            rx.link(
                rx.button(
                    "Reportes de red",
                    height="40px",
                    variant="solid",
                    border_radius="32px",
                    padding="24px 12px",
                    _hover={"opacity": 0.9},
                )
            ),
            rx.link(
                rx.button(
                    "Detalles de comisiones",
                    height="40px",
                    variant="solid",
                    border_radius="32px",
                    padding="24px 12px",
                    _hover={"opacity": 0.9},
                )
            ),
            rx.link(
                rx.button(
                    "Solicitar comisiones",
                    height="40px",
                    variant="solid",
                    border_radius="32px",
                    padding="24px 12px",
                    _hover={"opacity": 0.9},
                )
            ),
            rx.link(
                rx.button(
                    "Transferencia interna",
                    height="40px",
                    variant="solid",
                    border_radius="32px",
                    padding="24px 12px",
                    _hover={"opacity": 0.9},
                )
            ),
        ),
        border_radius="32px",
        padding="8px",
        bg=rx.color_mode_cond(
            light=Custom_theme().light_colors()["traslucid-background"],
            dark=Custom_theme().dark_colors()["traslucid-background"]
        ),
        box_shadow=rx.color_mode_cond(
            light=Custom_theme().light_colors()["box_shadow"],
            dark=Custom_theme().dark_colors()["box_shadow"],
        ),
        backdrop_filter="blur(8px)",  # Efecto de desenfoque (blur)
    )
"""

#############################################
# --- Componentes para la cuenta activa --- #
#############################################

def logged_in_user() -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.image(src="/user_avatar.png", width="40px", border_radius="full", margin_right="8px"),
            rx.text(AuthState.get_user_display_name, font_size="1rem", font_weight="medium", margin_right="16px"),
            rx.icon("ellipsis-vertical", size=20, margin_left="4px"),
            align="center",
            padding="12px 24px 12px 24px",
        ),
        #top="32px",
        #z_index="10",
        #position="fixed",
        border_radius="32px",
        bg=rx.color_mode_cond(
            light=Custom_theme().light_colors()["traslucid-background"],
            dark=Custom_theme().dark_colors()["traslucid-background"]
        ),
        box_shadow=rx.color_mode_cond(
            light=Custom_theme().light_colors()["box_shadow"],
            dark=Custom_theme().dark_colors()["box_shadow"],
        ),
        backdrop_filter="blur(8px)",  # Efecto de desenfoque (blur)
        #align="end",
    )
"""
def mobile_logged_in_user() -> rx.Component:
    return rx.box(
        rx.text(profile_data.get("firstname") + " " + profile_data.get("lastname"), font_size="1rem", font_weight="medium", margin_right="16px"),
        border_radius="32px",
        bg=rx.color_mode_cond(
            light=Custom_theme().light_colors()["traslucid-background"],
            dark=Custom_theme().dark_colors()["traslucid-background"]
        ),
        box_shadow=rx.color_mode_cond(
            light=Custom_theme().light_colors()["box_shadow"],
            dark=Custom_theme().dark_colors()["box_shadow"],
        ),
        backdrop_filter="blur(8px)",
    )
"""
#######################################
# --- Componentes para el sidebar --- #
#######################################

def sidebar_item(text: str, icon: str, href: str) -> rx.Component:
    return rx.link(
        rx.hstack(
            rx.icon(icon),
            rx.text(text, font_size="1rem"),
            width="100%",
            padding_x="1rem",
            padding_y="0.75rem",
            align="center",
            style={
                "_hover": {
                    "bg": rx.color("accent", 4),
                    "color": rx.color("accent", 11),
                },
                "border-radius": "1rem",
            },
        ),
        href=href,
        underline="none",
        weight="medium",
        width="100%",
    )

def sidebar_subitem(text: str, href: str) -> rx.Component:
    return rx.link(
        rx.hstack(
            rx.text(text, font_size="1rem"),
            width="100%",
            padding_x="1rem",
            padding_y="0.75rem",
            align="center",
            style={
                "_hover": {
                    "bg": rx.color("accent", 4),
                    "color": rx.color("accent", 11),
                },
                "border-radius": "1rem",
            },
        ),
        href=href,
        underline="none",
        weight="medium",
        width="100%",
    )

def desktop_sidebar() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.image(src="/nnprotect_logo.png", height="5vh", position="top", margin="auto"),
            rx.spacer(),
            rx.spacer(),
            rx.spacer(),
            rx.spacer(),
            sidebar_item("Dashboard", "layout-dashboard", "/dashboard"),
            sidebar_item("Nuevo registro", "circle-plus", "/register"),
            rx.accordion.root(
                rx.accordion.item(
                    header=rx.hstack(rx.icon("network"), rx.text("Negocio")),
                    content=rx.vstack(
                        sidebar_subitem("Red de negocio", "/network"),
                        sidebar_subitem("Reportes de red", "/network_reports"),
                        sidebar_subitem("Detalles de comisiones", "/income_reports")
                    ),
                ),
                variant="ghost",
                collapsible=True,
                type="multiple",
                width="100%",
            ),
            sidebar_item("Órdenes", "scroll-text", "/orders"),
            sidebar_item("Tienda", "store", "/store"),
            sidebar_item("Retiros", "wallet", "/withdrawals"),
            sidebar_item("NN Travels", "plane", "/travels"),
            sidebar_item("Tickets/Soporte", "messages-square", "/tickets"),
            sidebar_item("Herramientas", "folder-cog", "/tools"),
            spacing="2",
            width="100%",
        ),
        bg=rx.color_mode_cond(
            light=Custom_theme().light_colors()["tertiary"],
            dark=Custom_theme().dark_colors()["tertiary"],
        ),
        border_radius="36px",
        box_shadow=rx.color_mode_cond(
            light=Custom_theme().light_colors()["box_shadow"],
            dark=Custom_theme().dark_colors()["box_shadow"],
        ),
        top="128px",
        left="2vw",
        z_index="1",
        position="fixed",
        align="start",
        padding="32px 20px 16px 20px",
        height="auto",
        max_width="16vw",
    )

def mobile_sidebar() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.image(src="/nnprotect_logo.png", height="5vh", position="top", margin="auto"),
            rx.spacer(),
            rx.spacer(),
            rx.spacer(),
            rx.spacer(),
            rx.spacer(),
            sidebar_item("Dashboard", "layout-dashboard", "/dashboard"),
            sidebar_item("Nuevo registro", "circle-plus", "/register"),
            rx.accordion.root(
                rx.accordion.item(
                    header=rx.hstack(rx.icon("network"), rx.text("Negocio")),
                    content=rx.vstack(
                        sidebar_subitem("Red de negocio", "/network"),
                        sidebar_subitem("Reportes de red", "/network_reports"),
                        sidebar_subitem("Detalles de comisiones", "/income_reports")
                    ),
                ),
                variant="ghost",
                collapsible=True,
                type="multiple",
                width="100%",
            ),
            sidebar_item("Órdenes", "scroll-text", "/orders"),
            sidebar_item("Tienda", "store", "/store"),
            sidebar_item("Retiros", "wallet", "/withdrawals"),
            sidebar_item("NN Travels", "plane", "/travels"),
            sidebar_item("Tickets/Soporte", "messages-square", "/tickets"),
            sidebar_item("Herramientas", "folder-cog", "/tools"),
            rx.button(
                "Cerrar sesión",
                font_size="1em",
                font_weight="bold",
                bg=rx.color_mode_cond(
                    light=Custom_theme().light_colors()["primary"],
                    dark=Custom_theme().light_colors()["primary"],
                ),
                border_radius="16px",
                height="48px",
                margin_top="32px",
                width="100%",
                on_click=AuthState.logout_user,
            ),
            spacing="2",
            width="100%",
        ),
        bg=rx.color_mode_cond(
            light=Custom_theme().light_colors()["tertiary"],
            dark=Custom_theme().dark_colors()["tertiary"],
        ),
        box_shadow=rx.color_mode_cond(
            light=Custom_theme().light_colors()["box_shadow"],
            dark=Custom_theme().dark_colors()["box_shadow"],
        ),
        padding="20px 10px 20px 10px",
        height="100%",
        width="80vw",
        z_index="100",
    )

#######################################
# --- Contenedores principales ------- #
#######################################

def main_container_derecha(*children):
    return rx.box(
        rx.vstack(
            *children,
        ),
        margin_left="240px",
        width="77vw",  # Cambiado de 60vw a 100%
        #flex="1",      # Para que ocupe el espacio restante
    )

def mobile_header():
    return rx.hstack(
        rx.drawer.root(
            rx.drawer.trigger(
                rx.button(
                    rx.icon(
                        "menu",
                        color=rx.color_mode_cond(
                            light=Custom_theme().light_colors()["text"],
                            dark=Custom_theme().dark_colors()["text"]
                        ),
                        size=24
                        ),
                    radius="full",
                    height="48px",
                    backdrop_filter="blur(30px)",
                    box_shadow=rx.color_mode_cond(
                        light=Custom_theme().light_colors()["box_shadow"],
                        dark=Custom_theme().dark_colors()["box_shadow"],
                    ),
                    bg=rx.color_mode_cond(
                        light=Custom_theme().light_colors()["traslucid-background"],
                        dark=Custom_theme().dark_colors()["traslucid-background"]
                    ),
                ),
            ),
            rx.drawer.overlay(z_index="500"),
            rx.drawer.portal(
                rx.drawer.content(
                    mobile_sidebar(),
                )
            ),
            direction="left",
        ),
        rx.hstack(
            rx.flex(
                rx.button(
                    rx.icon(
                    "bell",
                    color=rx.color_mode_cond(
                        light=Custom_theme().light_colors()["text"],
                        dark=Custom_theme().dark_colors()["text"]
                    ),
                    size=24
                    ),
                    variant="ghost",
                    radius="full",
                ),
                rx.button(
                    rx.cond(
                        CountProducts.cart_total > 0,
                        rx.box(
                            rx.text(CountProducts.cart_total, color="white", font_size="0.8em", font_weight="bold", margin="0"),
                            bg="red",
                            border="1px solid white",
                            border_radius="36px",
                            width="21px",
                            height="content",
                            align="center",
                            justify="center",
                            padding="2px",
                            position="absolute",
                            top="6px",
                            right="6px",
                            z_index="1",
                        )
                    ),
                    rx.icon(
                        "shopping-cart",
                        color=rx.color_mode_cond(
                            light=Custom_theme().light_colors()["text"],
                            dark=Custom_theme().dark_colors()["text"]
                        ),
                        size=24
                    ),
                    variant="ghost",
                    radius="full",
                    disabled=CountProducts.cart_total == 0,
                    on_click=rx.redirect("/shopping_cart")
                ),
                padding="0 16px",
                spacing="4",
                direction="row",
                height="48px",
                align="center",
                border_radius="32px",
                bg=rx.color_mode_cond(
                    light=Custom_theme().light_colors()["traslucid-background"],
                    dark=Custom_theme().dark_colors()["traslucid-background"]
                ),
                box_shadow=rx.color_mode_cond(
                    light=Custom_theme().light_colors()["box_shadow"],
                    dark=Custom_theme().dark_colors()["box_shadow"],
                ),
                backdrop_filter="blur(8px)",
            ),
            rx.center(
                rx.text(AuthState.profile_data.get("profile_name"), font_size="1rem", font_weight="bold", margin="0 16px 0 16px"),
                border_radius="32px",
                bg=rx.color_mode_cond(
                    light=Custom_theme().light_colors()["traslucid-background"],
                    dark=Custom_theme().dark_colors()["traslucid-background"]
                ),
                box_shadow=rx.color_mode_cond(
                    light=Custom_theme().light_colors()["box_shadow"],
                    dark=Custom_theme().dark_colors()["box_shadow"],
                ),
                height="48px",
                backdrop_filter="blur(8px)",
            ),
        ),
        bg=rx.color_mode_cond(
            light=Custom_theme().light_colors()["menu-background"],
            dark=Custom_theme().dark_colors()["menu-background"],
        ),
        backdrop_filter="blur(2px)",
        width="100%",
        padding="1rem",
        justify="between",
        position="fixed",
        top="0",
        z_index="1",
        margin_bottom="80px",
    )