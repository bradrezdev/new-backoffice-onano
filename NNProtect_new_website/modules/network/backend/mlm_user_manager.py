"""
Manager para datos MLM de usuarios - SEPARADO de autenticación Supabase.
Se enfoca únicamente en la lógica de negocio multinivel.
"""
import reflex as rx
import sqlmodel
from typing import Optional, Dict, Any
from database.users import Users, UserStatus

# Timezone utilities
from NNProtect_new_website.utils.timezone_mx import get_mexico_now, format_mexico_date, format_mexico_datetime, get_mexico_date, get_mexico_datetime_naive
from datetime import timedelta
from database.userprofiles import UserProfiles, UserGender
from database.social_accounts import SocialAccounts, SocialNetwork
from database.roles import Roles
from database.roles_users import RolesUsers
from database.auth_credentials import AuthCredentials
from database.usertreepaths import UserTreePath
from database.unilevel_report import UnilevelReports
from NNProtect_new_website.modules.network.backend.rank_service import RankService
from NNProtect_new_website.modules.finance.backend.wallet_service import WalletService
import os

class MLMUserManager:
    """Maneja datos MLM separados de la autenticación Supabase."""
    
    @staticmethod
    def get_next_member_id(session) -> int:
        """Obtiene el siguiente member_id disponible."""
        last_user = session.exec(
            sqlmodel.select(Users).order_by(sqlmodel.desc(Users.member_id))
        ).first()
        return last_user.member_id + 1 if last_user else 1

    @staticmethod
    def create_mlm_user(session, supabase_user_id: str, first_name: str, 
                       last_name: str, email: str, sponsor_member_id: Optional[int] = None) -> Users:
        """
        Crea registro MLM para usuario autenticado en Supabase.
        NO maneja autenticación - solo datos de negocio.
        """
        try:
            member_id = MLMUserManager.get_next_member_id(session)
            
            # Convertir sponsor_member_id a sponsor_id (users.id)
            sponsor_id = None
            if sponsor_member_id and sponsor_member_id > 0:
                sponsor = session.exec(
                    sqlmodel.select(Users).where(Users.member_id == sponsor_member_id)
                ).first()
                if sponsor:
                    sponsor_id = sponsor.id
            
            # Crear registro MLM
            new_user = Users(
                supabase_user_id=supabase_user_id,
                member_id=member_id,
                first_name=first_name,
                last_name=last_name,
                email_cache=email,
                sponsor_id=sponsor_id,
                status=UserStatus.NO_QUALIFIED
            )
            session.add(new_user)
            session.flush()
            
            # Crear genealogía en UserTreePath
            from .genealogy_service import GenealogyService
            tree_created = GenealogyService.add_member_to_tree(
                session,
                new_member_id=member_id,
                sponsor_id=sponsor_member_id
            )
            if tree_created:
                print(f"✅ UserTreePath creado - Sponsor ID: {sponsor_member_id}, User ID: {member_id}")
            else:
                print(f"⚠️  No se pudo crear UserTreePath para usuario {member_id}")
            
            # Generar referral link
            base_url = MLMUserManager.get_base_url()
            new_user.referral_link = f"{base_url}?ref={member_id}"
            
            # 🎯 ASIGNAR RANGO INICIAL "Sin rango" (id=1) AUTOMÁTICAMENTE
            rank_assigned = RankService.assign_initial_rank(session, member_id)
            if not rank_assigned:
                print(f"⚠️  Advertencia: No se pudo asignar rango inicial a usuario {member_id}")
            
            # 🆕 CREAR REGISTRO INICIAL EN UNILEVEL_REPORTS
            try:
                from database.periods import Periods
                from sqlmodel import desc
                from database.unilevel_report import UnilevelReports
                
                # Obtener el período actual
                current_period = session.exec(
                    sqlmodel.select(Periods).order_by(desc(Periods.starts_on)).limit(1)
                ).first()
                
                if current_period:
                    initial_report = UnilevelReports(
                        user_id=new_user.id,
                        period_id=current_period.id,
                        pv=0,
                        vn=0.0,
                        pvg_1=0,
                        vng_1=0.0,
                        pvg_2=0,
                        vng_2=0.0,
                        pvg_3=0,
                        vng_3=0.0,
                        pvg_4=0,
                        vng_4=0.0,
                        pvg_5=0,
                        vng_5=0.0,
                        pvg_6=0,
                        vng_6=0.0,
                        pvg_7=0,
                        vng_7=0.0,
                        pvg_8=0,
                        vng_8=0.0,
                        pvg_9=0,
                        vng_9=0.0,
                        pvg_10_plus=0,
                        vng_10_plus=0.0,
                        pvg_total=0,
                        vng_total=0.0
                    )
                    session.add(initial_report)
                    print(f"✅ UnilevelReport inicial creado para usuario {member_id} en período {current_period.name}")
                else:
                    print(f"⚠️  No se encontró período actual para crear UnilevelReport")
            except Exception as e:
                print(f"⚠️  Error creando UnilevelReport inicial: {e}")
            
            # 🆕 CREAR WALLET
            try:
                WalletService.create_wallet(session, member_id, "MXN")
            except Exception as e:
                print(f"⚠️  Error creando Wallet inicial: {e}")

            print(f"✅ Usuario MLM creado - Member ID: {member_id}, Sponsor ID: {sponsor_id}")
            return new_user
            
        except Exception as e:
            print(f"❌ Error creando usuario MLM: {e}")
            raise

    @staticmethod
    def get_user_by_supabase_id(supabase_user_id: str) -> Optional[Users]:
        """Obtiene usuario MLM por su ID de Supabase."""
        try:
            with rx.session() as session:
                return session.exec(
                    sqlmodel.select(Users).where(Users.supabase_user_id == supabase_user_id)
                ).first()
        except Exception as e:
            print(f"❌ Error obteniendo usuario MLM: {e}")
            return None

    @staticmethod
    def get_user_by_member_id(member_id: int) -> Optional[Users]:
        """Obtiene usuario MLM por member_id."""
        try:
            with rx.session() as session:
                return session.exec(
                    sqlmodel.select(Users).where(Users.member_id == member_id)
                ).first()
        except Exception as e:
            print(f"❌ Error obteniendo usuario por member_id: {e}")
            return None

    @staticmethod
    def validate_sponsor_by_member_id(member_id: int) -> bool:
        """Verifica si existe un sponsor válido."""
        return MLMUserManager.get_user_by_member_id(member_id) is not None

    @staticmethod
    def create_user_profile(session, user_id: int, phone: str, gender: str):
        """Crea perfil extendido del usuario."""
        gender_enum = UserGender.MALE if gender == "Masculino" else UserGender.FEMALE
        
        profile = UserProfiles(
            user_id=user_id,
            gender=gender_enum,
            phone_number=phone
        )
        session.add(profile)
        print(f"✅ Perfil MLM creado para usuario {user_id}")

    @staticmethod
    def create_social_accounts(session, user_id: int):
        """Crea registro de redes sociales."""
        # Temporal: No crear registro social por defecto para evitar enum error
        pass

    @staticmethod
    def assign_default_role(session, user_id: int):
        """Asigna rol por defecto al usuario."""
        default_role = session.exec(
            sqlmodel.select(Roles).where(Roles.role_name == "USER")
        ).first()
        
        if default_role:
            user_role = RolesUsers(
                user_id=user_id,
                role_id=default_role.role_id
            )
            session.add(user_role)
            print(f"✅ Rol asignado al usuario MLM {user_id}")
        else:
            print("⚠️ Rol 'USER' no encontrado, continuando sin rol")

    @staticmethod
    def create_legacy_auth_credentials(session, user_id: int):
        """Crea credenciales legacy para compatibilidad (sin contraseña real)."""
        try:
            credentials = AuthCredentials(
                user_id=user_id,
                password_hash="supabase_managed",  # Marcador para indicar que Supabase maneja auth
                terms_accepted=True
            )
            session.add(credentials)
            print(f"✅ Credenciales legacy creadas para usuario {user_id}")
        except Exception as e:
            print(f"⚠️ No se pudieron crear credenciales legacy: {e}")

    @staticmethod
    def get_base_url() -> str:
        """URL base para referral links."""
        is_production = (
            os.environ.get("REFLEX_ENV") == "prod" or 
            not os.path.exists(".env")
        )
        return "https://codebradrez.tech/register" if is_production else "http://localhost:3000/register"

    @staticmethod
    async def load_complete_user_data_async(supabase_user_id: str) -> dict:
        """
        🚀 VERSIÓN ASYNC: Carga datos completos del usuario MLM usando supabase_user_id.
        
        Esta versión async permite paralelizar con Supabase auth usando asyncio.gather().
        Mejora performance de login de 59s a <5s.
        """
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        
        try:
            print(f"⚡ [ASYNC] Buscando datos MLM para Supabase ID: {supabase_user_id}")
            
            # Ejecutar query de BD en thread pool para no bloquear event loop
            loop = asyncio.get_event_loop()
            
            def _load_user_data():
                with rx.session() as session:
                    return MLMUserManager._load_user_data_sync(session, supabase_user_id)
            
            # Ejecutar en thread pool
            result = await loop.run_in_executor(None, _load_user_data)
            return result
            
        except Exception as e:
            print(f"❌ Error en load_complete_user_data_async: {str(e)}")
            import traceback
            traceback.print_exc()
            return {}
    
    @staticmethod
    def _load_user_data_sync(session, supabase_user_id: str) -> dict:
        """Helper síncrono para extraer lógica de BD."""
        user = session.exec(
            sqlmodel.select(Users).where(Users.supabase_user_id == supabase_user_id)
        ).first()
        
        if not user:
            print(f"❌ Usuario MLM no encontrado con supabase_user_id: {supabase_user_id}")
            return {}
        
        print(f"✅ Usuario MLM encontrado: ID={user.id}, Member ID={user.member_id}")
        
        # Cargar perfil con manejo seguro
        user_profile = session.exec(
            sqlmodel.select(UserProfiles).where(UserProfiles.user_id == user.id)
        ).first()
        
        # ✅ CORRECCIÓN: Los nombres están en Users, no en UserProfiles
        first_name = user.first_name if user.first_name else ''
        last_name = user.last_name if user.last_name else ''
        phone_number = user_profile.phone_number if user_profile else ''
        gender_value = ''
        
        if user_profile and user_profile.gender:
            gender_value = user_profile.gender.value if hasattr(user_profile.gender, 'value') else str(user_profile.gender)
        
        # Construir nombres optimizados
        full_name = f"{first_name} {last_name}".strip() if first_name or last_name else f"Usuario {user.member_id}"
        
        # Profile name con primeras palabras solamente
        first_word = first_name.split()[0] if first_name and first_name.split() else ""
        last_word = last_name.split()[0] if last_name and last_name.split() else ""
        
        if first_word and last_word:
            profile_name = f"{first_word} {last_word}"
        elif first_word:
            profile_name = first_word
        elif last_word:
            profile_name = last_word
        else:
            profile_name = f"Usuario {user.member_id}"

        # ✅ NUEVO: Cargar rangos del usuario
        current_month_rank = MLMUserManager.get_user_current_month_rank(session, user.member_id)
        highest_rank = MLMUserManager.get_user_highest_rank(session, user.member_id)

        # ✅ NUEVO: Cargar balance de wallet
        wallet_balance, wallet_currency = MLMUserManager.get_user_wallet_balance(session, user.member_id)

        # Datos de retorno completos
        mlm_data = {
            "id": user.id,
            "username": f"user{user.member_id}",
            "member_id": user.member_id,
            "status": user.status.value if hasattr(user.status, 'value') else str(user.status),
            "firstname": first_name,
            "lastname": last_name,
            "full_name": full_name,
            "profile_name": profile_name,
            "email": user.email_cache or '',
            "phone": phone_number,
            "gender": gender_value,
            "referral_link": user.referral_link,
            "sponsor_id": user.sponsor_id,
            "created_at": format_mexico_date(user.created_at) if user.created_at else '',
            "created_at_iso": user.created_at.isoformat() if user.created_at else '',
            "last_login": format_mexico_datetime(user.updated_at) if user.updated_at else '',
            "current_month_rank": current_month_rank,
            "highest_rank": highest_rank,
            "pv_cache": user.pv_cache,
            "pvg_cache": user.pvg_cache,
            "wallet_balance": wallet_balance,
            "wallet_currency": wallet_currency,
        }

        # ✅ NUEVO: Cargar datos del sponsor
        sponsor_data = MLMUserManager.load_sponsor_data(session, user)
        mlm_data["sponsor_data"] = sponsor_data
        
        print(f"✅ Datos MLM cargados exitosamente para {profile_name}")
        if sponsor_data:
            print(f"✅ Datos de sponsor cargados: {sponsor_data.get('profile_name', 'N/A')}")
        
        return mlm_data
    
    @staticmethod
    def load_complete_user_data(supabase_user_id: str) -> dict:
        """
        🔄 VERSIÓN SÍNCRONA (LEGACY): Carga datos completos del usuario MLM.
        
        ⚠️  DEPRECADO: Usar load_complete_user_data_async() para mejor performance.
        Esta versión se mantiene para compatibilidad con código existente.
        """
        try:
            print(f"🔄 Buscando datos MLM para Supabase ID: {supabase_user_id}")
            
            with rx.session() as session:
                return MLMUserManager._load_user_data_sync(session, supabase_user_id)
                
                # Cargar perfil con manejo seguro
                user_profile = session.exec(
                    sqlmodel.select(UserProfiles).where(UserProfiles.user_id == user.id)
                ).first()
                
                # ✅ CORRECCIÓN: Los nombres están en Users, no en UserProfiles
                first_name = user.first_name if user.first_name else ''
                last_name = user.last_name if user.last_name else ''
                phone_number = user_profile.phone_number if user_profile else ''
                gender_value = ''
                
                if user_profile and user_profile.gender:
                    gender_value = user_profile.gender.value if hasattr(user_profile.gender, 'value') else str(user_profile.gender)
                
                # Construir nombres optimizados
                full_name = f"{first_name} {last_name}".strip() if first_name or last_name else f"Usuario {user.member_id}"
                
                # Profile name con primeras palabras solamente
                first_word = first_name.split()[0] if first_name and first_name.split() else ""
                last_word = last_name.split()[0] if last_name and last_name.split() else ""
                
                if first_word and last_word:
                    profile_name = f"{first_word} {last_word}"
                elif first_word:
                    profile_name = first_word
                elif last_word:
                    profile_name = last_word
                else:
                    profile_name = f"Usuario {user.member_id}"

                # ✅ NUEVO: Cargar rangos del usuario
                current_month_rank = MLMUserManager.get_user_current_month_rank(session, user.member_id)
                highest_rank = MLMUserManager.get_user_highest_rank(session, user.member_id)

                # ✅ NUEVO: Cargar balance de wallet
                wallet_balance, wallet_currency = MLMUserManager.get_user_wallet_balance(session, user.member_id)

                # Datos de retorno completos
                mlm_data = {
                    "id": user.id,
                    "username": f"user{user.member_id}",  # Username generado basado en member_id
                    "member_id": user.member_id,
                    "status": user.status.value if hasattr(user.status, 'value') else str(user.status),
                    "firstname": first_name,
                    "lastname": last_name,
                    "full_name": full_name,  # ✅ NUEVO: Nombre completo
                    "profile_name": profile_name,  # ✅ MEJORADO: Solo primeras palabras
                    "email": user.email_cache or '',  # ✅ NUEVO: Email del usuario
                    "phone": phone_number,
                    "gender": gender_value,
                    "referral_link": user.referral_link,
                    "sponsor_id": user.sponsor_id,
                    "created_at": format_mexico_date(user.created_at) if user.created_at else '',  # ✅ MÉXICO TIMEZONE
                    "created_at_iso": user.created_at.isoformat() if user.created_at else '',  # ✅ NUEVO: Formato ISO
                    "last_login": format_mexico_datetime(user.updated_at) if user.updated_at else '',  # ✅ MÉXICO TIMEZONE
                    "current_month_rank": current_month_rank,
                    "highest_rank": highest_rank,
                    "pv_cache": user.pv_cache,  # ✅ NUEVO: PV acumulado
                    "pvg_cache": user.pvg_cache,  # ✅ NUEVO: PVG acumulado
                    "wallet_balance": wallet_balance,  # ✅ NUEVO: Balance de billetera virtual
                    "wallet_currency": wallet_currency,  # ✅ NUEVO: Moneda de la billetera
                }

                # ✅ NUEVO: Cargar datos del sponsor
                sponsor_data = MLMUserManager.load_sponsor_data(session, user)
                mlm_data["sponsor_data"] = sponsor_data
                
                print(f"✅ Datos MLM cargados exitosamente para {profile_name}")
                if sponsor_data:
                    print(f"✅ Datos de sponsor cargados: {sponsor_data.get('profile_name', 'N/A')}")
                
                return mlm_data
                
        except Exception as e:
            print(f"❌ Error detallado en load_complete_user_data: {str(e)}")
            import traceback
            traceback.print_exc()
            return {}

    @staticmethod
    def load_sponsor_data(session, user: Users) -> dict:
        """Carga datos completos del sponsor de un usuario."""
        try:
            if not user.sponsor_id:
                return {}
            
            # JOIN para obtener datos del sponsor
            sponsor = session.exec(
                sqlmodel.select(Users).where(Users.id == user.sponsor_id)
            ).first()
            
            if not sponsor:
                return {}
            
            # Cargar perfil del sponsor
            sponsor_profile = session.exec(
                sqlmodel.select(UserProfiles).where(UserProfiles.user_id == sponsor.id)
            ).first()
            
            # Construir datos del sponsor
            first_name = sponsor.first_name if sponsor.first_name else ''
            last_name = sponsor.last_name if sponsor.last_name else ''
            phone_number = sponsor_profile.phone_number if sponsor_profile else ''
            gender_value = ''
            
            if sponsor_profile and sponsor_profile.gender:
                gender_value = sponsor_profile.gender.value if hasattr(sponsor_profile.gender, 'value') else str(sponsor_profile.gender)
            
            # Construir nombres del sponsor
            full_name = f"{first_name} {last_name}".strip() if first_name or last_name else f"Usuario {sponsor.member_id}"
            
            first_word = first_name.split()[0] if first_name and first_name.split() else ""
            last_word = last_name.split()[0] if last_name and last_name.split() else ""
            
            if first_word and last_word:
                profile_name = f"{first_word} {last_word}"
            elif first_word:
                profile_name = first_word
            elif last_word:
                profile_name = last_word
            else:
                profile_name = f"Usuario {sponsor.member_id}"
            
            sponsor_data = {
                "id": sponsor.id,
                "member_id": sponsor.member_id,
                "username": f"user{sponsor.member_id}",
                "firstname": first_name,
                "lastname": last_name,
                "full_name": full_name,
                "profile_name": profile_name,
                "email": sponsor.email_cache or '',
                "phone": phone_number,
                "gender": gender_value,
                "referral_link": sponsor.referral_link or '',
                "created_at": format_mexico_date(sponsor.created_at) if sponsor.created_at else '',
                "status": sponsor.status.value if hasattr(sponsor.status, 'value') else str(sponsor.status),
                "current_month_rank": MLMUserManager.get_user_current_month_rank(session, sponsor.member_id),  # ✅ NUEVO: Rango actual del sponsor
            }
            
            return sponsor_data
            
        except Exception as e:
            print(f"❌ Error cargando datos del sponsor: {str(e)}")
            return {}

    @staticmethod
    def create_user_address(session, user_id: int, street: str, neighborhood: str, 
                           city: str, state: str, country: str, zip_code: str):
        """Crea dirección del usuario."""
        from database.addresses import Addresses
        from database.users_addresses import UserAddresses
        import datetime
        
        try:
            # ✅ Usar RegistrationManager para convertir país a valor interno
            from NNProtect_new_website.modules.auth.state.auth_state import RegistrationManager
            country_value = RegistrationManager.get_country_value(country)
            
            if not country_value:
                print(f"⚠️ País '{country}' no válido")
                return
            
            # Crear dirección con texto plano
            new_address = Addresses(
                street=street,
                neighborhood=neighborhood or "",
                city=city,
                state=state or "",
                country=country_value,  # ✅ Texto plano, no ENUM
                zip_code=zip_code or ""
            )
            session.add(new_address)
            session.flush()
            
            # Crear vinculación usuario-dirección
            user_address = UserAddresses(
                user_id=user_id,
                address_id=new_address.id,
                address_name="Principal",
                is_default=True,
                created_at=get_mexico_now(),  # ✅ MÉXICO TIMEZONE
                updated_at=get_mexico_now()  # ✅ MÉXICO TIMEZONE
            )
            session.add(user_address)
            print(f"✅ Dirección creada para usuario {user_id}")
            
        except Exception as e:
            print(f"❌ Error creando dirección: {e}")
            # No fallar el registro completo por error de dirección
    
    @staticmethod
    def get_user_level(user_member_id: int, root_sponsor_id: int) -> int:
        """
        Calcula el nivel de un usuario respecto a un sponsor raíz usando BFS.
        
        Args:
            user_member_id: member_id del usuario a evaluar
            root_sponsor_id: member_id del sponsor raíz (usuario autenticado)
            
        Returns:
            int: Nivel del usuario (1, 2, 3, etc.) o 0 si no está en la red
        """
        try:
            if user_member_id == root_sponsor_id:
                return 0  # El sponsor raíz es nivel 0
            
            with rx.session() as session:
                # BFS desde el sponsor raíz hacia abajo
                from collections import deque
                
                # Cola: (member_id, nivel)
                queue = deque([(root_sponsor_id, 0)])
                visited = set([root_sponsor_id])
                
                while queue:
                    current_id, current_level = queue.popleft()
                    
                    # Buscar todos los usuarios directos de current_id
                    direct_users = session.exec(
                        sqlmodel.select(UserTreePath)
                        .where(UserTreePath.ancestor_id == current_id)
                    ).all()
                    
                    for tree_path in direct_users:
                        child_id = tree_path.descendant_id
                        child_level = current_level + 1
                        
                        # Si encontramos al usuario buscado
                        if child_id == user_member_id:
                            print(f"✅ Usuario {user_member_id} encontrado en nivel {child_level} de {root_sponsor_id}")
                            return child_level
                        
                        # Si no lo hemos visitado, agregarlo a la cola
                        if child_id not in visited:
                            visited.add(child_id)
                            queue.append((child_id, child_level))
                
                # Usuario no encontrado en la red
                print(f"⚠️ Usuario {user_member_id} no encontrado en la red de {root_sponsor_id}")
                return 0
                
        except Exception as e:
            print(f"❌ Error calculando nivel de usuario {user_member_id}: {e}")
            import traceback
            traceback.print_exc()
            return 0

    @staticmethod
    def get_network_descendants(sponsor_member_id: int, root_user_id: Optional[int] = None) -> list:
        """
        Obtiene toda la red descendente de un sponsor usando UserTreePath.
        Optimizado con Path Enumeration Pattern - elimina recursión innecesaria.

        Args:
            sponsor_member_id: member_id del sponsor principal
            root_user_id: member_id del usuario autenticado (para calcular niveles)

        Returns:
            Lista de diccionarios con datos de usuarios descendentes
        """
        try:
            with rx.session() as session:
                # Query optimizado con JOIN para obtener todos los datos en una sola consulta
                descendants_query = session.exec(
                    sqlmodel.select(Users, UserTreePath, UserProfiles)
                    .join(UserTreePath, Users.member_id == UserTreePath.descendant_id)
                    .outerjoin(UserProfiles, Users.id == UserProfiles.user_id)
                    .where(
                        UserTreePath.ancestor_id == sponsor_member_id,
                        UserTreePath.depth > 0  # Excluir self-reference
                    )
                    .order_by(UserTreePath.depth, Users.member_id)
                ).all()

                descendants = []
                sponsor_cache = {}  # Cache para evitar queries repetidas de sponsors

                for user, tree_path, user_profile in descendants_query:
                    # Obtener datos del sponsor (con cache)
                    sponsor_data = {}
                    if user.sponsor_id:
                        if user.sponsor_id not in sponsor_cache:
                            sponsor_result = session.exec(
                                sqlmodel.select(Users, UserProfiles)
                                .outerjoin(UserProfiles, Users.id == UserProfiles.user_id)
                                .where(Users.member_id == user.sponsor_id)
                            ).first()

                            if sponsor_result:
                                sponsor_user, sponsor_profile = sponsor_result
                                sponsor_cache[user.sponsor_id] = {
                                    "id": sponsor_user.id,
                                    "member_id": sponsor_user.member_id,
                                    "first_name": sponsor_user.first_name or "",
                                    "last_name": sponsor_user.last_name or "",
                                    "full_name": f"{sponsor_user.first_name or ''} {sponsor_user.last_name or ''}".strip(),
                                    "phone": sponsor_profile.phone_number if sponsor_profile else "",
                                    "email": sponsor_user.email_cache or ""
                                }

                        sponsor_data = sponsor_cache.get(user.sponsor_id, {})

                    # Formatear fecha a DD/MM/YYYY
                    formatted_date = user.created_at.strftime("%d/%m/%Y") if user.created_at else "N/A"

                    # Nivel ya viene directamente de tree_path.depth (más eficiente)
                    user_level = tree_path.depth

                    user_data = {
                        "id": user.id,
                        "member_id": user.member_id,
                        "first_name": user.first_name or "",
                        "last_name": user.last_name or "",
                        "full_name": f"{user.first_name or ''} {user.last_name or ''}".strip() if (user.first_name or user.last_name) else "N/A",
                        "email": user.email_cache or "",
                        "status": user.status.value if hasattr(user.status, 'value') else str(user.status),
                        "created_at": formatted_date,
                        "phone": user_profile.phone_number if user_profile else "",
                        "sponsor_member_id": sponsor_data.get("member_id", None),
                        "level": user_level,
                        "sponsor_full_name": sponsor_data.get("full_name", "N/A"),
                        "sponsor_phone": sponsor_data.get("phone", "N/A")
                    }
                    descendants.append(user_data)

                return descendants

        except Exception as e:
            print(f"❌ Error obteniendo red descendente: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    @staticmethod
    def _filter_registrations_by_date_range(sponsor_member_id: int, start_date, end_date) -> list:
        """
        Método privado que filtra registraciones por rango de fechas.
        Aplica POO para reutilizar lógica común.
        
        Args:
            sponsor_member_id: member_id del sponsor principal
            start_date: fecha de inicio (inclusive)
            end_date: fecha de fin (inclusive)
            
        Returns:
            Lista de usuarios registrados en el rango de fechas
        """
        try:
            # Obtener toda la red descendente pasando el sponsor como root para niveles
            all_descendants = MLMUserManager.get_network_descendants(sponsor_member_id, sponsor_member_id)
            
            # Filtrar por rango de fechas
            filtered_registrations = []
            from datetime import datetime
            
            # Convertir start_date y end_date a date objects para comparación consistente
            start_date_only = start_date.date() if hasattr(start_date, 'date') else start_date
            end_date_only = end_date.date() if hasattr(end_date, 'date') else end_date
            
            for user in all_descendants:
                if user.get("created_at") and user["created_at"] != "N/A":
                    try:
                        # Parsear string formato DD/MM/YYYY a date object
                        created_at_str = user["created_at"]  # "26/09/2025"
                        created_at_date = datetime.strptime(created_at_str, "%d/%m/%Y").date()
                        
                        # Comparar fechas
                        if start_date_only <= created_at_date <= end_date_only:
                            filtered_registrations.append(user)
                            
                    except ValueError as ve:
                        print(f"⚠️ Error parseando fecha '{user['created_at']}': {ve}")
                        continue
            
            print(f"✅ Filtradas {len(filtered_registrations)} registraciones entre {start_date_only} y {end_date_only}")
            return filtered_registrations
            
        except Exception as e:
            print(f"❌ Error filtrando registraciones por fecha: {e}")
            return []

    @staticmethod
    def get_todays_registrations(sponsor_member_id: int) -> list:
        """
        Obtiene las inscripciones del día de la red de un sponsor.
        
        Args:
            sponsor_member_id: member_id del sponsor principal
            
        Returns:
            Lista de usuarios registrados hoy en la red
        """
        try:
            # ✅ USAR FECHA DE MÉXICO
            today = get_mexico_date()
            
            # Reutilizar lógica común usando POO
            return MLMUserManager._filter_registrations_by_date_range(sponsor_member_id, today, today)
            
        except Exception as e:
            print(f"❌ Error obteniendo inscripciones del día: {e}")
            return []

    @staticmethod
    def get_monthly_registrations(sponsor_member_id: int) -> list:
        """
        Obtiene las inscripciones del mes actual de la red de un sponsor
        según el período corriendo en ese instante.

        Args:
            sponsor_member_id: member_id del sponsor principal

        Returns:
            Lista de usuarios registrados en el período actual
        """
        try:
            from .period_service import PeriodService

            # Obtener el período actual
            with rx.session() as session:
                current_period = PeriodService.get_current_period(session)

                if not current_period:
                    print("⚠️ No hay período actual activo")
                    return []

                # Convertir starts_on y ends_on a date objects para comparación
                start_date = current_period.starts_on.date()
                end_date = current_period.ends_on.date()

                print(f"📅 Filtrando registros por período actual: {current_period.name} ({start_date} a {end_date})")

            # Reutilizar lógica común usando POO
            return MLMUserManager._filter_registrations_by_date_range(sponsor_member_id, start_date, end_date)

        except Exception as e:
            print(f"❌ Error obteniendo inscripciones del mes: {e}")
            import traceback
            traceback.print_exc()
            return []

    @staticmethod
    def get_all_registrations(sponsor_member_id: int) -> list:
        """
        Obtiene TODAS las inscripciones de la red de un sponsor usando CTE recursivo,
        sin importar el período o fecha de registro.
        
        Usa el mismo enfoque que tu query SQL - recursión directa sobre sponsor_id
        en lugar de depender de UserTreePath.

        Args:
            sponsor_member_id: member_id del sponsor principal

        Returns:
            Lista de TODOS los usuarios registrados en la red (histórico completo)
        """
        try:
            print(f"🔄 Obteniendo TODAS las inscripciones para member_id: {sponsor_member_id}")
            
            with rx.session() as session:
                # CTE recursivo - Igual que tu SQL
                # Busca todos los descendientes usando sponsor_id
                recursive_query = sqlmodel.text("""
                    WITH RECURSIVE network_tree AS (
                        -- Caso base: el usuario raíz
                        SELECT 
                            u.id,
                            u.member_id,
                            u.first_name,
                            u.last_name,
                            u.email_cache,
                            u.sponsor_id,
                            u.status,
                            u.created_at,
                            1 AS level,
                            ARRAY[u.member_id] AS path
                        FROM users u
                        WHERE u.member_id = :root_member_id
                        
                        UNION ALL
                        
                        -- Caso recursivo: todos los referidos directos e indirectos
                        SELECT 
                            u.id,
                            u.member_id,
                            u.first_name,
                            u.last_name,
                            u.email_cache,
                            u.sponsor_id,
                            u.status,
                            u.created_at,
                            nt.level + 1 AS level,
                            nt.path || u.member_id AS path
                        FROM users u
                        INNER JOIN network_tree nt ON u.sponsor_id = nt.member_id
                        WHERE NOT (u.member_id = ANY(nt.path))  -- Evitar ciclos
                    )
                    SELECT 
                        id,
                        member_id,
                        first_name,
                        last_name,
                        email_cache,
                        sponsor_id,
                        status,
                        created_at,
                        level
                    FROM network_tree
                    WHERE level > 1  -- Excluir el usuario raíz
                    ORDER BY level, member_id
                """)
                
                # Ejecutar query con parámetros
                result = session.execute(
                    recursive_query.bindparams(root_member_id=sponsor_member_id)
                )
                
                # Procesar resultados
                descendants = []
                sponsor_cache = {}  # Cache para sponsors
                
                for row in result:
                    # Obtener datos del sponsor (con cache)
                    sponsor_data = {}
                    if row.sponsor_id:
                        if row.sponsor_id not in sponsor_cache:
                            sponsor_result = session.exec(
                                sqlmodel.select(Users, UserProfiles)
                                .outerjoin(UserProfiles, Users.id == UserProfiles.user_id)
                                .where(Users.member_id == row.sponsor_id)
                            ).first()

                            if sponsor_result:
                                sponsor_user, sponsor_profile = sponsor_result
                                sponsor_cache[row.sponsor_id] = {
                                    "id": sponsor_user.id,
                                    "member_id": sponsor_user.member_id,
                                    "first_name": sponsor_user.first_name or "",
                                    "last_name": sponsor_user.last_name or "",
                                    "full_name": f"{sponsor_user.first_name or ''} {sponsor_user.last_name or ''}".strip(),
                                    "phone": sponsor_profile.phone_number if sponsor_profile else "",
                                    "email": sponsor_user.email_cache or ""
                                }

                        sponsor_data = sponsor_cache.get(row.sponsor_id, {})
                    
                    # Obtener teléfono del usuario
                    user_profile = session.exec(
                        sqlmodel.select(UserProfiles)
                        .where(UserProfiles.user_id == row.id)
                    ).first()
                    
                    # Formatear fecha
                    formatted_date = row.created_at.strftime("%d/%m/%Y") if row.created_at else "N/A"
                    
                    user_data = {
                        "id": row.id,
                        "member_id": row.member_id,
                        "first_name": row.first_name or "",
                        "last_name": row.last_name or "",
                        "full_name": f"{row.first_name or ''} {row.last_name or ''}".strip() if (row.first_name or row.last_name) else "N/A",
                        "email": row.email_cache or "",
                        "status": row.status if isinstance(row.status, str) else row.status.value,
                        "created_at": formatted_date,
                        "phone": user_profile.phone_number if user_profile else "",
                        "sponsor_member_id": sponsor_data.get("member_id", None),
                        "level": row.level,
                        "sponsor_full_name": sponsor_data.get("full_name", "N/A"),
                        "sponsor_phone": sponsor_data.get("phone", "N/A")
                    }
                    descendants.append(user_data)
                
                print(f"✅ Obtenidas {len(descendants)} inscripciones totales en la red")
                return descendants
            
        except Exception as e:
            print(f"❌ Error obteniendo todas las inscripciones: {e}")
            import traceback
            traceback.print_exc()
            return []

    @staticmethod
    def get_period_volumes(member_id: int) -> dict:
        """
        Obtiene volúmenes por periodo y por nivel desde la tabla precalculada unilevel_report.
        Retorna los últimos 6 periodos con PV y PVG desglosados por niveles (1-9).
        
        Args:
            member_id: ID del usuario (member_id en Users)
            
        Returns:
            Diccionario con estructura plana para acceso fácil desde Reflex
            {
                "period_names": ["2025-10", "2025-09", ...],
                "pv_0": "1,500", "pv_1": "1,200", ...,
                "level_1_0": "3,200", "level_1_1": "2,800", ...,
                ...
            }
        """
        try:
            from database.periods import Periods
            from database.unilevel_report import UnilevelReports
            from database.users import Users
            
            with rx.session() as session:
                print(f"🔄 Obteniendo volúmenes por periodo para member_id: {member_id}")
                
                # 1️⃣ Obtener user_id desde member_id
                user = session.exec(
                    sqlmodel.select(Users).where(Users.member_id == member_id)
                ).first()
                
                if not user:
                    print(f"⚠️  Usuario con member_id={member_id} no encontrado")
                    # Retornar estructura vacía
                    result = {"period_names": [f"Mes {i+1}" for i in range(6)]}
                    for idx in range(6):
                        result[f"pv_{idx}"] = "0"
                        for level in range(1, 10):
                            result[f"level_{level}_{idx}"] = "0"
                    return result
                
                user_id = user.id
                
                # 2️⃣ Obtener últimos 6 periodos
                periods = session.exec(
                    sqlmodel.select(Periods)
                    .order_by(sqlmodel.desc(Periods.starts_on))
                    .limit(6)
                ).all()
                
                # 3️⃣ Crear estructura plana con datos de unilevel_report
                result = {"period_names": []}
                
                for idx, period in enumerate(periods):
                    result["period_names"].append(period.name)
                    
                    # Buscar reporte de este usuario en este periodo
                    report = session.exec(
                        sqlmodel.select(UnilevelReports)
                        .where(
                            UnilevelReports.user_id == user_id,
                            UnilevelReports.period_id == period.id
                        )
                    ).first()
                    
                    if report:
                        result[f"pv_{idx}"] = f"{report.pv:,}"
                        result[f"level_1_{idx}"] = f"{report.pvg_1:,}"
                        result[f"level_2_{idx}"] = f"{report.pvg_2:,}"
                        result[f"level_3_{idx}"] = f"{report.pvg_3:,}"
                        result[f"level_4_{idx}"] = f"{report.pvg_4:,}"
                        result[f"level_5_{idx}"] = f"{report.pvg_5:,}"
                        result[f"level_6_{idx}"] = f"{report.pvg_6:,}"
                        result[f"level_7_{idx}"] = f"{report.pvg_7:,}"
                        result[f"level_8_{idx}"] = f"{report.pvg_8:,}"
                        result[f"level_9_{idx}"] = f"{report.pvg_9:,}"
                        print(f"  ✅ Periodo '{period.name}': PV={report.pv}")
                    else:
                        # Sin reporte, todos en 0
                        result[f"pv_{idx}"] = "0"
                        for level in range(1, 10):
                            result[f"level_{level}_{idx}"] = "0"
                        print(f"  ⚠️  Periodo '{period.name}': Sin reporte")
                
                # 4️⃣ Rellenar con periodos vacíos hasta completar 6
                while len(result["period_names"]) < 6:
                    idx = len(result["period_names"])
                    period_num = idx + 1
                    result["period_names"].append(f"Mes {period_num}")
                    result[f"pv_{idx}"] = "0"
                    for level in range(1, 10):
                        result[f"level_{level}_{idx}"] = "0"
                
                print(f"✅ Retornando volúmenes de {len(result['period_names'])} periodos")
                return result
                
        except Exception as e:
            print(f"❌ Error obteniendo volúmenes por periodo: {e}")
            import traceback
            traceback.print_exc()
            # Retornar estructura vacía
            result = {"period_names": [f"Mes {i+1}" for i in range(6)]}
            for idx in range(6):
                result[f"pv_{idx}"] = "0"
                for level in range(1, 10):
                    result[f"level_{level}_{idx}"] = "0"
            return result

    @staticmethod
    def update_unilevel_report_for_order(order_member_id: int, period_id: int):
        """
        Actualiza la tabla unilevel_report para todos los ancestros del usuario que hizo la orden.
        Se debe llamar cada vez que se complete una orden.
        
        Args:
            order_member_id: member_id del usuario que hizo la orden
            period_id: ID del periodo de la orden
        """
        try:
            from database.unilevel_report import UnilevelReports
            from database.users import Users
            from database.orders import Orders
            
            with rx.session() as session:
                print(f"🔄 Actualizando unilevel_report para orden de member_id={order_member_id}, periodo={period_id}")
                
                # 1️⃣ Obtener user_id del comprador
                buyer = session.exec(
                    sqlmodel.select(Users).where(Users.member_id == order_member_id)
                ).first()
                
                if not buyer:
                    print(f"⚠️  Usuario comprador no encontrado")
                    return
                
                # 2️⃣ Actualizar el PV personal del comprador
                pv_total = session.exec(
                    sqlmodel.select(sqlmodel.func.sum(Orders.total_pv))
                    .where(
                        Orders.member_id == order_member_id,
                        Orders.period_id == period_id,
                        Orders.status == "completed"
                    )
                ).first() or 0
                
                buyer_report = session.exec(
                    sqlmodel.select(UnilevelReports)
                    .where(
                        UnilevelReports.user_id == buyer.id,
                        UnilevelReports.period_id == period_id
                    )
                ).first()
                
                # Calcular VN total del comprador
                vn_total = session.exec(
                    sqlmodel.select(sqlmodel.func.sum(Orders.total_vn))
                    .where(
                        Orders.member_id == order_member_id,
                        Orders.period_id == period_id,
                        Orders.status == "completed"
                    )
                ).first() or 0.0
                
                if buyer_report:
                    buyer_report.pv = int(pv_total)
                    buyer_report.vn = float(vn_total)
                else:
                    buyer_report = UnilevelReports(
                        user_id=buyer.id,
                        period_id=period_id,
                        pv=int(pv_total),
                        vn=float(vn_total)
                    )
                    session.add(buyer_report)
                
                # 🆕 Calcular totales para el comprador (no tiene PVG, solo PV personal)
                buyer_report.pvg_total = 0
                buyer_report.vng_total = 0.0
                
                # 3️⃣ Obtener todos los ancestros y actualizar sus PVG por nivel
                ancestors = session.exec(
                    sqlmodel.select(UserTreePath)
                    .where(UserTreePath.descendant_id == order_member_id)
                ).all()
                
                for ancestor_path in ancestors:
                    if ancestor_path.depth == 0:
                        continue  # Skip self
                    
                    ancestor_member_id = ancestor_path.ancestor_id
                    depth = ancestor_path.depth
                    
                    # Obtener user_id del ancestro
                    ancestor_user = session.exec(
                        sqlmodel.select(Users).where(Users.member_id == ancestor_member_id)
                    ).first()
                    
                    if not ancestor_user:
                        continue
                    
                    # Calcular PVG para este nivel
                    descendants_at_this_level = session.exec(
                        sqlmodel.select(UserTreePath.descendant_id)
                        .where(
                            UserTreePath.ancestor_id == ancestor_member_id,
                            UserTreePath.depth == depth
                        )
                    ).all()
                    
                    pvg_for_level = session.exec(
                        sqlmodel.select(sqlmodel.func.sum(Orders.total_pv))
                        .where(
                            Orders.member_id.in_(descendants_at_this_level),
                            Orders.period_id == period_id,
                            Orders.status == "completed"
                        )
                    ).first() or 0
                    
                    vng_for_level = session.exec(
                        sqlmodel.select(sqlmodel.func.sum(Orders.total_vn))
                        .where(
                            Orders.member_id.in_(descendants_at_this_level),
                            Orders.period_id == period_id,
                            Orders.status == "completed"
                        )
                    ).first() or 0.0
                    
                    # Actualizar/crear reporte del ancestro
                    ancestor_report = session.exec(
                        sqlmodel.select(UnilevelReports)
                        .where(
                            UnilevelReports.user_id == ancestor_user.id,
                            UnilevelReports.period_id == period_id
                        )
                    ).first()
                    
                    if not ancestor_report:
                        ancestor_report = UnilevelReports(
                            user_id=ancestor_user.id,
                            period_id=period_id
                        )
                        session.add(ancestor_report)
                    
                    # Actualizar el PVG y VNG del nivel correspondiente
                    if depth == 1:
                        ancestor_report.pvg_1 = int(pvg_for_level)
                        ancestor_report.vng_1 = float(vng_for_level)
                    elif depth == 2:
                        ancestor_report.pvg_2 = int(pvg_for_level)
                        ancestor_report.vng_2 = float(vng_for_level)
                    elif depth == 3:
                        ancestor_report.pvg_3 = int(pvg_for_level)
                        ancestor_report.vng_3 = float(vng_for_level)
                    elif depth == 4:
                        ancestor_report.pvg_4 = int(pvg_for_level)
                        ancestor_report.vng_4 = float(vng_for_level)
                    elif depth == 5:
                        ancestor_report.pvg_5 = int(pvg_for_level)
                        ancestor_report.vng_5 = float(vng_for_level)
                    elif depth == 6:
                        ancestor_report.pvg_6 = int(pvg_for_level)
                        ancestor_report.vng_6 = float(vng_for_level)
                    elif depth == 7:
                        ancestor_report.pvg_7 = int(pvg_for_level)
                        ancestor_report.vng_7 = float(vng_for_level)
                    elif depth == 8:
                        ancestor_report.pvg_8 = int(pvg_for_level)
                        ancestor_report.vng_8 = float(vng_for_level)
                    elif depth == 9:
                        ancestor_report.pvg_9 = int(pvg_for_level)
                        ancestor_report.vng_9 = float(vng_for_level)
                    elif depth >= 10:
                        ancestor_report.pvg_10_plus = int(pvg_for_level)
                        ancestor_report.vng_10_plus = float(vng_for_level)
                    
                    # 🆕 Calcular totales agregados
                    ancestor_report.pvg_total = (
                        (ancestor_report.pvg_1 or 0) +
                        (ancestor_report.pvg_2 or 0) +
                        (ancestor_report.pvg_3 or 0) +
                        (ancestor_report.pvg_4 or 0) +
                        (ancestor_report.pvg_5 or 0) +
                        (ancestor_report.pvg_6 or 0) +
                        (ancestor_report.pvg_7 or 0) +
                        (ancestor_report.pvg_8 or 0) +
                        (ancestor_report.pvg_9 or 0) +
                        (ancestor_report.pvg_10_plus or 0)
                    )
                    
                    ancestor_report.vng_total = (
                        (ancestor_report.vng_1 or 0.0) +
                        (ancestor_report.vng_2 or 0.0) +
                        (ancestor_report.vng_3 or 0.0) +
                        (ancestor_report.vng_4 or 0.0) +
                        (ancestor_report.vng_5 or 0.0) +
                        (ancestor_report.vng_6 or 0.0) +
                        (ancestor_report.vng_7 or 0.0) +
                        (ancestor_report.vng_8 or 0.0) +
                        (ancestor_report.vng_9 or 0.0) +
                        (ancestor_report.vng_10_plus or 0.0)
                    )
                
                session.commit()
                print(f"✅ unilevel_report actualizado correctamente")
                
        except Exception as e:
            print(f"❌ Error actualizando unilevel_report: {e}")
            import traceback
            traceback.print_exc()

    # 🎯 MÉTODOS PARA GESTIÓN AUTOMÁTICA DE RANGOS
    @staticmethod
    def get_user_current_month_rank(session, member_id: int) -> str:
        """
        Obtiene el rango actual del período activo del usuario.
        Retorna "Sin rango" si no tiene rangos en el período actual.
        
        ACTUALIZADO: Filtra por period_id del período actual en lugar de año/mes.
        Esto asegura que el rango se tome del período corriendo.
        """
        try:
            from database.user_rank_history import UserRankHistory
            from database.ranks import Ranks
            from database.periods import Periods
            from NNProtect_new_website.utils.timezone_mx import get_mexico_now

            # Obtener período actual
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
                return "Sin rango"

            # JOIN explícito entre Ranks y UserRankHistory, filtrando por period_id
            latest_rank = session.exec(
                sqlmodel.select(Ranks)
                .join(UserRankHistory, Ranks.id == UserRankHistory.rank_id)
                .where(
                    (UserRankHistory.member_id == member_id) &
                    (UserRankHistory.period_id == current_period.id)
                )
                .order_by(sqlmodel.desc(UserRankHistory.rank_id))
            ).first()

            return latest_rank.name if latest_rank else "Sin rango"

        except Exception as e:
            print(f"❌ Error obteniendo rango mensual de usuario {member_id}: {e}")
            import traceback
            traceback.print_exc()
            return "Sin rango"

    @staticmethod
    def get_user_highest_rank(session, member_id: int) -> str:
        """
        Obtiene el rango máximo alcanzado por el usuario en toda su vida.
        Retorna 1 (Sin rango) si no tiene rangos.
        """
        try:
            from database.user_rank_history import UserRankHistory
            from database.ranks import Ranks

            # Buscar el rango más alto de toda la vida con JOIN para obtener el nombre
            highest_rank = session.exec(
                sqlmodel.select(Ranks)
                .join(UserRankHistory, Ranks.id == UserRankHistory.rank_id)
                .where(UserRankHistory.member_id == member_id)
                .order_by(sqlmodel.desc(UserRankHistory.rank_id))
            ).first()

            return highest_rank.name if highest_rank else "Sin rango"

        except Exception as e:
            print(f"❌ Error obteniendo rango máximo de usuario {member_id}: {e}")
            import traceback
            traceback.print_exc()
            return "Sin rango"

    @staticmethod
    def promote_user_rank(member_id: int, new_rank_id: int) -> bool:
        """Promueve usuario a un nuevo rango."""
        try:
            with rx.session() as session:
                success = RankService.promote_user_rank(session, member_id, new_rank_id)
                if success:
                    session.commit()
                return success
        except Exception as e:
            print(f"❌ Error promoviendo usuario: {e}")
            return False

    @staticmethod
    def get_user_rank_history(member_id: int) -> list:
        """Obtiene historial completo de rangos del usuario."""
        try:
            with rx.session() as session:
                return RankService.get_rank_progression_history(session, member_id)
        except Exception as e:
            print(f"❌ Error obteniendo historial de rangos: {e}")
            return []

    @staticmethod
    def get_user_wallet_balance(session, member_id: int) -> tuple:
        """
        Obtiene el balance actual de la billetera virtual del usuario.

        Args:
            session: Sesión de base de datos
            member_id: ID del usuario

        Returns:
            Tupla (balance, currency) - (0.0, "MXN") si no tiene wallet
        """
        try:
            from database.wallet import Wallets

            wallet = session.exec(
                sqlmodel.select(Wallets).where(Wallets.member_id == member_id)
            ).first()

            if wallet:
                return (wallet.balance, wallet.currency)
            else:
                # Retornar valores por defecto si no tiene wallet
                return (0.0, "MXN")

        except Exception as e:
            print(f"❌ Error obteniendo balance de wallet para usuario {member_id}: {e}")
            return (0.0, "MXN")