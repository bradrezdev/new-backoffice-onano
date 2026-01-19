"""Nueva Backoffice NN Protect | Órdenes"""

import reflex as rx
from rxconfig import config

from ....components.shared_ui.theme import Custom_theme
from ....components.shared_ui.layout import main_container_derecha, mobile_header, desktop_sidebar, header

# Importar OrderState
from ..state.orders_state import OrderState


# ============================================================================
# HELPER FUNCTIONS PARA RENDERIZADO DINÁMICO
# ============================================================================

def get_payment_method_icon(payment_method) -> rx.Component:
	"""Retorna el ícono apropiado según el método de pago.
	Usa rx.match para ser compatible con reactive Vars.

	Args:
		payment_method: Método de pago (puede ser str o Var)

	Returns:
		Reactive expression que retorna el nombre del ícono
	"""
	return rx.match(
		payment_method,
		("Tarjeta crédito", "credit-card"),
		("Tarjeta débito", "credit-card"),
		("Billetera digital", "wallet"),
		("PayPal", "wallet"),
		("Transferencia", "banknote"),
		("Efectivo", "banknote"),
		("admin_test", "credit-card"),
		"credit-card"  # default
	)


def get_status_color_scheme(status) -> rx.Component:
	"""Retorna el color scheme de badge según el estado.
	Usa rx.match para ser compatible con reactive Vars.

	Args:
		status: Estado de la orden (puede ser str o Var)

	Returns:
		Reactive expression que retorna el color scheme
	"""
	return rx.match(
		status,
		("Pendiente", "orange"),
		("En proceso", "blue"),
		("Enviado", "cyan"),
		("En camino", "yellow"),
		("Entregado", "green"),
		("Cancelado", "red"),
		"gray"  # default
	)


# ============================================================================
# COMPONENTES REUTILIZABLES PARA DESKTOP
# ============================================================================

def desktop_order_row(order: dict) -> rx.Component:
	"""Renderiza una fila de orden en la tabla de escritorio.

	Args:
		order: Diccionario con datos de la orden (debe incluir:
			- order_number: str
			- shipping_address: str
			- purchase_date: str
			- payment_method: str
			- total: str
			- status: str
			- order_id: str (para navegación)
		)

	Returns:
		rx.table.row con todos los datos de la orden
	"""
	return rx.table.row(
		rx.table.row_header_cell(
			f"#{order['order_number']}",
			font_weight="bold"
		),
		rx.table.cell(order['shipping_address']),
		rx.table.cell(order['purchase_date']),
		rx.table.cell(
			rx.hstack(
				rx.icon(
					get_payment_method_icon(order['payment_method']),
					size=16
				),
				rx.text(order['payment_method']),
				spacing="1"
			)
		),
		rx.table.cell(
			order['total'],
			font_weight="bold",
			color=rx.color_mode_cond(
				light=Custom_theme().light_colors()["primary"],
				dark=Custom_theme().dark_colors()["primary"]
			)
		),
		rx.table.cell(
			rx.badge(
				order['status'],
				color_scheme=get_status_color_scheme(order['status'])
			)
		),
		rx.table.cell(
			rx.hstack(
				rx.button(
					rx.icon("eye", size=16),
					"Ver detalles",
					size="2",
					variant="soft",
					color_scheme="blue",
					on_click=lambda: rx.redirect(f"/orders/order_details?id={order['order_id']}")
				),
				rx.button(
					rx.icon("download", size=16),
					"PDF",
					size="2",
					variant="outline",
					color_scheme="gray"
					# TODO: Conectar con función de descarga PDF cuando esté disponible
					# on_click=OrderState.download_pdf(order['order_id'])
				),
				spacing="2",
				justify="center"
			)
		),
	)


# ============================================================================
# COMPONENTES REUTILIZABLES PARA MOBILE
# ============================================================================

def mobile_product_item(product: dict) -> rx.Component:
	"""Renderiza un producto dentro de la orden móvil.

	Args:
		product: Diccionario con datos del producto (debe incluir:
			- name: str
			- quantity: int
		)

	Returns:
		rx.hstack con el nombre y cantidad del producto
	"""
	return rx.hstack(
		rx.text(
			product['name'],
			font_size="0.9em",
			color=rx.color_mode_cond(
				light="gray.600",
				dark="gray.400"
			)
		),
		rx.text(
			f"Cantidad: {product['quantity']}",
			font_size="0.9em",
			font_weight="medium",
			color=rx.color_mode_cond(
				light="gray.700",
				dark="gray.300"
			)
		),
		justify="between",
		width="100%"
	)


def mobile_order_card(order: dict) -> rx.Component:
	"""Renderiza una card de orden en la versión móvil.

	Args:
		order: Diccionario con datos de la orden (debe incluir:
			- order_number: str
			- shipping_status: str (ej: "En camino")
			- payment_status: str (ej: "Pagado")
			- purchase_date: str
			- payment_method: str
			- shipping_alias: str (alias de la dirección)
			- products: list[dict] (lista de productos con name y quantity)
			- total: str
			- order_id: str (para navegación)
		)

	Returns:
		rx.box con la card completa de la orden
	"""
	return rx.box(
		rx.vstack(
			# Header: Número de orden y badges
			rx.flex(
				rx.text(
					f"#{order['order_number']}",
					font_weight="bold",
					font_size="1.25em"
				),
				rx.hstack(
					rx.badge(
						order['shipping_status'],
						color_scheme=get_status_color_scheme(order['shipping_status']),
						size="2",
						radius="full"
					),
					rx.badge(
						order['payment_status'],
						color_scheme=get_status_color_scheme(order['payment_status']),
						size="2",
						radius="full"
					),
					spacing="1"
				),
				width="100%",
				align="center",
				justify="between",
			),

			# Información de la orden
			rx.vstack(
				rx.hstack(
					rx.icon("calendar", size=16, color=rx.color("gray", 11)),
					rx.text(
						order['purchase_date'],
						font_size="1em",
						color=rx.color("gray", 11)
					),
					align="center",
					spacing="1"
				),
				rx.hstack(
					rx.icon("credit-card", size=16, color=rx.color("gray", 11)),
					rx.text(
						order['payment_method'],
						font_size="1em",
						color=rx.color("gray", 11)
					),
					align="center",
					spacing="1"
				),
				rx.hstack(
					rx.icon("map-pin", size=16, color=rx.color("gray", 11)),
					rx.text(
						order['shipping_alias'],
						font_size="1em",
						color=rx.color("gray", 11)
					),
					align="center",
					spacing="1"
				),
				spacing="1",
				align="start",
				width="100%"
			),

			rx.divider(margin="0.5em 0"),

			# Productos
			rx.text("Productos", font_size="1em", font_weight="bold"),
			rx.text(
				order['products_summary'],
				font_size="0.9em",
				color=rx.color_mode_cond(
					light="gray.600",
					dark="gray.400"
				),
				white_space="pre",  # Respeta saltos de línea (\n)
				width="100%"
			),

			rx.divider(margin="0.5em 0"),

			# Total
			rx.hstack(
				rx.text("Total:", font_size="1.25em"),
				rx.text(
					order['total'],
					font_weight="bold",
					font_size="1.25em",
					color=rx.color_mode_cond(
						light=Custom_theme().light_colors()["primary"],
						dark=Custom_theme().dark_colors()["primary"]
					)
				),
				margin_bottom="0.5em",
				spacing="1",
				align="end",
			),

			# Botones de acción
			rx.hstack(
				rx.button(
					"Ver detalles",
					bg=rx.color_mode_cond(
						light=Custom_theme().light_colors()["primary"],
						dark=Custom_theme().dark_colors()["primary"]
					),
					color="white",
					width="48%",
					size="3",
					font_size="1em",
					radius="full",
					on_click=lambda: rx.redirect(f"/orders/order_details?id={order['order_id']}")
				),
				rx.button(
					rx.icon("download", size=18),
					"PDF",
					variant="outline",
					width="48%",
					size="3",
					font_size="1em",
					radius="full",
					# TODO: Conectar con función de descarga PDF cuando esté disponible
					# on_click=OrderState.download_pdf(order['order_id'])
				),
				width="100%",
			),
			spacing="3",
			width="100%"
		),
		bg=rx.color_mode_cond(
			light=Custom_theme().light_colors()["tertiary"],
			dark=Custom_theme().dark_colors()["tertiary"]
		),
		border_radius="32px",
		padding="1em",
		width="100%",
		margin_bottom="0.8em"
	)


# ============================================================================
# PÁGINA PRINCIPAL
# ============================================================================

def orders() -> rx.Component:
	"""Página que muestra todas las órdenes del usuario"""
	return rx.center(
		# Versión de escritorio
		rx.desktop_only(
			rx.vstack(
				header(),  # Muestra el usuario logueado en la esquina superior derecha
				rx.hstack(
					desktop_sidebar(),
					main_container_derecha(
						rx.vstack(
							# Encabezado de la página
							rx.text(
								"Órdenes",
								font_size="2em",
								font_weight="bold",
								margin_bottom="0.5em"
							),

							# Barra de búsqueda y filtros
							rx.hstack(
								# Campo de búsqueda
								rx.box(
									rx.hstack(
										rx.icon("search", size=20, color=rx.color("gray", 11)),
										rx.input(
											placeholder="Buscar por número de orden...",
											border="none",
											bg="transparent",
											width="100%",
											_focus={"outline": "none"},
									value=OrderState.search_query,
									on_change=OrderState.set_search_query
										),
										width="100%",
										align="center",
										spacing="2"
									),
									bg=rx.color_mode_cond(
										light=Custom_theme().light_colors()["tertiary"],
										dark=Custom_theme().dark_colors()["tertiary"]
									),
									border_radius="32px",
									padding="12px 24px",
									width="40%",
									border=f"1px solid {rx.color('gray', 6)}"
								),

								# Filtros adicionales
								rx.select(
									["Todas", "Pendiente", "En proceso", "Enviado", "Entregado", "Cancelado"],
									placeholder="Estado",
									default_value="Todas",
									radius="large",
									width="200px",
									value=OrderState.status_filter,
									on_change=OrderState.set_status_filter
								),

								rx.select(
									["Más reciente", "Más antiguo", "Mayor monto", "Menor monto"],
									placeholder="Ordenar por",
									default_value="Más reciente",
									radius="large",
									width="200px",
									value=OrderState.sort_by,
									on_change=OrderState.set_sort_by
								),

								width="100%",
								justify="between",
								margin_bottom="2em"
							),

							# Tabla de órdenes
							rx.box(
								rx.table.root(
									rx.table.header(
										rx.table.row(
											rx.table.column_header_cell("# Orden"),
											rx.table.column_header_cell("Dirección de envío"),
											rx.table.column_header_cell("Fecha de compra"),
											rx.table.column_header_cell("Método de pago"),
											rx.table.column_header_cell("Total pagado"),
											rx.table.column_header_cell("Estado"),
											rx.table.column_header_cell("Acciones", text_align="center"),
										)
									),
									rx.table.body(
										rx.foreach(OrderState.filtered_orders, desktop_order_row),

										# REFERENCIA: Ejemplo de estructura de datos hardcodeada
										# rx.table.row(
										# 	rx.table.row_header_cell("#12345", font_weight="bold"),
										# 	rx.table.cell("Av. Siempre Viva 742, Col. Centro, Colima"),
										# 	rx.table.cell("10/09/2025"),
										# 	rx.table.cell(
										# 		rx.hstack(
										# 			rx.icon("credit-card", size=16),
										# 			rx.text("Tarjeta crédito"),
										# 			spacing="1"
										# 		)
										# 	),
										# 	rx.table.cell("$1,746.50", font_weight="bold", color=rx.color_mode_cond(
										# 		light=Custom_theme().light_colors()["primary"],
										# 		dark=Custom_theme().dark_colors()["primary"]
										# 	)),
										# 	rx.table.cell(
										# 		rx.badge("Entregado", color_scheme="green")
										# 	),
										# 	rx.table.cell(
										# 		rx.hstack(
										# 			rx.button(
										# 				rx.icon("eye", size=16),
										# 				"Ver detalles",
										# 				size="2",
										# 				variant="soft",
										# 				color_scheme="blue",
										# 				on_click=lambda: rx.redirect("/order_details")
										# 			),
										# 			rx.button(
										# 				rx.icon("download", size=16),
										# 				"PDF",
										# 				size="2",
										# 				variant="outline",
										# 				color_scheme="gray"
										# 			),
										# 			spacing="2",
										# 			justify="center"
										# 		)
										# 	),
										# ),
									),
									width="100%",
									variant="surface"
								),
								bg=rx.color_mode_cond(
									light=Custom_theme().light_colors()["tertiary"],
									dark=Custom_theme().dark_colors()["tertiary"]
								),
								border_radius="24px",
								padding="24px",
								width="100%"
							),

							# Paginación
							rx.hstack(
								rx.text(
									f"Mostrando {OrderState.current_page_start}-{OrderState.current_page_end} de {OrderState.total_orders} órdenes",
								),
								rx.spacer(),
								rx.hstack(
									rx.button(
										rx.icon("chevron-left", size=16),
										"Anterior",
										variant="soft",
										disabled=OrderState.is_first_page,
										on_click=OrderState.prev_page
									),
									rx.text(
										f"Página {OrderState.current_page} de {OrderState.total_pages}",
										font_size="0.9em",
										color=rx.color("gray", 11)
									),
									rx.button(
										"Siguiente",
										rx.icon("chevron-right", size=16),
										variant="soft",
										disabled=OrderState.is_last_page,
										on_click=OrderState.next_page
									),
									spacing="2"
								),
								width="100%",
								margin_top="2em"
							),

							spacing="4",
							width="100%"
						)
					),
					width="100%"
				),
				align="end",
				margin_top="8em",
				margin_bottom="2em",
				max_width="1920px",
				width="100%"
			)
		),

		# Versión móvil
		rx.mobile_only(
			rx.vstack(
				# Header móvil
				mobile_header(),

				# Barra de búsqueda móvil
				rx.box(
					rx.input(
						rx.input.slot(
							rx.icon("search", size=24, color=rx.color("gray", 11)),
						),
						placeholder="Buscar orden...",
						variant="soft",
						border_radius="32px",
						width="100%",
						font_size="1em",
						height="auto",
						padding_y="8px",
						bg=rx.color_mode_cond(
							light=Custom_theme().light_colors()["traslucid-background"],
							dark=Custom_theme().dark_colors()["traslucid-background"]
						),
							value=OrderState.search_query,
							on_change=OrderState.set_search_query
					),
					backdrop_filter="blur(8px)",
					padding_x="1em",
					margin_top="80px",
					width="100%",
					z_index="1",
					position="fixed",
					box_shadow=rx.color_mode_cond(
						light=Custom_theme().light_colors()["box_shadow"],
						dark=Custom_theme().dark_colors()["box_shadow"]
					),
				),

				# Contenido principal móvil
				rx.vstack(

					# Filtros móvil
					rx.hstack(
						rx.select(
							["Todas", "Pendiente", "En proceso", "Enviado", "Entregado", "Cancelado"],
							placeholder="Estado",
							default_value="Todas",
							size="2",
							width="48%",
							radius="full",
								value=OrderState.status_filter,
								on_change=OrderState.set_status_filter
						),
						rx.select(
							["Más reciente", "Más antiguo"],
							placeholder="Ordenar",
							default_value="Más reciente",
							size="2",
							width="48%",
							radius="full",
								value=OrderState.sort_by,
								on_change=OrderState.set_sort_by
						),
						justify="between",
						width="100%",
						margin_bottom="1.5em"
					),

					# Lista de órdenes móvil (cards en lugar de tabla)
					rx.vstack(
						rx.foreach(OrderState.filtered_orders, mobile_order_card),
						height="100%",
						width="100%"
					),
					# Paginación móvil (comentada en original)
#					rx.hstack(
#						rx.button(
#							rx.icon("chevron-left", size=16),
#							variant="soft",
#							disabled=True,
#							size="2",
#							radius="full"
#						),
#						rx.text("1 de 4", font_size="0.9em"),
#						rx.button(
#							rx.icon("chevron-right", size=14),
#							variant="soft",
#							size="2",
#							radius="full"
#						),
#						align="center",
#						justify="center",
#						width="100%",
#						margin_top="1.5em"
#					),
					#spacing="4",
					width="100%",
					padding="1em",
					margin_top="140px",
					margin_bottom="0.2em",
				),
				#height="100vh",
			),
			height="100vh",
			width="100%"
		),
		# Propiedades del contenedor principal.
		bg=rx.color_mode_cond(
			light=Custom_theme().light_colors()["background"],
			dark=Custom_theme().dark_colors()["background"]
		),
		#position="absolute",
		width="100%",
		height="100%",
		on_mount=OrderState.load_orders
	)
