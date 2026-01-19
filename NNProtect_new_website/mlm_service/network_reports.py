"""Nueva Backoffice NN Protect | Reportes de Red"""

import reflex as rx
from ..shared_ui.theme import Custom_theme
from rxconfig import config
from ..shared_ui.layout import main_container_derecha, mobile_header, desktop_sidebar, mobile_sidebar, logged_in_user
from NNProtect_new_website.modules.auth.state.auth_state import AuthState
from .mlm_user_manager import MLMUserManager
from typing import List, Dict, Any

def format_date(date_obj) -> str:
    """Convierte objeto datetime a formato YYYY/MM/DD"""
    try:
        # Debug: ver qué tipo de objeto llega
        print(f"🔍 DEBUG fecha recibida: '{date_obj}' (tipo: {type(date_obj)})")
        
        if not date_obj:
            return "N/A"
        
        # Manejar diferentes tipos de entrada
        from datetime import datetime
        
        # Caso 1: Ya es un objeto datetime
        if isinstance(date_obj, datetime):
            return date_obj.strftime("%Y/%m/%d")
        
        # Caso 2: Es un string (fallback para otros casos)
        if isinstance(date_obj, str):
            if "T" in date_obj or "-" in date_obj:
                try:
                    parsed_date = datetime.fromisoformat(str(date_obj).replace("Z", ""))
                    return parsed_date.strftime("%Y/%m/%d")
                except:
                    pass
            
            if "/" in date_obj:
                parts = date_obj.split("/")
                if len(parts) == 3:
                    day, month, year = parts
                    return f"{year}/{month.zfill(2)}/{day.zfill(2)}"
        
        # Fallback: convertir a string y devolver
        return str(date_obj)
        
    except Exception as e:
        print(f"❌ Error parseando fecha '{date_obj}': {e}")
        return "N/A"

class NetworkReportsState(rx.State):
	"""State para manejar datos de reportes de red."""
	todays_registrations: List[Dict[str, Any]] = []
	monthly_registrations: List[Dict[str, Any]] = []
	all_registrations: List[Dict[str, Any]] = []
	is_loading: bool = False
	
	# Progresión de rango
	current_pvg: int = 0
	next_rank_pvg: int = 0
	
	# 🆕 Volúmenes por periodo - Variables individuales para compatibilidad con Reflex
	period_names: List[str] = ["N/A", "N/A", "N/A", "N/A", "N/A", "N/A"]
	pv_0: str = "0"
	pv_1: str = "0"
	pv_2: str = "0"
	pv_3: str = "0"
	pv_4: str = "0"
	pv_5: str = "0"
	level_1_0: str = "0"
	level_1_1: str = "0"
	level_1_2: str = "0"
	level_1_3: str = "0"
	level_1_4: str = "0"
	level_1_5: str = "0"
	level_2_0: str = "0"
	level_2_1: str = "0"
	level_2_2: str = "0"
	level_2_3: str = "0"
	level_2_4: str = "0"
	level_2_5: str = "0"
	level_3_0: str = "0"
	level_3_1: str = "0"
	level_3_2: str = "0"
	level_3_3: str = "0"
	level_3_4: str = "0"
	level_3_5: str = "0"
	level_4_0: str = "0"
	level_4_1: str = "0"
	level_4_2: str = "0"
	level_4_3: str = "0"
	level_4_4: str = "0"
	level_4_5: str = "0"
	level_5_0: str = "0"
	level_5_1: str = "0"
	level_5_2: str = "0"
	level_5_3: str = "0"
	level_5_4: str = "0"
	level_5_5: str = "0"
	level_6_0: str = "0"
	level_6_1: str = "0"
	level_6_2: str = "0"
	level_6_3: str = "0"
	level_6_4: str = "0"
	level_6_5: str = "0"
	level_7_0: str = "0"
	level_7_1: str = "0"
	level_7_2: str = "0"
	level_7_3: str = "0"
	level_7_4: str = "0"
	level_7_5: str = "0"
	level_8_0: str = "0"
	level_8_1: str = "0"
	level_8_2: str = "0"
	level_8_3: str = "0"
	level_8_4: str = "0"
	level_8_5: str = "0"
	level_9_0: str = "0"
	level_9_1: str = "0"
	level_9_2: str = "0"
	level_9_3: str = "0"
	level_9_4: str = "0"
	level_9_5: str = "0"

	@rx.var
	def today_registrations_count(self) -> str:
		"""Cuenta de inscripciones del día."""
		return str(len(self.todays_registrations))

	@rx.var
	def monthly_registrations_count(self) -> str:
		"""Cuenta de inscripciones del mes."""
		return str(len(self.monthly_registrations))
	
	@rx.var
	def all_registrations_count(self) -> str:
		"""Cuenta de todas las inscripciones (histórico completo)."""
		return str(len(self.all_registrations))
	
	@rx.event
	async def load_todays_registrations(self):
		"""Carga las inscripciones del día de la red del usuario autenticado."""
		self.is_loading = True
		yield
		
		try:
			# Obtener el member_id del usuario autenticado
			auth_state = await self.get_state(AuthState)
			
			# ✅ VALIDACIÓN SIMPLIFICADA - Solo lo necesario
			member_id = auth_state.profile_data.get("member_id") if auth_state.profile_data else None
			if not member_id:
				print("❌ Usuario no autenticado o member_id no encontrado")
				self.todays_registrations = []
				return
				
			print(f"🔄 Cargando inscripciones del día para member_id: {member_id}")
			
			# Obtener inscripciones del día de la red
			registrations = MLMUserManager.get_todays_registrations(member_id)
			self.todays_registrations = registrations
			
			print(f"✅ Cargadas {len(registrations)} inscripciones del día")
			
		except Exception as e:
			print(f"❌ Error cargando inscripciones: {e}")
			self.todays_registrations = []
		finally:
			self.is_loading = False

	@rx.event
	async def load_monthly_registrations(self):
		"""Carga las inscripciones del mes de la red del usuario autenticado."""
		self.is_loading = True
		yield
		
		try:
			# Obtener el member_id del usuario autenticado
			auth_state = await self.get_state(AuthState)
			
			# ✅ VALIDACIÓN SIMPLIFICADA - Solo lo necesario
			member_id = auth_state.profile_data.get("member_id") if auth_state.profile_data else None
			if not member_id:
				print("❌ Usuario no autenticado o member_id no encontrado")
				self.monthly_registrations = []
				return
				
			print(f"🔄 Cargando inscripciones del mes para member_id: {member_id}")
			
			# Obtener inscripciones del mes de la red
			registrations = MLMUserManager.get_monthly_registrations(member_id)
			self.monthly_registrations = registrations
			
			print(f"✅ Cargadas {len(registrations)} inscripciones del mes")
			
		except Exception as e:
			print(f"❌ Error cargando inscripciones del mes: {e}")
			self.monthly_registrations = []
		finally:
			self.is_loading = False

	@rx.event
	async def load_all_registrations(self):
		"""Carga TODAS las inscripciones de la red del usuario autenticado (histórico completo)."""
		self.is_loading = True
		yield
		
		try:
			# Obtener el member_id del usuario autenticado
			auth_state = await self.get_state(AuthState)
			
			# ✅ VALIDACIÓN SIMPLIFICADA - Solo lo necesario
			member_id = auth_state.profile_data.get("member_id") if auth_state.profile_data else None
			if not member_id:
				print("❌ Usuario no autenticado o member_id no encontrado")
				self.all_registrations = []
				return
				
			print(f"🔄 Cargando TODAS las inscripciones para member_id: {member_id}")
			
			# Obtener TODAS las inscripciones de la red (sin filtro de fecha)
			registrations = MLMUserManager.get_all_registrations(member_id)
			self.all_registrations = registrations
			
			print(f"✅ Cargadas {len(registrations)} inscripciones totales")
			
		except Exception as e:
			print(f"❌ Error cargando todas las inscripciones: {e}")
			self.all_registrations = []
		finally:
			self.is_loading = False

	@rx.event
	async def load_period_volumes(self):
		"""Carga volúmenes (PV/PVG) por periodo del usuario autenticado."""
		self.is_loading = True
		yield
		
		try:
			auth_state = await self.get_state(AuthState)
			member_id = auth_state.profile_data.get("member_id") if auth_state.profile_data else None
			
			if not member_id:
				print("❌ Usuario no autenticado o member_id no encontrado")
				return
				
			print(f"🔄 Cargando volúmenes por periodo para member_id: {member_id}")
			volumes = MLMUserManager.get_period_volumes(member_id)
			
			# Asignar valores individuales a las variables de estado
			self.period_names = volumes.get("period_names", ["N/A", "N/A", "N/A", "N/A", "N/A", "N/A"])
			self.pv_0 = volumes.get("pv_0", "0")
			self.pv_1 = volumes.get("pv_1", "0")
			self.pv_2 = volumes.get("pv_2", "0")
			self.pv_3 = volumes.get("pv_3", "0")
			self.pv_4 = volumes.get("pv_4", "0")
			self.pv_5 = volumes.get("pv_5", "0")
			
			# Niveles 1-9, períodos 0-5
			for level in range(1, 10):
				for period in range(6):
					setattr(self, f"level_{level}_{period}", volumes.get(f"level_{level}_{period}", "0"))
			
			print(f"✅ Cargados volúmenes de {len(self.period_names)} periodos")
			
		except Exception as e:
			print(f"❌ Error cargando volúmenes por periodo: {e}")
		finally:
			self.is_loading = False
	
	@rx.event
	async def load_rank_progression(self):
		"""Carga la progresión del usuario hacia el siguiente rango."""
		try:
			from database.user_rank_history import UserRankHistory
			from database.ranks import Ranks
			from database.users import Users
			from datetime import datetime, timezone
			import sqlmodel
			
			# Obtener member_id desde AuthState
			auth_state = await self.get_state(AuthState)
			profile_data = auth_state.profile_data
			
			# Validar que profile_data existe y tiene member_id
			if not isinstance(profile_data, dict) or "member_id" not in profile_data:
				print("⚠️  No se pudo obtener member_id del usuario")
				return
			
			member_id = profile_data["member_id"]
			
			with rx.session() as session:
				# Obtener PVG actual del usuario
				user = session.exec(
					sqlmodel.select(Users).where(Users.member_id == member_id)
				).first()
				
				if not user:
					print(f"⚠️  Usuario {member_id} no encontrado")
					return
				
				self.current_pvg = user.pvg_cache or 0
				
				# Obtener rank_id actual del mes
				now = datetime.now(timezone.utc)
				current_rank_history = session.exec(
					sqlmodel.select(UserRankHistory)
					.where(
						UserRankHistory.member_id == member_id,
						sqlmodel.extract('year', UserRankHistory.achieved_on) == now.year,
						sqlmodel.extract('month', UserRankHistory.achieved_on) == now.month
					)
					.order_by(sqlmodel.desc(UserRankHistory.rank_id))
				).first()
				
				current_rank_id = current_rank_history.rank_id if current_rank_history else 1
				
				# Obtener siguiente rango
				next_rank = session.exec(
					sqlmodel.select(Ranks)
					.where(Ranks.id == current_rank_id + 1)
					.order_by(Ranks.id)
				).first()
				
				if next_rank:
					self.next_rank_pvg = next_rank.pvg_required
				else:
					# Usuario está en el rango máximo
					current_rank = session.exec(
						sqlmodel.select(Ranks).where(Ranks.id == current_rank_id)
					).first()
					self.next_rank_pvg = current_rank.pvg_required if current_rank else 0
				
				print(f"📊 Progresión de rango - PVG: {self.current_pvg}/{self.next_rank_pvg}")
				
		except Exception as e:
			print(f"❌ Error cargando progresión de rango: {e}")
			import traceback
			traceback.print_exc()

def network_reports() -> rx.Component:
	"""Página de reportes de red"""
	return rx.center(
		# Contenedor principal centrado
		rx.desktop_only(
			# Solo se muestra en escritorio
			rx.vstack(
				logged_in_user(), # Muestra el usuario logueado en la esquina superior derecha
				# Contenedor vertical principal
				rx.hstack(
					# Contenedor horizontal para sidebar y contenido principal
					desktop_sidebar(),
					# Sidebar (menú lateral)
					main_container_derecha(
						# Contenedor principal de la derecha
						rx.vstack(
							# Contenedor vertical para el contenido de reportes
							# Encabezado de la página
							rx.text(
								"Reportes de Red",
								font_size="2rem",
								font_weight="bold",
								margin_bottom="0.1em"
							),
							
							# Secciones de detalles del usuario y patrocinador
							rx.hstack(
								# Sección de detalles del usuario
								rx.box(
									rx.vstack(
										rx.text(
											"Detalles personales",
											color="#FFFFFF",
											font_size="1.5rem",
											font_weight="bold",
											margin_bottom="1rem"
										),
										rx.hstack(
											# Primera columna - Etiquetas
											rx.vstack(
												rx.text("ID:", font_weight="bold", color="#FFFFFF"),
												rx.text("Nombre:", font_weight="bold", color="#FFFFFF"),
												rx.text("Rango actual:", font_weight="bold", color="#FFFFFF"),
												rx.text("Fecha de registro:", font_weight="bold", color="#FFFFFF"),
												align="start",
												spacing="3",
												width="50%"
											),
											# Segunda columna - Valores
											rx.vstack(
												rx.text(AuthState.profile_data.get("member_id"), color="#FFFFFF"),
												rx.text(AuthState.profile_data.get("full_name"), color="#FFFFFF"),
												rx.text(AuthState.profile_data.get("current_month_rank"), color="#FFFFFF"),
												rx.text(AuthState.profile_data.get("created_at"), color="#FFFFFF"),
												align="end",
												spacing="3",
												width="70%"
											),
											width="100%",
											align="stretch",
										),
										spacing="3",
										width="100%"
									),
									bg=rx.color_mode_cond(
										light=Custom_theme().light_colors()["secondary"],
										dark=Custom_theme().dark_colors()["secondary"]
									),
									border_radius="29px",
									padding="24px",
									width="50%",
									margin_right="1rem"
								),
								
								# Sección de detalles del patrocinador
								rx.box(
									rx.vstack(
										rx.text(
											"Detalles del Patrocinador",
											font_size="1.5rem",
											font_weight="bold",
											margin_bottom="1rem"
										),
										rx.hstack(
											# Primera columna - Etiquetas
											rx.vstack(
												rx.text("ID:", font_weight="bold"),
												rx.text("Patrocinador:", font_weight="bold"),
												rx.text("Rango:", font_weight="bold"),
												rx.text("Contacto:", font_weight="bold"),
												align="start",
												spacing="3",
												width="50%"
											),
											# Segunda columna - Valores
											rx.vstack(
												rx.text(AuthState.profile_data.get("sponsor_id", "N/A"), color=rx.color("gray", 11)),
												rx.text(AuthState.sponsor_data.get("full_name", "N/A"), color=rx.color("gray", 11)),
												rx.text(AuthState.sponsor_data.get("current_month_rank", "N/A"), color=rx.color("blue", 11)),
												rx.text(AuthState.sponsor_data.get("phone", "N/A"), color=rx.color("gray", 11)),
												align="end",
												spacing="3",
												width="50%"
											),
											width="100%",
											align="stretch",
										),
										spacing="3",
										width="100%"
									),
									bg=rx.color_mode_cond(
										light=Custom_theme().light_colors()["tertiary"],
										dark=Custom_theme().dark_colors()["tertiary"]
									),
									border_radius="29px",
									padding="24px",
									width="50%"
								),
								width="100%",
								align="stretch",
								margin_bottom="1.5rem"
							),
							
							# Sección de reporte de volumen
							rx.box(
								rx.vstack(
									rx.text(
										"Reporte de Volumen",
										font_size="1.5rem",
										font_weight="bold",
										margin_bottom="1rem"
									),
									# Métricas principales
									rx.hstack(
										rx.vstack(
											rx.text("Volumen personal:", font_weight="bold"),
											rx.text(AuthState.profile_data.get("pv_cache"), color="#32D74B", font_size="2rem"),
											align="center",
											spacing="1"
										),
										rx.vstack(
											rx.text("Volumen grupal:", font_weight="bold"),
											rx.text(f"{NetworkReportsState.current_pvg:,}", color="#0039F2", font_size="2rem"),
											align="center",
											spacing="1"
										),
										rx.vstack(
											rx.text("Siguiente rango:", font_weight="bold"),
											rx.text(f"{NetworkReportsState.next_rank_pvg:,}", color="#5E79FF", font_size="2rem"),
											align="center",
											spacing="1"
										),
										justify="between",
										width="100%"
									),
									rx.divider(),
									# Tabla de volúmenes - DATOS DINÁMICOS (se carga automáticamente en on_mount)
									rx.text("Detalle por niveles:", font_weight="bold", margin_bottom="0.5rem"),
									rx.cond(
										NetworkReportsState.period_names[0] != "Mes 1",
										rx.table.root(
											rx.table.header(
												rx.table.row(
													rx.table.column_header_cell("Nivel", align="left"),
													rx.table.column_header_cell(NetworkReportsState.period_names[0]),
													rx.table.column_header_cell(NetworkReportsState.period_names[1]),
													rx.table.column_header_cell(NetworkReportsState.period_names[2]),
													rx.table.column_header_cell(NetworkReportsState.period_names[3]),
													rx.table.column_header_cell(NetworkReportsState.period_names[4]),
													rx.table.column_header_cell(NetworkReportsState.period_names[5]),
													align="center",
												),
												text_align="center"
											),
											rx.table.body(
												# Volumen personal (PV)
												rx.table.row(
													rx.table.row_header_cell("Volumen personal", font_weight="bold", align="left"),
													rx.table.cell(NetworkReportsState.pv_0, color=rx.color("green", 11)),
													rx.table.cell(NetworkReportsState.pv_1, color=rx.color("gray", 11)),
													rx.table.cell(NetworkReportsState.pv_2, color=rx.color("gray", 11)),
													rx.table.cell(NetworkReportsState.pv_3, color=rx.color("gray", 11)),
													rx.table.cell(NetworkReportsState.pv_4, color=rx.color("gray", 11)),
													rx.table.cell(NetworkReportsState.pv_5, color=rx.color("gray", 11))
												),
												# Primer nivel
												rx.table.row(
													rx.table.row_header_cell("Primer nivel", font_weight="bold", align="left"),
													rx.table.cell(NetworkReportsState.level_1_0, color=rx.color("blue", 11)),
													rx.table.cell(NetworkReportsState.level_1_1, color=rx.color("gray", 11)),
													rx.table.cell(NetworkReportsState.level_1_2, color=rx.color("gray", 11)),
													rx.table.cell(NetworkReportsState.level_1_3, color=rx.color("gray", 11)),
													rx.table.cell(NetworkReportsState.level_1_4, color=rx.color("gray", 11)),
													rx.table.cell(NetworkReportsState.level_1_5, color=rx.color("gray", 11))
												),
												# Segundo nivel
												rx.table.row(
													rx.table.row_header_cell("Segundo nivel", font_weight="bold", align="left"),
													rx.table.cell(NetworkReportsState.level_2_0, color=rx.color("orange", 11)),
													rx.table.cell(NetworkReportsState.level_2_1, color=rx.color("gray", 11)),
													rx.table.cell(NetworkReportsState.level_2_2, color=rx.color("gray", 11)),
													rx.table.cell(NetworkReportsState.level_2_3, color=rx.color("gray", 11)),
													rx.table.cell(NetworkReportsState.level_2_4, color=rx.color("gray", 11)),
													rx.table.cell(NetworkReportsState.level_2_5, color=rx.color("gray", 11))
												),
												# Tercer nivel
												rx.table.row(
													rx.table.row_header_cell("Tercer nivel", font_weight="bold", align="left"),
													rx.table.cell(NetworkReportsState.level_3_0, color=rx.color("purple", 11)),
													rx.table.cell(NetworkReportsState.level_3_1, color=rx.color("gray", 11)),
													rx.table.cell(NetworkReportsState.level_3_2, color=rx.color("gray", 11)),
													rx.table.cell(NetworkReportsState.level_3_3, color=rx.color("gray", 11)),
													rx.table.cell(NetworkReportsState.level_3_4, color=rx.color("gray", 11)),
													rx.table.cell(NetworkReportsState.level_3_5, color=rx.color("gray", 11))
												),
												# Cuarto nivel
												rx.table.row(
													rx.table.row_header_cell("Cuarto nivel", font_weight="bold", align="left"),
													rx.table.cell(NetworkReportsState.level_4_0, color=rx.color("cyan", 11)),
													rx.table.cell(NetworkReportsState.level_4_1, color=rx.color("gray", 11)),
													rx.table.cell(NetworkReportsState.level_4_2, color=rx.color("gray", 11)),
													rx.table.cell(NetworkReportsState.level_4_3, color=rx.color("gray", 11)),
													rx.table.cell(NetworkReportsState.level_4_4, color=rx.color("gray", 11)),
													rx.table.cell(NetworkReportsState.level_4_5, color=rx.color("gray", 11))
												),
												# Quinto nivel
												rx.table.row(
													rx.table.row_header_cell("Quinto nivel", font_weight="bold", align="left"),
													rx.table.cell(NetworkReportsState.level_5_0, color=rx.color("pink", 11)),
													rx.table.cell(NetworkReportsState.level_5_1, color=rx.color("gray", 11)),
													rx.table.cell(NetworkReportsState.level_5_2, color=rx.color("gray", 11)),
													rx.table.cell(NetworkReportsState.level_5_3, color=rx.color("gray", 11)),
													rx.table.cell(NetworkReportsState.level_5_4, color=rx.color("gray", 11)),
													rx.table.cell(NetworkReportsState.level_5_5, color=rx.color("gray", 11))
												),
												# Sexto nivel
												rx.table.row(
													rx.table.row_header_cell("Sexto nivel", font_weight="bold", align="left"),
													rx.table.cell(NetworkReportsState.level_6_0, color=rx.color("indigo", 11)),
													rx.table.cell(NetworkReportsState.level_6_1, color=rx.color("gray", 11)),
													rx.table.cell(NetworkReportsState.level_6_2, color=rx.color("gray", 11)),
													rx.table.cell(NetworkReportsState.level_6_3, color=rx.color("gray", 11)),
													rx.table.cell(NetworkReportsState.level_6_4, color=rx.color("gray", 11)),
													rx.table.cell(NetworkReportsState.level_6_5, color=rx.color("gray", 11))
												),
												# Séptimo nivel
												rx.table.row(
													rx.table.row_header_cell("Séptimo nivel", font_weight="bold", align="left"),
													rx.table.cell(NetworkReportsState.level_7_0, color=rx.color("teal", 11)),
													rx.table.cell(NetworkReportsState.level_7_1, color=rx.color("gray", 11)),
													rx.table.cell(NetworkReportsState.level_7_2, color=rx.color("gray", 11)),
													rx.table.cell(NetworkReportsState.level_7_3, color=rx.color("gray", 11)),
													rx.table.cell(NetworkReportsState.level_7_4, color=rx.color("gray", 11)),
													rx.table.cell(NetworkReportsState.level_7_5, color=rx.color("gray", 11))
												),
												# Octavo nivel
												rx.table.row(
													rx.table.row_header_cell("Octavo nivel", font_weight="bold", align="left"),
													rx.table.cell(NetworkReportsState.level_8_0, color=rx.color("amber", 11)),
													rx.table.cell(NetworkReportsState.level_8_1, color=rx.color("gray", 11)),
													rx.table.cell(NetworkReportsState.level_8_2, color=rx.color("gray", 11)),
													rx.table.cell(NetworkReportsState.level_8_3, color=rx.color("gray", 11)),
													rx.table.cell(NetworkReportsState.level_8_4, color=rx.color("gray", 11)),
													rx.table.cell(NetworkReportsState.level_8_5, color=rx.color("gray", 11))
												),
												# Noveno nivel
												rx.table.row(
													rx.table.row_header_cell("Noveno nivel", font_weight="bold", align="left"),
													rx.table.cell(NetworkReportsState.level_9_0, color=rx.color("red", 11)),
													rx.table.cell(NetworkReportsState.level_9_1, color=rx.color("gray", 11)),
													rx.table.cell(NetworkReportsState.level_9_2, color=rx.color("gray", 11)),
													rx.table.cell(NetworkReportsState.level_9_3, color=rx.color("gray", 11)),
													rx.table.cell(NetworkReportsState.level_9_4, color=rx.color("gray", 11)),
													rx.table.cell(NetworkReportsState.level_9_5, color=rx.color("gray", 11))
												),
												text_align="center"
											),
											variant="surface",
											width="100%",
											border_radius="15px"
										),
										rx.text(
											"Haz clic en 'Cargar' para ver los volúmenes por periodo.",
											color=rx.color("gray", 11),
											text_align="center",
											padding="2rem"
										)
									),
									align="start",
									spacing="3",
									width="100%"
								),
								bg=rx.color_mode_cond(
									light=Custom_theme().light_colors()["tertiary"],
									dark=Custom_theme().dark_colors()["tertiary"]
								),
								border_radius="29px",
								padding="24px",
								width="100%",
								margin_top="1.5rem"
							),
							
							# Sección de inscripciones del equipo
							rx.box(
								rx.vstack(
									rx.text(
										"Equipo de negocio",
										font_size="1.5rem",
										font_weight="bold",
										margin_bottom="1rem"
									),
									rx.hstack(
										rx.vstack(
											rx.text("Total de miembros:", font_weight="bold"),
											rx.text(NetworkReportsState.all_registrations_count, color=rx.color("blue", 11), font_size="2rem"),
											align="center",
											spacing="1"
										),
										rx.vstack(
											rx.text("Nuevos este mes:", font_weight="bold"),
											rx.text(NetworkReportsState.monthly_registrations_count, color=rx.color("green", 11), font_size="2rem"),
											align="center",
											spacing="1"
										),
										rx.vstack(
											rx.text("Activos:", font_weight="bold"),
											rx.text("42", color=rx.color("orange", 11), font_size="2rem"),
											align="center",
											spacing="1"
										),
										justify="between",
										width="100%"
									),
									rx.divider(),
									# Tabla de inscripciones del mes
									rx.text("Inscripciones del mes:", font_weight="bold", margin_bottom="0.5rem"),
									rx.cond(
										NetworkReportsState.is_loading,
										rx.spinner(loading=True, size="2"),
										rx.cond(
											NetworkReportsState.monthly_registrations,
											rx.table.root(
												rx.table.header(
													rx.table.row(
														rx.table.column_header_cell("Nombre", align="left"),
														rx.table.column_header_cell("ID socio"),
														rx.table.column_header_cell("Contacto"),
														rx.table.column_header_cell("Volumen personal"),
														rx.table.column_header_cell("Nivel"),
														rx.table.column_header_cell("Fecha de inscripción"),
														rx.table.column_header_cell("Patrocinador"),
														rx.table.column_header_cell("ID patrocinador"),
														rx.table.column_header_cell("Estado"),
														align="center",
													),
													text_align="center"
												),
												rx.table.body(
													rx.foreach(
														NetworkReportsState.monthly_registrations,
														lambda user: rx.table.row(
															rx.table.row_header_cell(user["full_name"], align="left"),
															rx.table.cell(user["member_id"]),
															rx.table.cell(user["phone"]),
															rx.table.cell("2000"),  # Volumen personal (placeholder)
															rx.table.cell(user["level"]),  # ✅ Nivel real del usuario
															rx.table.cell(user["created_at"]),
															rx.table.cell(user["sponsor_full_name"]),
															rx.table.cell(user["sponsor_member_id"]),
															rx.table.cell(rx.cond(user["status"] == "active", rx.badge("Activo", color_scheme="green"), rx.badge("Inactivo", color_scheme="red"))),
															align="center"
														),
													),
													text_align="center",
												),
												width="100%"
											),
											rx.text(
												"No hay inscripciones del día en tu red",
												font_style="italic",
												color="gray",
												text_align="center",
												padding="2rem"
											)
										)
									),
									align="start",
									spacing="3",
									width="100%"
								),
								bg=rx.color_mode_cond(
									light=Custom_theme().light_colors()["tertiary"],
									dark=Custom_theme().dark_colors()["tertiary"]
								),
								border_radius="29px",
								padding="24px",
								width="100%",
								margin_top="1.5rem"
							),
							
							# Propiedades del vstack principal
							width="100%",
						),
					),
					width="100%",
				),
				# Propiedades vstack que contiene el contenido de la página
				align="end",
				margin_top="8em",
				margin_bottom="2em",
				max_width="1920px",
				width="100%",
			),
			#width="100%",
		),
		
		# Versión móvil
		rx.mobile_only(
			# Encabezado de la página móvil
			mobile_header(),
			rx.vstack(				
				# Sección de detalles del usuario (móvil)
				rx.box(
					rx.vstack(
						rx.text(
							"Detalles personales",
							color="#FFFFFF",
							font_size="1.2rem",
							font_weight="bold",
							margin_bottom="0.8rem",
							text_align="center"
						),
						rx.vstack(
							rx.hstack(
								rx.text("ID de Usuario:", font_weight="bold", color="#FFFFFF", font_size="0.9rem"),
								rx.text(AuthState.profile_data.get("member_id"), color="#FFFFFF", font_size="0.9rem"),
								justify="between",
								width="100%"
							),
							rx.hstack(
								rx.text("Nombre:", font_weight="bold", color="#FFFFFF", font_size="0.9rem"),
								rx.text(AuthState.profile_data.get("full_name"), color="#FFFFFF", font_size="0.9rem"),
								justify="between",
								width="100%"
							),
							rx.hstack(
								rx.text("Rango actual:", font_weight="bold", color="#FFFFFF", font_size="0.9rem"),
								rx.text(AuthState.profile_data.get("current_month_rank"), color="#FFFFFF", font_size="0.9rem"),
								justify="between",
								width="100%"
							),
							rx.hstack(
								rx.text("Fecha de registro:", font_weight="bold", color="#FFFFFF", font_size="0.9rem"),
								rx.text(AuthState.profile_data.get("created_at"), color="#FFFFFF", font_size="0.9rem"),
								justify="between",
								width="100%"
							),
							spacing="2",
							width="100%"
						),
						spacing="2",
						width="100%"
					),
					bg=rx.color_mode_cond(
						light=Custom_theme().light_colors()["secondary"],
						dark=Custom_theme().dark_colors()["secondary"]
					),
					border_radius="29px",
					padding="16px",
					width="100%",
					margin_bottom="1rem"
				),
				
				# Sección de detalles del patrocinador (móvil)
				rx.box(
					rx.vstack(
						rx.text(
							"Detalles del Patrocinador",
							font_size="1.2rem",
							font_weight="bold",
							margin_bottom="0.8rem",
							text_align="center"
						),
						rx.vstack(
							rx.hstack(
								rx.text("ID:", font_weight="bold", font_size="0.9rem"),
								rx.text(AuthState.profile_data.get("sponsor_id", "N/A"), color=rx.color("gray", 11), font_size="0.9rem"),
								justify="between",
								width="100%"
							),
							rx.hstack(
								rx.text("Nombre:", font_weight="bold", font_size="0.9rem"),
								rx.text(AuthState.sponsor_data.get("full_name", "N/A"), color=rx.color("gray", 11), font_size="0.9rem"),
								justify="between",
								width="100%"
							),
							rx.hstack(
								rx.text("Rango:", font_weight="bold", font_size="0.9rem"),
								rx.text(AuthState.sponsor_data.get("current_month_rank", "N/A"), color=rx.color("blue", 11), font_size="0.9rem"),
								justify="between",
								width="100%"
							),
							rx.hstack(
								rx.text("Contacto:", font_weight="bold", font_size="0.9rem"),
								rx.text(AuthState.sponsor_data.get("phone", "N/A"), color=rx.color("gray", 11), font_size="0.9rem"),
								justify="between",
								width="100%"
							),
							spacing="2",
							width="100%"
						),
						spacing="2",
						width="100%"
					),
					bg=rx.color_mode_cond(
						light=Custom_theme().light_colors()["tertiary"],
						dark=Custom_theme().dark_colors()["tertiary"]
					),
					border_radius="29px",
					padding="16px",
					width="100%",
					margin_bottom="1rem"
				),

				# Sección de reporte de volumen (móvil)
				rx.box(
					rx.vstack(
						rx.text(
							"Reporte de Volumen",
							font_size="1.2rem",
							font_weight="bold",
							margin_bottom="0.8rem",
							text_align="center"
						),
						# Métricas principales en móvil
						rx.vstack(
							rx.hstack(
								rx.text("Volumen personal:", font_weight="bold", font_size="0.9rem"),
								rx.text(AuthState.profile_data.get("pv_cache", 0), color="#32D74B", font_size="1.2rem", font_weight="bold"),
								justify="between",
								width="100%"
							),
							rx.hstack(
								rx.text("Volumen grupal:", font_weight="bold", font_size="0.9rem"),
								rx.text(f"{NetworkReportsState.current_pvg:,}", color="#0039F2", font_size="1.2rem", font_weight="bold"),
								justify="between",
								width="100%"
							),
							rx.hstack(
								rx.text("Siguiente rango:", font_weight="bold", font_size="0.9rem"),
								rx.text(f"{NetworkReportsState.next_rank_pvg:,}", color="#5E79FF", font_size="1.2rem", font_weight="bold"),
								justify="between",
								width="100%"
							),
							spacing="2",
							width="100%"
						),
						rx.divider(),
						# Tabla completa de niveles móvil con scroll horizontal - DATOS DINÁMICOS
						rx.text("Detalle por niveles:", font_weight="bold", font_size="0.9rem", margin_bottom="0.5rem"),
						rx.cond(
							NetworkReportsState.period_names[0] != "Mes 1",
							rx.box(
								rx.scroll_area(
									rx.table.root(
										rx.table.header(
											rx.table.row(
												rx.table.column_header_cell("Nivel", align="left", min_width="100px"),
												rx.table.column_header_cell(NetworkReportsState.period_names[0], min_width="90px"),
												rx.table.column_header_cell(NetworkReportsState.period_names[1], min_width="80px"),
												rx.table.column_header_cell(NetworkReportsState.period_names[2], min_width="80px"),
												rx.table.column_header_cell(NetworkReportsState.period_names[3], min_width="80px"),
												rx.table.column_header_cell(NetworkReportsState.period_names[4], min_width="80px"),
												rx.table.column_header_cell(NetworkReportsState.period_names[5], min_width="80px"),
												text_align="center",
												align="center",
											),
										),
										rx.table.body(
											# Volumen personal
											rx.table.row(
												rx.table.row_header_cell("Volumen personal", font_weight="bold", font_size="0.8rem", min_width="100px", align="left"),
												rx.table.cell(NetworkReportsState.pv_0, color=rx.color("green", 11), font_size="0.8rem", font_weight="bold", min_width="90px", text_align="center"),
												rx.table.cell(NetworkReportsState.pv_1, color=rx.color("gray", 11), font_size="0.8rem", min_width="80px", text_align="center"),
												rx.table.cell(NetworkReportsState.pv_2, color=rx.color("gray", 11), font_size="0.8rem", min_width="80px", text_align="center"),
												rx.table.cell(NetworkReportsState.pv_3, color=rx.color("gray", 11), font_size="0.8rem", min_width="80px", text_align="center"),
												rx.table.cell(NetworkReportsState.pv_4, color=rx.color("gray", 11), font_size="0.8rem", min_width="80px", text_align="center"),
												rx.table.cell(NetworkReportsState.pv_5, color=rx.color("gray", 11), font_size="0.8rem", min_width="80px", text_align="center"),
												align="center"
											),
											# Primer nivel
											rx.table.row(
												rx.table.row_header_cell("Primero", font_weight="bold", font_size="0.8rem", min_width="100px", align="left"),
												rx.table.cell(NetworkReportsState.level_1_0, color=rx.color("blue", 11), font_size="0.8rem", font_weight="bold", min_width="90px", text_align="center"),
												rx.table.cell(NetworkReportsState.level_1_1, color=rx.color("gray", 11), font_size="0.8rem", min_width="80px", text_align="center"),
												rx.table.cell(NetworkReportsState.level_1_2, color=rx.color("gray", 11), font_size="0.8rem", min_width="80px", text_align="center"),
												rx.table.cell(NetworkReportsState.level_1_3, color=rx.color("gray", 11), font_size="0.8rem", min_width="80px", text_align="center"),
												rx.table.cell(NetworkReportsState.level_1_4, color=rx.color("gray", 11), font_size="0.8rem", min_width="80px", text_align="center"),
												rx.table.cell(NetworkReportsState.level_1_5, color=rx.color("gray", 11), font_size="0.8rem", min_width="80px", text_align="center"),
												align="center"
											),
											# Segundo nivel
											rx.table.row(
												rx.table.row_header_cell("Segundo", font_weight="bold", font_size="0.8rem", min_width="100px", align="left"),
												rx.table.cell(NetworkReportsState.level_2_0, color=rx.color("orange", 11), font_size="0.8rem", font_weight="bold", min_width="90px", text_align="center"),
												rx.table.cell(NetworkReportsState.level_2_1, color=rx.color("gray", 11), font_size="0.8rem", min_width="80px", text_align="center"),
												rx.table.cell(NetworkReportsState.level_2_2, color=rx.color("gray", 11), font_size="0.8rem", min_width="80px", text_align="center"),
												rx.table.cell(NetworkReportsState.level_2_3, color=rx.color("gray", 11), font_size="0.8rem", min_width="80px", text_align="center"),
												rx.table.cell(NetworkReportsState.level_2_4, color=rx.color("gray", 11), font_size="0.8rem", min_width="80px", text_align="center"),
												rx.table.cell(NetworkReportsState.level_2_5, color=rx.color("gray", 11), font_size="0.8rem", min_width="80px", text_align="center"),
												align="center"
											),
											# Tercer nivel
											rx.table.row(
												rx.table.row_header_cell("Tercero", font_weight="bold", font_size="0.8rem", min_width="100px", align="left"),
												rx.table.cell(NetworkReportsState.level_3_0, color=rx.color("purple", 11), font_size="0.8rem", font_weight="bold", min_width="90px", text_align="center"),
												rx.table.cell(NetworkReportsState.level_3_1, color=rx.color("gray", 11), font_size="0.8rem", min_width="80px", text_align="center"),
												rx.table.cell(NetworkReportsState.level_3_2, color=rx.color("gray", 11), font_size="0.8rem", min_width="80px", text_align="center"),
												rx.table.cell(NetworkReportsState.level_3_3, color=rx.color("gray", 11), font_size="0.8rem", min_width="80px", text_align="center"),
												rx.table.cell(NetworkReportsState.level_3_4, color=rx.color("gray", 11), font_size="0.8rem", min_width="80px", text_align="center"),
												rx.table.cell(NetworkReportsState.level_3_5, color=rx.color("gray", 11), font_size="0.8rem", min_width="80px", text_align="center"),
												align="center"
											),
											# Cuarto nivel
											rx.table.row(
												rx.table.row_header_cell("Cuarto", font_weight="bold", font_size="0.8rem", min_width="100px", align="left"),
												rx.table.cell(NetworkReportsState.level_4_0, color=rx.color("cyan", 11), font_size="0.8rem", font_weight="bold", min_width="90px", text_align="center"),
												rx.table.cell(NetworkReportsState.level_4_1, color=rx.color("gray", 11), font_size="0.8rem", min_width="80px", text_align="center"),
												rx.table.cell(NetworkReportsState.level_4_2, color=rx.color("gray", 11), font_size="0.8rem", min_width="80px", text_align="center"),
												rx.table.cell(NetworkReportsState.level_4_3, color=rx.color("gray", 11), font_size="0.8rem", min_width="80px", text_align="center"),
												rx.table.cell(NetworkReportsState.level_4_4, color=rx.color("gray", 11), font_size="0.8rem", min_width="80px", text_align="center"),
												rx.table.cell(NetworkReportsState.level_4_5, color=rx.color("gray", 11), font_size="0.8rem", min_width="80px", text_align="center"),
												align="center"
											),
											# Quinto nivel
											rx.table.row(
												rx.table.row_header_cell("Quinto", font_weight="bold", font_size="0.8rem", min_width="100px", align="left"),
												rx.table.cell(NetworkReportsState.level_5_0, color=rx.color("pink", 11), font_size="0.8rem", font_weight="bold", min_width="90px", text_align="center"),
												rx.table.cell(NetworkReportsState.level_5_1, color=rx.color("gray", 11), font_size="0.8rem", min_width="80px", text_align="center"),
												rx.table.cell(NetworkReportsState.level_5_2, color=rx.color("gray", 11), font_size="0.8rem", min_width="80px", text_align="center"),
												rx.table.cell(NetworkReportsState.level_5_3, color=rx.color("gray", 11), font_size="0.8rem", min_width="80px", text_align="center"),
												rx.table.cell(NetworkReportsState.level_5_4, color=rx.color("gray", 11), font_size="0.8rem", min_width="80px", text_align="center"),
												rx.table.cell(NetworkReportsState.level_5_5, color=rx.color("gray", 11), font_size="0.8rem", min_width="80px", text_align="center"),
												align="center"
											),
											# Sexto nivel
											rx.table.row(
												rx.table.row_header_cell("Sexto", font_weight="bold", font_size="0.8rem", min_width="100px", align="left"),
												rx.table.cell(NetworkReportsState.level_6_0, color=rx.color("indigo", 11), font_size="0.8rem", font_weight="bold", min_width="90px", text_align="center"),
												rx.table.cell(NetworkReportsState.level_6_1, color=rx.color("gray", 11), font_size="0.8rem", min_width="80px", text_align="center"),
												rx.table.cell(NetworkReportsState.level_6_2, color=rx.color("gray", 11), font_size="0.8rem", min_width="80px", text_align="center"),
												rx.table.cell(NetworkReportsState.level_6_3, color=rx.color("gray", 11), font_size="0.8rem", min_width="80px", text_align="center"),
												rx.table.cell(NetworkReportsState.level_6_4, color=rx.color("gray", 11), font_size="0.8rem", min_width="80px", text_align="center"),
												rx.table.cell(NetworkReportsState.level_6_5, color=rx.color("gray", 11), font_size="0.8rem", min_width="80px", text_align="center"),
												align="center"
											),
											# Séptimo nivel
											rx.table.row(
												rx.table.row_header_cell("Séptimo", font_weight="bold", font_size="0.8rem", min_width="100px", align="left"),
												rx.table.cell(NetworkReportsState.level_7_0, color=rx.color("teal", 11), font_size="0.8rem", font_weight="bold", min_width="90px", text_align="center"),
												rx.table.cell(NetworkReportsState.level_7_1, color=rx.color("gray", 11), font_size="0.8rem", min_width="80px", text_align="center"),
												rx.table.cell(NetworkReportsState.level_7_2, color=rx.color("gray", 11), font_size="0.8rem", min_width="80px", text_align="center"),
												rx.table.cell(NetworkReportsState.level_7_3, color=rx.color("gray", 11), font_size="0.8rem", min_width="80px", text_align="center"),
												rx.table.cell(NetworkReportsState.level_7_4, color=rx.color("gray", 11), font_size="0.8rem", min_width="80px", text_align="center"),
												rx.table.cell(NetworkReportsState.level_7_5, color=rx.color("gray", 11), font_size="0.8rem", min_width="80px", text_align="center"),
												align="center"
											),
											# Octavo nivel
											rx.table.row(
												rx.table.row_header_cell("Octavo", font_weight="bold", font_size="0.8rem", min_width="100px", align="left"),
												rx.table.cell(NetworkReportsState.level_8_0, color=rx.color("amber", 11), font_size="0.8rem", font_weight="bold", min_width="90px", text_align="center"),
												rx.table.cell(NetworkReportsState.level_8_1, color=rx.color("gray", 11), font_size="0.8rem", min_width="80px", text_align="center"),
												rx.table.cell(NetworkReportsState.level_8_2, color=rx.color("gray", 11), font_size="0.8rem", min_width="80px", text_align="center"),
												rx.table.cell(NetworkReportsState.level_8_3, color=rx.color("gray", 11), font_size="0.8rem", min_width="80px", text_align="center"),
												rx.table.cell(NetworkReportsState.level_8_4, color=rx.color("gray", 11), font_size="0.8rem", min_width="80px", text_align="center"),
												rx.table.cell(NetworkReportsState.level_8_5, color=rx.color("gray", 11), font_size="0.8rem", min_width="80px", text_align="center"),
												align="center"
											),
											# Noveno nivel
											rx.table.row(
												rx.table.row_header_cell("Noveno", font_weight="bold", font_size="0.8rem", min_width="100px", align="left"),
												rx.table.cell(NetworkReportsState.level_9_0, color=rx.color("red", 11), font_size="0.8rem", font_weight="bold", min_width="90px", text_align="center"),
												rx.table.cell(NetworkReportsState.level_9_1, color=rx.color("gray", 11), font_size="0.8rem", min_width="80px", text_align="center"),
												rx.table.cell(NetworkReportsState.level_9_2, color=rx.color("gray", 11), font_size="0.8rem", min_width="80px", text_align="center"),
												rx.table.cell(NetworkReportsState.level_9_3, color=rx.color("gray", 11), font_size="0.8rem", min_width="80px", text_align="center"),
												rx.table.cell(NetworkReportsState.level_9_4, color=rx.color("gray", 11), font_size="0.8rem", min_width="80px", text_align="center"),
												rx.table.cell(NetworkReportsState.level_9_5, color=rx.color("gray", 11), font_size="0.8rem", min_width="80px", text_align="center"),
												align="center"
											),
										),
										variant="surface",
										border_radius="15px",
										min_width="590px",
										font_size="0.8rem",
										size="1"
									),
								# Configuración del scroll area siguiendo patrón de store.py
								scrollbars="horizontal",  # Solo scroll horizontal
								type="scroll",  # Aparece al hacer scroll
								height="auto",  # Altura automática
								width="100%",  # Ancho completo
								padding="0",  # Sin padding extra
							),
								# Indicador visual de scroll horizontal
								rx.hstack(
									rx.box(
										width="25px",
										height="3px",
										bg=rx.color_mode_cond(
											light="rgba(0,0,0,0.2)",
											dark="rgba(255,255,255,0.3)"
										),
										border_radius="2px",
										opacity="0.5"
									),
									rx.box(
										width="40px",
										height="3px",
										bg=rx.color_mode_cond(
											light=Custom_theme().light_colors()["primary"],
											dark=Custom_theme().dark_colors()["primary"]
										),
										border_radius="2px"
									),
									rx.box(
										width="25px",
										height="3px",
										bg=rx.color_mode_cond(
											light="rgba(0,0,0,0.2)",
											dark="rgba(255,255,255,0.3)"
										),
										border_radius="2px",
										opacity="0.5"
									),
									spacing="1",
									justify="center",
									margin_top="0.5rem"
								),
								width="100%"
							),
							# Mensaje si no hay datos cargados
							rx.text(
								"Cargando datos...",
								color=rx.color("gray", 11),
								font_size="0.8rem",
								text_align="center",
								padding="2rem"
							),
						),
						spacing="2",
						width="100%"
					),
					bg=rx.color_mode_cond(
						light=Custom_theme().light_colors()["tertiary"],
						dark=Custom_theme().dark_colors()["tertiary"]
					),
					border_radius="29px",
					padding="16px",
					width="100%",
					margin_bottom="0.4em",
				),
				
				# Sección de equipo de negocio (móvil) - ACTUALIZADA
				rx.box(
					rx.vstack(
						rx.text(
							"Equipo de negocio",
							font_size="1.2rem",
							font_weight="bold",
							margin_bottom="0.8rem",
							text_align="center"
						),
						# Métricas del equipo en móvil
						rx.vstack(
							rx.hstack(
								rx.text("Total de miembros:", font_weight="bold", font_size="0.9rem"),
								rx.text(NetworkReportsState.all_registrations_count, color=rx.color("blue", 11), font_size="1.5rem", font_weight="bold"),
								justify="between",
								width="100%"
							),
							rx.hstack(
								rx.text("Nuevos este mes:", font_weight="bold", font_size="0.9rem"),
								rx.text(NetworkReportsState.monthly_registrations_count, color=rx.color("green", 11), font_size="1.5rem", font_weight="bold"),
								justify="between",
								width="100%"
							),
							rx.hstack(
								rx.text("Activos:", font_weight="bold", font_size="0.9rem"),
								rx.text("42", color=rx.color("orange", 11), font_size="1.5rem", font_weight="bold"),
								justify="between",
								width="100%"
							),
							spacing="2",
							width="100%"
						),
						rx.divider(),
						# Tabla de inscripciones del mes móvil con scroll horizontal
						rx.text("Inscripciones del mes:", font_weight="bold", font_size="0.9rem", margin_bottom="0.5rem"),
						rx.cond(
							NetworkReportsState.is_loading,
							rx.spinner(loading=True, size="2"),
							rx.cond(
								NetworkReportsState.monthly_registrations,
								rx.box(
									rx.scroll_area(
										rx.table.root(
											rx.table.header(
												rx.table.row(
													rx.table.column_header_cell("Nombre", align="left", min_width="120px"),
													rx.table.column_header_cell("ID", min_width="80px"),
													rx.table.column_header_cell("Contacto", min_width="120px"),
													rx.table.column_header_cell("Vol.", min_width="70px"),
													rx.table.column_header_cell("Nivel", min_width="60px"),
													rx.table.column_header_cell("Fecha", min_width="90px"),
													rx.table.column_header_cell("Patrocinador", min_width="120px"),
													rx.table.column_header_cell("ID Patrocinador", min_width="80px"),
													rx.table.column_header_cell("Estado", min_width="80px"),
													align="center",
													text_align="center",
												),
											),
											rx.table.body(
												rx.foreach(
													NetworkReportsState.monthly_registrations,
													lambda user: rx.table.row(
														rx.table.row_header_cell(
															user["full_name"], 
															align="left",
															font_size="0.8rem",
															min_width="120px"
														),
														rx.table.cell(
															user["member_id"],
															font_size="0.8rem",
															min_width="80px",
															text_align="center"
														),
														rx.table.cell(
															user["phone"],
															font_size="0.8rem",
															min_width="120px",
															text_align="center"
														),
														rx.table.cell(
															user["pv_cache"],
															font_size="0.8rem",
															color=rx.color("green", 11),
															min_width="70px",
															text_align="center"
														),
														rx.table.cell(
															user["level"],
															font_size="0.8rem",
															color=rx.color("blue", 11),
															font_weight="bold",
															min_width="60px",
															text_align="center"
														),
														rx.table.cell(
															user["created_at"],
															font_size="0.8rem",
															min_width="90px",
															text_align="center"
														),
														rx.table.cell(
															user["sponsor_full_name"],
															font_size="0.8rem",
															min_width="120px",
															text_align="center"
														),
														rx.table.cell(
															user["sponsor_member_id"],
															font_size="0.8rem",
															min_width="80px",
															text_align="center"
														),
														rx.table.cell(
															rx.cond(
																user["status"] == "active", 
																rx.badge("Activo", color_scheme="green", size="1"), 
																rx.badge("Inactivo", color_scheme="red", size="1")
															),
															min_width="80px",
															text_align="center"
														),
														align="center"
													),
												),
											),
											min_width="800px",  # Ancho mínimo para todas las columnas
											font_size="0.8rem",
											size="1"
										),
										# Configuración del scroll area siguiendo patrón de store.py
										scrollbars="horizontal",  # Scroll horizontal
										type="scroll",  # Aparece al hacer scroll
										height="auto",  # Altura automática
										width="100%",  # Ancho completo
										padding="0",  # Sin padding extra
									),
									# Indicador visual de scroll horizontal
									rx.hstack(
										rx.box(
											width="30px",
											height="3px",
											bg=rx.color_mode_cond(
												light="rgba(0,0,0,0.2)",
												dark="rgba(255,255,255,0.3)"
											),
											border_radius="2px",
											opacity="0.5"
										),
										rx.box(
											width="20px",
											height="3px",
											bg=rx.color_mode_cond(
												light=Custom_theme().light_colors()["primary"],
												dark=Custom_theme().dark_colors()["primary"]
											),
											border_radius="2px"
										),
										rx.box(
											width="30px",
											height="3px",
											bg=rx.color_mode_cond(
												light="rgba(0,0,0,0.2)",
												dark="rgba(255,255,255,0.3)"
											),
											border_radius="2px",
											opacity="0.5"
										),
										spacing="1",
										justify="center",
										margin_top="0.5rem"
									),
									width="100%"
								),
								rx.text(
									"No hay inscripciones del mes en tu red",
									font_style="italic",
									color="gray",
									text_align="center",
									padding="2rem",
									font_size="0.9rem"
								)
							)
						),
						spacing="3",
						width="100%"
					),
					bg=rx.color_mode_cond(
						light=Custom_theme().light_colors()["tertiary"],
						dark=Custom_theme().dark_colors()["tertiary"]
					),
					border_radius="29px",
					padding="16px",
					width="100%",
					margin_bottom="1rem"
				),
				# Propiedades del vstack móvil
				margin_top="80px",
				padding="1em",
			),
			width="100%",
		),
		on_mount=[
			NetworkReportsState.load_all_registrations,
			NetworkReportsState.load_period_volumes,
			NetworkReportsState.load_rank_progression
		],
		bg=rx.color_mode_cond(
			light=Custom_theme().light_colors()["background"],
			dark=Custom_theme().dark_colors()["background"]
		),
		position="absolute",
		width="100%",
	)