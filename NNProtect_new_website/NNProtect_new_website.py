"""Nueva Backoffice NN Protect | Dashboard"""

import reflex as rx

# --- Pages ---
# MLM Service
from .modules.network.pages.network import network
from .modules.network.pages.network_reports import network_reports
from .modules.network.pages.income_reports import income_reports

# Auth Service
from .modules.auth.pages.login import login
from .modules.auth.pages.new_register import register
from .modules.auth.pages.register_noSponsor import register_noSponsor
from .modules.auth.pages.welcome_page import welcome_page

# Product Service
from .modules.store.pages.store import store
from .modules.store.pages.shopping_cart import shopping_cart

# Order Service
from .modules.store.pages.orders import orders
from .modules.store.pages.order_details import order_details
from .modules.store.pages.order_confirmation import order_confirmation
from .modules.store.pages.shipment import shipment_method

# Finance Service
from .modules.finance.pages.withdrawals import withdrawals
from .modules.finance.pages.new_withdrawal import new_withdrawal

# Payment Service
from .modules.store.pages.payment import payment

# Admin App
from .Admin_app.admin_page import admin_page

# --- Components ---
from .components.shared_ui.layout import main_container_derecha, mobile_header, desktop_sidebar, mobile_sidebar, header
from .components.shared_ui.theme import Custom_theme
from .status_bar import pwa_meta_tags, wrap_page_with_statusbar  # ← NUEVO IMPORT
from rxconfig import config

from .modules.auth.state.auth_state import AuthState

# Removed wildcard import to fix "Table already exists" warnings
from database import initialize_database
from database.users import Users, UserStatus
import sqlmodel
from datetime import datetime, timezone

# Importar SchedulerService para tareas automáticas
from .modules.network.backend.scheduler_service import SchedulerService


class DashboardState(rx.State):
    """Estado para el dashboard con datos dinámicos de usuarios."""
    
    # Contadores de usuarios
    qualified_count: int = 0
    non_qualified_count: int = 0
    total_users: int = 0
    
    # Porcentajes para las barras
    qualified_percentage: float = 0.0
    non_qualified_percentage: float = 0.0
    
    # Progresión de rango
    current_pvg: int = 0
    next_rank_pvg: int = 0
    rank_progress_percentage: int = 0
    
    # Proyección de ganancias mensuales
    estimated_monthly_earnings: float = 0.0
    estimated_earnings_currency: str = "MXN"
    
    def load_user_stats(self):
        """Carga estadísticas de usuarios desde la base de datos."""
        try:
            with rx.session() as session:
                # Contar usuarios calificados
                self.qualified_count = session.exec(
                    sqlmodel.select(sqlmodel.func.count(Users.id))
                    .where(Users.status == UserStatus.QUALIFIED)
                ).first() or 0
                
                # Contar usuarios no calificados
                self.non_qualified_count = session.exec(
                    sqlmodel.select(sqlmodel.func.count(Users.id))
                    .where(Users.status == UserStatus.NO_QUALIFIED)
                ).first() or 0
                
                # Total de usuarios
                self.total_users = self.qualified_count + self.non_qualified_count
                
                # Calcular porcentajes
                if self.total_users > 0:
                    self.qualified_percentage = (self.qualified_count / self.total_users) * 100
                    self.non_qualified_percentage = (self.non_qualified_count / self.total_users) * 100
                else:
                    self.qualified_percentage = 0.0
                    self.non_qualified_percentage = 0.0
                
                print(f"📊 Usuarios cargados - Calificados: {self.qualified_count}, No calificados: {self.non_qualified_count}")
                
        except Exception as e:
            print(f"❌ Error cargando estadísticas de usuarios: {e}")
            import traceback
            traceback.print_exc()
    
    async def load_rank_progression(self):
        """
        Carga la progresión del usuario hacia el siguiente rango.
        
        ACTUALIZADO: Ahora también dispara el recálculo de ganancias estimadas
        cuando detecta cambios en el PVG (principio reactivo).
        """
        try:
            from database.user_rank_history import UserRankHistory
            from database.ranks import Ranks
            from datetime import datetime, timezone
            
            # Obtener member_id desde AuthState (acceso async)
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
                
                # Guardar PVG anterior para detectar cambios
                previous_pvg = self.current_pvg
                self.current_pvg = user.pvg_cache or 0
                
                # Obtener rank_id actual del período corriendo (no por fecha, sino por period_id)
                from database.periods import Periods
                from .utils.timezone_mx import get_mexico_now
                
                now = get_mexico_now()
                current_period = session.exec(
                    sqlmodel.select(Periods)
                    .where(
                        (Periods.starts_on <= now) &
                        (Periods.ends_on >= now)
                    )
                ).first()
                
                if not current_period:
                    print(f"⚠️  No hay período activo")
                    return
                
                current_rank_history = session.exec(
                    sqlmodel.select(UserRankHistory)
                    .where(
                        (UserRankHistory.member_id == member_id) &
                        (UserRankHistory.period_id == current_period.id)
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
                    
                    # Calcular porcentaje de progreso
                    if self.next_rank_pvg > 0:
                        self.rank_progress_percentage = int((self.current_pvg / self.next_rank_pvg) * 100)
                    else:
                        self.rank_progress_percentage = 0
                else:
                    # Usuario está en el rango máximo
                    current_rank = session.exec(
                        sqlmodel.select(Ranks).where(Ranks.id == current_rank_id)
                    ).first()
                    self.next_rank_pvg = current_rank.pvg_required if current_rank else 0
                    self.rank_progress_percentage = 100
                
                print(f"📊 Progresión de rango - PVG: {self.current_pvg}/{self.next_rank_pvg} ({self.rank_progress_percentage:.1f}%)")
                
                # ✅ NUEVO: Si el PVG cambió, recalcular ganancias estimadas automáticamente
                if self.current_pvg != previous_pvg:
                    print(f"🔄 PVG cambió de {previous_pvg} a {self.current_pvg} - Recalculando ganancias...")
                    await self.load_estimated_monthly_earnings()
                
        except Exception as e:
            print(f"❌ Error cargando progresión de rango: {e}")
            import traceback
            traceback.print_exc()
    
    async def load_estimated_monthly_earnings(self):
        """
        Calcula la proyección REAL de ganancias mensuales.
        
        ESTRATEGIA SIMPLE (Principio KISS de Adrian):
        1. Sumar TODAS las comisiones YA CALCULADAS del período
        2. Esto incluye Uninivel, Matching y Alcance que ya están en BD
        
        La ventaja: NO re-calcular, solo mostrar lo que YA existe.
        Si quieres proyección futura, las comisiones deben calcularse primero.
        
        ACTUALIZADO: Retorna $0 si PVG=0 (cuando los usuarios fueron reseteados).
        
        Arquitectura: Adrian (KISS) + Giovanni (QA Financial)
        """
        try:
            from database.comissions import Commissions, BonusType
            from database.periods import Periods
            from .modules.finance.backend.exchange_service import ExchangeService
            
            # Obtener member_id desde AuthState
            auth_state = await self.get_state(AuthState)
            profile_data = auth_state.profile_data
            
            if not isinstance(profile_data, dict) or "member_id" not in profile_data:
                print("⚠️  No se pudo obtener member_id del usuario")
                return
            
            member_id = profile_data["member_id"]
            
            with rx.session() as session:
                # Obtener usuario para moneda y PVG
                user = session.exec(
                    sqlmodel.select(Users).where(Users.member_id == member_id)
                ).first()
                
                if not user:
                    print(f"⚠️  Usuario {member_id} no encontrado")
                    return
                
                # ✅ Si el PVG está en 0, las ganancias deben ser $0 (periodo reseteado)
                if (user.pvg_cache or 0) == 0:
                    self.estimated_monthly_earnings = 0.0
                    self.estimated_earnings_currency = ExchangeService.get_country_currency(user.country_cache or "MX")
                    print(f"📊 Ganancias estimadas: $0.00 (PVG=0, usuario reseteado)")
                    return
                
                self.estimated_earnings_currency = ExchangeService.get_country_currency(user.country_cache or "MX")
                
                # Obtener período actual
                from .utils.timezone_mx import get_mexico_now
                now = get_mexico_now()
                current_period = session.exec(
                    sqlmodel.select(Periods)
                    .where(
                        (Periods.starts_on <= now) &
                        (Periods.ends_on >= now)
                    )
                ).first()
                
                if not current_period:
                    print(f"⚠️  No hay período activo")
                    self.estimated_monthly_earnings = 0.0
                    return
                
                # Sumar TODAS las comisiones del período (Uninivel + Matching + Alcance)
                total_earnings = session.exec(
                    sqlmodel.select(sqlmodel.func.sum(Commissions.amount_converted))
                    .where(
                        (Commissions.member_id == member_id) &
                        (Commissions.period_id == current_period.id) &
                        (Commissions.bonus_type.in_([
                            BonusType.BONO_UNINIVEL.value,
                            BonusType.BONO_MATCHING.value,
                            BonusType.BONO_ALCANCE.value
                        ]))
                    )
                ).first()
                
                self.estimated_monthly_earnings = float(total_earnings) if total_earnings else 0.0
                
                # Desglose por tipo de bono (para debug)
                bonos_alcance = session.exec(
                    sqlmodel.select(sqlmodel.func.sum(Commissions.amount_converted))
                    .where(
                        (Commissions.member_id == member_id) &
                        (Commissions.period_id == current_period.id) &
                        (Commissions.bonus_type == BonusType.BONO_ALCANCE.value)
                    )
                ).first() or 0.0
                
                bonos_uninivel = session.exec(
                    sqlmodel.select(sqlmodel.func.sum(Commissions.amount_converted))
                    .where(
                        (Commissions.member_id == member_id) &
                        (Commissions.period_id == current_period.id) &
                        (Commissions.bonus_type == BonusType.BONO_UNINIVEL.value)
                    )
                ).first() or 0.0
                
                bonos_matching = session.exec(
                    sqlmodel.select(sqlmodel.func.sum(Commissions.amount_converted))
                    .where(
                        (Commissions.member_id == member_id) &
                        (Commissions.period_id == current_period.id) &
                        (Commissions.bonus_type == BonusType.BONO_MATCHING.value)
                    )
                ).first() or 0.0
                
                print(f"💰 Proyección mensual (comisiones calculadas):")
                print(f"   Bonos Alcance:  ${bonos_alcance:,.2f}")
                print(f"   Bonos Uninivel: ${bonos_uninivel:,.2f}")
                print(f"   Bonos Matching: ${bonos_matching:,.2f}")
                print(f"   TOTAL:          ${self.estimated_monthly_earnings:,.2f} {self.estimated_earnings_currency}")
                
        except Exception as e:
            print(f"❌ Error calculando proyección de ganancias: {e}")
            import traceback
            traceback.print_exc()
            self.estimated_monthly_earnings = 0.0
    
    async def refresh_dashboard_data(self):
        """
        Refresca TODOS los datos del dashboard (progresión de rango y ganancias).
        
        Este método debe ser llamado cada vez que cambien los PVG del usuario,
        sin importar cuánto sea el cambio (0→1, 293→293.1, etc.).
        
        PATRONES APLICADOS:
        - Reactivo: Responde automáticamente a cambios de datos
        - KISS: Simplemente llama a los métodos existentes
        - DRY: Reutiliza load_rank_progression y load_estimated_monthly_earnings
        
        CASOS DE USO:
        - Después de crear una orden (PVG aumenta)
        - Después de confirmar pago (PVG se actualiza)
        - Después de cualquier actualización manual de PVG
        - Después de reset de período (PVG vuelve a 0)
        
        Arquitectura: Adrian (KISS) + Giovanni (Reactivo)
        """
        try:
            print("🔄 Refrescando datos del dashboard...")
            
            # 1. Recargar progresión de rango (incluye PVG actual)
            await self.load_rank_progression()
            
            # 2. Recargar ganancias estimadas (se dispara automáticamente si PVG cambió)
            # Nota: load_rank_progression ya llama a load_estimated_monthly_earnings si detecta cambio
            # pero lo llamamos explícitamente aquí por si acaso
            await self.load_estimated_monthly_earnings()
            
            print("✅ Dashboard refrescado correctamente")
            
        except Exception as e:
            print(f"❌ Error refrescando dashboard: {e}")
            import traceback
            traceback.print_exc()


def index() -> rx.Component:
    # Welcome Page (Index)
    return rx.center(
        # Contenedor principal centrado
        rx.desktop_only(
            # Solo se muestra en escritorio
            rx.vstack(
                header(),
                # Contenedor vertical principal
                rx.hstack(
                    # Contenedor horizontal para sidebar y contenido principal
                    desktop_sidebar(),
                    # Sidebar (menú lateral)
                    main_container_derecha(
                        # Contenedor principal de la derecha
                        rx.vstack(
                            # Contenedor vertical para el contenido del dashboard
                            # Sección de anuncios/noticias
                            rx.box(
                                rx.image(
                                    src="/banner_dashboard.png",
                                    height="100%",  # Imagen ocupa todo el alto del box
                                    width="100%",   # Imagen ocupa todo el ancho del box
                                    object_fit="cover",  # Ajuste de imagen
                                    border_radius="64px" # Bordes redondeados
                                ),
                                height="380px",         # Alto del banner
                                width="100%",           # Ancho completo
                                margin_bottom="0.5em",  # Espacio inferior
                            ),
                            # Fila: Volumen Personal, Puntos NN Travel, Rango mayor, Rango actual
                            rx.hstack(
                                rx.box(
                                    rx.text("Volumen Personal", font_size="0.875rem", color="black"),
                                    rx.text("2,930", font_size="1.5rem", font_weight="bold", color="black"),
                                    bg="#32D74B",             # Fondo verde
                                    on_click=lambda: rx.redirect("/network_reports"),  # Redirige al reporte de red
                                    cursor="pointer",        # Cambia el cursor al pasar por encima
                                    padding="1em",            # Espaciado interno
                                    border_radius="32px",     # Bordes redondeados
                                    width="25%",              # Ancho relativo
                                ),
                                rx.box(
                                    rx.text("Puntos NN Travel", font_size="0.875rem"),
                                    rx.text("500", font_size="1.5rem", font_weight="bold"),
                                    bg=rx.color_mode_cond(
                                        light=Custom_theme().light_colors()["tertiary"],
                                        dark=Custom_theme().dark_colors()["tertiary"]
                                    ),                        # Fondo según modo
                                    padding="1em",
                                    border_radius="32px",
                                    width="25%",
                                ),
                                rx.box(
                                    rx.text("Rango más alto alcanzado", font_size="0.875rem"),
                                    rx.text("E. Consciente", font_size="1.5rem", font_weight="bold"),
                                    bg="#0039F2",             # Fondo azul
                                    color="white",            # Texto blanco
                                    padding="1em",
                                    border_radius="32px",
                                    width="25%",
                                ),
                                rx.box(
                                    rx.text("Rango Actual", font_size="0.875rem"),
                                    rx.text("E. Transformador", font_size="1.5rem", font_weight="bold"),
                                    bg="#5E79FF",             # Fondo azul claro
                                    color="white",
                                    padding="1em",
                                    border_radius="32px",
                                    width="25%",
                                ),
                                spacing="2",                 # Espacio entre cajas
                                width="100%",                # Ancho completo
                            ),
                            rx.hstack(
                                # Fila vertical: puntos de lealtad y cashback
                                rx.vstack(
                                    rx.box(
                                        rx.text("Puntos de lealtad", font_size="0.875rem"),
                                        rx.text("100", font_size="1.5rem", font_weight="bold"),
                                        bg=rx.color_mode_cond(
                                            light=Custom_theme().light_colors()["tertiary"],
                                            dark=Custom_theme().dark_colors()["tertiary"]
                                        ),
                                        padding="1em",
                                        border_radius="32px",
                                        width="100%",
                                    ),
                                    rx.box(
                                        rx.text("Puntos de CASHBACK", font_size="0.875rem"),
                                        rx.text("2,930", font_size="1.5rem", font_weight="bold"),
                                        bg=rx.color_mode_cond(
                                            light=Custom_theme().light_colors()["tertiary"],
                                            dark=Custom_theme().dark_colors()["tertiary"]
                                        ),
                                        padding="1em",
                                        border_radius="32px",
                                        width="100%",
                                    ),
                                    spacing="2",              # Espacio entre cajas
                                    width="25%",              # Ancho relativo
                                ),
                                # Barra de progresión
                                rx.box(
                                    rx.text("Progresión para el siguiente rango", font_size="0.875rem", color="#FFFFFF"),
                                    rx.center(
                                        rx.text(
                                            f"{DashboardState.current_pvg:,} — {DashboardState.next_rank_pvg:,} PVG",
                                            font_size="2rem", 
                                            font_weight="bold"
                                        ),
                                        height="6em",          # Altura del centro
                                    ),
                                    rx.progress(
                                        bg="#D0D7FF",          # Fondo de la barra
                                        fill_color="#0039F2",  # Color de progreso
                                        height="8px",          # Altura de la barra
                                        width="100%",          # Ancho completo
                                        value=DashboardState.rank_progress_percentage,
                                        max=100,
                                    ),
                                    spacing="1",              # Espacio entre elementos
                                    bg="#5E79FF",             # Fondo del box
                                    color="white",            # Texto blanco
                                    padding="1.5em",          # Espaciado interno
                                    justify="center",         # Centrado
                                    border_radius="48px",     # Bordes redondeados
                                    height="100%",            # Alto completo
                                    width="75%",              # Ancho relativo
                                    on_click=lambda: rx.redirect("/network_reports"),  # Redirige al reporte de red
                                    cursor="pointer",        # Cambia el cursor al pasar por encima
                                ),
                                height="11em",               # Altura de la fila
                                width="100%",                # Ancho completo
                            ),
                            # Enlace de referido
                            rx.box(
                                rx.text("Enlace de referido", font_size="0.875rem", margin_bottom="0.5em"),
                                rx.box(
                                    rx.text(
                                        AuthState.get_user_display_name
                                        ),
                                    read_only=True,           # Solo lectura
                                    border_radius="18px"      # Bordes redondeados
                                ),
                                bg=rx.color_mode_cond(
                                    light=Custom_theme().light_colors()["tertiary"],
                                    dark=Custom_theme().dark_colors()["tertiary"]
                                ),
                                padding="1em",
                                border_radius="32px",
                                width="100%",
                                margin_top="1em",            # Espacio superior
                            ),
                            # Reporte de usuarios
                            rx.box(
                                rx.text("Reporte de usuarios", font_size="0.875rem"),
                                rx.hstack(
                                    rx.box(
                                        bg="#32D74B", 
                                        height="8px", 
                                        width=f"{DashboardState.qualified_percentage}%", 
                                        border_radius="4px"
                                    ),
                                    rx.box(
                                        bg="#FF3B30", 
                                        height="8px", 
                                        width=f"{DashboardState.non_qualified_percentage}%", 
                                        border_radius="4px"
                                    ),
                                    spacing="1",              # Espacio entre barras
                                    width="100%",
                                ),
                                rx.hstack(
                                    rx.text(f"Calificados – {DashboardState.qualified_count}"),
                                    rx.text(f"No calificados – {DashboardState.non_qualified_count}", margin_left="auto")
                                ),
                                bg=rx.color_mode_cond(
                                    light=Custom_theme().light_colors()["tertiary"],
                                    dark=Custom_theme().dark_colors()["tertiary"]
                                ),
                                padding="1em",
                                border_radius="32px",
                                width="100%",
                                margin_top="1em",
                            ),
                            # Ganancias y acciones
                            rx.hstack(
                                rx.box(
                                    rx.text("Estimado de ganancia del mes"),
                                    rx.text("42,659,227.68", font_size="1.5rem", font_weight="bold"),
                                    bg="#0039F2",
                                    color="white",
                                    padding="1em",
                                    border_radius="32px",
                                    width="25%",
                                ),
                                rx.box(
                                    rx.text("Billetera"),
                                    rx.text("53,324,034.60", font_size="1.5rem", font_weight="bold"),
                                    bg=rx.color_mode_cond(
                                        light=Custom_theme().light_colors()["tertiary"],
                                        dark=Custom_theme().dark_colors()["tertiary"]
                                    ),
                                    padding="1em",
                                    border_radius="32px",
                                    width="25%",
                                ),
                                rx.box(
                                    rx.text("Pago en espera"),
                                    rx.text("10,664,806.92", font_size="1.5rem", font_weight="bold"),
                                    bg=rx.color_mode_cond(
                                        light=Custom_theme().light_colors()["tertiary"],
                                        dark=Custom_theme().dark_colors()["tertiary"]
                                    ),
                                    padding="1em",
                                    border_radius="32px",
                                    width="25%",
                                ),
                                rx.vstack(
                                    rx.link(
                                        rx.button(
                                            "Solicitar comisiones",
                                            bg="#0039F2",
                                            color="white",
                                            border_radius="32px",
                                            width="100%",
                                        ),
                                        width="100%",
                                        height="40px",
                                        href="/new_withdrawal",
                                    ),
                                    rx.button(
                                        "Transferencia interna",
                                        bg=rx.color_mode_cond(
                                            light=Custom_theme().light_colors()["tertiary"],
                                            dark=Custom_theme().dark_colors()["tertiary"]
                                        ),
                                        border="1px solid #0039F2",
                                        color=rx.color_mode_cond(
                                            light=Custom_theme().light_colors()["text"],
                                            dark=Custom_theme().dark_colors()["text"]
                                        ),
                                        border_radius="32px",
                                        width="100%",
                                        height="36px"
                                    ),
                                    margin="auto",            # Centrado vertical
                                    width="25%",
                                    spacing="2",              # Espacio entre botones
                                ),
                                spacing="2",                  # Espacio entre cajas
                                width="100%",
                                margin_top="1em",
                            ),
                            # Herramientas para tu negocio (grid)
                            rx.vstack(
                                rx.text("Herramientas para tu negocio", font_size="1rem", font_weight="bold"),
                                rx.grid(
                                    *[rx.box(bg="#E5E5E5", height="80px", border_radius="12px") for _ in range(12)],
                                    template_columns="repeat(4, 1fr)",  # 4 columnas
                                    gap="1em",                          # Espacio entre cajas
                                    width="100%",
                                    margin_top="1em",
                                ),
                            ),
                            # Propiedades del vstack que contiene el contenido de la página
                            width="100%", # Ancho total del contenido de la página
                        ),
                    ),
                    # Propiedades de flex dentro del vstack que contiene el contenido de la página.
                    width="100%",                  # Ancho completo (Propiedad necesaria para que el contenedor quede centrado no importa si la ventana es muy grande.)
                ),
                # Propiedades vstack que contiene el contenido de la página.
                align="end",        # Centrado vertical
                margin_top="8em",         # Espacio superior
                margin_bottom="2em",      # Espacio inferior
                width="100%",
                max_width="1920px",       # Ancho máximo
            )
        ),
        
        # Versión móvil
        rx.mobile_only(
            rx.vstack(
                # Header móvil
                mobile_header(),

                # Contenido principal móvil
                rx.vstack(
                    # Banner móvil
                    rx.box(
                        rx.image(
                            src="/banner_dashboard.png",
                            height="100%",
                            width="100%",
                            object_fit="cover",
                            border_radius="16px"
                        ),
                        height="200px",
                        width="100%",
                        margin_bottom="1.5rem"
                    ),
                    
                    # Estadísticas principales - Grid 2x2
                    rx.grid(
                        rx.box(
                            rx.vstack(
                                rx.text("Volumen Personal", font_size="0.8rem", color="black", text_align="center"),
                                rx.text(AuthState.profile_data.get("pv_cache", 0), font_size="1.3rem", font_weight="bold", color="black", text_align="center"),
                                spacing="1"
                            ),
                            bg="#32D74B",
                            padding="16px",
                            border_radius="29px",
                            width="100%",
                            on_click=lambda: rx.redirect("/network_reports")
                        ),
                        rx.box(
                            rx.vstack(
                                rx.text("NN Travel", font_size="0.8rem", text_align="center"),
                                rx.text("500", font_size="1.3rem", font_weight="bold", text_align="center"),
                                spacing="1"
                            ),
                            bg=rx.color_mode_cond(
                                light=Custom_theme().light_colors()["tertiary"],
                                dark=Custom_theme().dark_colors()["tertiary"]
                            ),
                            padding="16px",
                            border_radius="29px",
                            width="100%"
                        ),
                        rx.box(
                            rx.vstack(
                                rx.text("Máximo rango", font_size="0.8rem"),
                                rx.text(AuthState.profile_data.get("highest_rank"), font_size="0.9rem", font_weight="bold"),
                                spacing="1"
                            ),
                            bg="#0039F2",
                            color="white",
                            padding="16px",
                            border_radius="29px",
                            width="100%"
                        ),
                        rx.box(
                            rx.vstack(
                                rx.text("Rango Actual", font_size="0.8rem"),
                                rx.text(AuthState.profile_data.get("current_month_rank"), font_size="0.9rem", font_weight="bold"),
                                spacing="1"
                            ),
                            bg="#5E79FF",
                            color="white",
                            padding="16px",
                            border_radius="29px",
                            width="100%"
                        ),
                        rx.box(
                            rx.vstack(
                                rx.text("Lealtad", font_size="0.8rem", text_align="center"),
                                rx.text("100", font_size="1.2rem", font_weight="bold", text_align="center"),
                                spacing="1"
                            ),
                            bg=rx.color_mode_cond(
                                light=Custom_theme().light_colors()["tertiary"],
                                dark=Custom_theme().dark_colors()["tertiary"]
                            ),
                            padding="16px",
                            border_radius="29px",
                            width="100%"
                        ),
                        rx.box(
                            rx.vstack(
                                rx.text("Cashback", font_size="0.8rem", text_align="center"),
                                rx.text("2,930", font_size="1.2rem", font_weight="bold", text_align="center"),
                                spacing="1"
                            ),
                            bg=rx.color_mode_cond(
                                light=Custom_theme().light_colors()["tertiary"],
                                dark=Custom_theme().dark_colors()["tertiary"]
                            ),
                            padding="16px",
                            border_radius="29px",
                            width="100%"
                        ),
                        columns="2",
                        spacing="3",
                        width="100%",
                    ),
                    
                    # Progresión de rango
                    rx.box(
                        rx.vstack(
                            rx.text("Progresión siguiente rango", font_size="0.9rem", color="white"),
                            rx.heading(
                                f"{DashboardState.current_pvg:,} — {DashboardState.next_rank_pvg:,} VG",
                                #font_size="1.1rem",
                                #font_weight="bold",
                                size="6",
                                color="white",
                                width="100%",
                                text_align="center"
                            ),
                            rx.progress(
                                bg="#D0D7FF",
                                fill_color="#0039F2",
                                height="6px",
                                width="100%",
                                value=DashboardState.rank_progress_percentage,
                                max=100,
                            ),
                            width="100%",
                            spacing="2"
                        ),
                        bg="#5E79FF",
                        padding="16px",
                        border_radius="29px",
                        width="100%",
                        cursor="pointer",
                        on_click=lambda: rx.redirect("/network_reports")
                    ),
                    
                    # Enlace de referido móvil
                    rx.box(
                        rx.text("Enlace de referido", font_size="0.9rem", font_weight="bold", margin_bottom="0.5rem"),
                        rx.box(
                            rx.text(
                                AuthState.profile_data.get("referral_link"),
                                font_size="16px",
                                ),
                            bg=rx.color_mode_cond(
                                light=Custom_theme().light_colors()["background"],
                                dark=Custom_theme().dark_colors()["background"]
                            ),
                            padding="4px 8px",
                            width="100%",
                            read_only=True,
                            border_radius="13px",
                            font_size="0.8rem",
                        ),
                        bg=rx.color_mode_cond(
                            light=Custom_theme().light_colors()["tertiary"],
                            dark=Custom_theme().dark_colors()["tertiary"]
                        ),
                        padding="16px",
                        border_radius="29px",
                        width="100%",
                    ),
                    
                    # Reporte de usuarios móvil
                    rx.box(
                        rx.vstack(
                            rx.text("Reporte de usuarios", font_size="0.9rem", font_weight="bold"),
                            rx.hstack(
                                rx.box(
                                    bg="#32D74B", 
                                    height="6px", 
                                    width=f"{DashboardState.qualified_percentage}%", 
                                    border_radius="3px"
                                ),
                                rx.box(
                                    bg="#FF3B30", 
                                    height="6px", 
                                    width=f"{DashboardState.non_qualified_percentage}%", 
                                    border_radius="3px"
                                ),
                                spacing="1",
                                width="100%"
                            ),
                            rx.hstack(
                                rx.text(f"Calificados: {DashboardState.qualified_count}", font_size="0.9em"),
                                rx.spacer(),
                                rx.text(f"No calificados: {DashboardState.non_qualified_count}", font_size="0.9em"),
                                width="100%",
                                justify="between",
                            ),
                            spacing="2"
                        ),
                        bg=rx.color_mode_cond(
                            light=Custom_theme().light_colors()["tertiary"],
                            dark=Custom_theme().dark_colors()["tertiary"]
                        ),
                        padding="16px",
                        border_radius="29px",
                        width="100%",
                    ),
                    
                    # Finanzas móvil
                    rx.vstack(
                        rx.box(
                            rx.vstack(
                                rx.text("Proyección mensual", font_size="0.8rem", text_align="center"),
                                rx.text(
                                    f"${DashboardState.estimated_monthly_earnings:,.2f} {DashboardState.estimated_earnings_currency}",
                                    font_size="1.1rem",
                                    font_weight="bold",
                                    text_align="center"
                                ),
                                spacing="1"
                            ),
                            bg="#0039F2",
                            color="white",
                            padding="16px",
                            border_radius="32px",
                            width="100%"
                        ),
                        rx.hstack(
                            rx.box(
                                rx.vstack(
                                    rx.text("Billetera", font_size="0.8rem", text_align="center"),
                                    rx.text(f"${AuthState.profile_data.get("wallet_balance", 0):,.0f}", font_size="1rem", font_weight="bold", text_align="center"),
                                    spacing="1"
                                ),
                                bg=rx.color_mode_cond(
                                    light=Custom_theme().light_colors()["tertiary"],
                                    dark=Custom_theme().dark_colors()["tertiary"]
                                ),
                                padding="16px",
                                border_radius="32px",
                                width="49%"
                            ),
                            rx.box(
                                rx.vstack(
                                    rx.text("En espera", font_size="0.8rem", text_align="center"),
                                    rx.text("$10,664,806", font_size="1rem", font_weight="bold", text_align="center"),
                                    spacing="1"
                                ),
                                bg=rx.color_mode_cond(
                                    light=Custom_theme().light_colors()["tertiary"],
                                    dark=Custom_theme().dark_colors()["tertiary"]
                                ),
                                padding="16px",
                                border_radius="29px",
                                width="49%"
                            ),
                            justify="between",
                            width="100%"
                        ),
                        rx.vstack(
                            rx.link(
                                rx.button(
                                    "Solicitar comisiones",
                                    bg="#0039F2",
                                    color="white",
                                    border_radius="22px",
                                    height="48px",
                                    width="100%",
                                ),
                                width="100%",
                                href="/new_withdrawal",
                            ),
                            rx.link(
                                rx.button(
                                    "Transferencia interna",
                                    variant="outline",
                                    color=rx.color_mode_cond(
                                        light=Custom_theme().light_colors()["text"],
                                        dark=Custom_theme().dark_colors()["text"]
                                    ),
                                    border="1px solid #0039F2",
                                    border_radius="32px",
                                    height="48px",
                                    width="100%",
                                ),
                                width="100%",
                                href="/",
                            ),
                            spacing="2",
                            width="100%"
                        ),
                        spacing="3",
                        width="100%",
                        margin_bottom="1.5rem"
                    ),
                    
                    # Herramientas móvil
                    rx.vstack(
                        rx.text("Herramientas para tu negocio", font_size="1rem", font_weight="bold"),
                        rx.grid(
                            *[rx.box(
                                bg=rx.color_mode_cond(
                                    light=Custom_theme().light_colors()["tertiary"],
                                    dark=Custom_theme().dark_colors()["tertiary"]
                                ), 
                                height="60px", 
                                border_radius="8px"
                            ) for _ in range(8)],
                            columns="2",
                            spacing="2",
                            width="100%"
                        ),
                        spacing="3",
                        width="100%"
                    ),
                    spacing="4",
                    width="100%",
                    padding="1em",
                    margin_top="80px",
                    margin_bottom="0.2em",
                ),
                bg=rx.color_mode_cond(
                    light=Custom_theme().light_colors()["background"],
                    dark=Custom_theme().dark_colors()["background"]
                ),
                width="100%",
            ),
            width="100%",
        ),
        # Propiedades del contenedor principal.
        height="100%",
        bg=rx.color_mode_cond(
            light=Custom_theme().light_colors()["background"],
            dark=Custom_theme().dark_colors()["background"]
        ),
        width="100%",                  # Ancho de la ventana
        on_mount=[
            AuthState.load_user_from_token,
            DashboardState.load_user_stats,
            DashboardState.load_rank_progression,
            DashboardState.load_estimated_monthly_earnings
        ],
    )

# Meta tags para PWA y configuración móvil
meta = [
    # 1. CLAVE: Se agrega el viewport con 'viewport-fit=cover' para que la PWA abrace la muesca.
    {"name": "viewport", "content": "initial-scale=1, viewport-fit=cover, width=device-width"},
    
    # 2. Requisitos de la PWA de Apple para modo app y estilo de barra.
    {"name": "apple-mobile-web-app-status-bar-style", "content": "black-translucent"}, 
    {"name": "apple-mobile-web-app-capable", "content": "yes"},
]

app = rx.App(
    theme=rx.theme(appearance="inherit")
)

app.add_page(
    index,
    title="NN Protect | Dashboard",
    route="/dashboard",
    meta=meta,
)

# Login y Registro
app.add_page(login, title="NN Protect | Iniciar sesión", route="/", meta=meta)
app.add_page(register, title="NN Protect | Nuevo registro", route="/register", meta=meta)
app.add_page(register_noSponsor, title="NN Protect | Registro sin patrocinador", route="/register_noSponsor", meta=meta)
app.add_page(welcome_page, title="NN Protect | Bienvenido", route="/welcome", meta=meta)

# Servicio de red
app.add_page(network, title="NN Protect | Red", route="/network", meta=meta)
app.add_page(network_reports, title="NN Protect | Reportes de Red", route="/network_reports", meta=meta)
app.add_page(income_reports, title="NN Protect | Reportes de Ingresos", route="/income_reports", meta=meta)

# Servicio de tienda
app.add_page(store, title="NN Protect | Tienda", route="/store", meta=meta)
app.add_page(shopping_cart, title="NN Protect | Carrito de Compras", route="/shopping_cart", meta=meta)

# Servicio de órdenes
app.add_page(orders, title="NN Protect | Órdenes", route="/orders", meta=meta)
app.add_page(order_details, title="NN Protect | Detalles de Orden", route="/orders/order_details", meta=meta)
app.add_page(order_confirmation, title="NN Protect | Confirmación de Orden", route="/order_confirmation", meta=meta)

# Servicio de retiros
app.add_page(withdrawals, title="NN Protect | Retiros", route="/withdrawals", meta=meta)
app.add_page(new_withdrawal, title="NN Protect | Nuevo Retiro", route="/new_withdrawal", meta=meta)

# Servicio de envíos
app.add_page(shipment_method, title="NN Protect | Método de Envío", route="/shipment_method", meta=meta)

# Servicio de pagos
app.add_page(payment, title="NN Protect | Método de Pago", route="/payment", meta=meta)

# Admin Panel
app.add_page(admin_page, title="NN Protect | Admin Panel", route="/admin", meta=meta)

# Inicializar base de datos (crear periodo inicial si no existe)
initialize_database()

# Iniciar scheduler de tareas automáticas
SchedulerService.start_scheduler()