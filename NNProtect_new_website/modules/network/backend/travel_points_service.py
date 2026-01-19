"""
Servicio POO para gestión de puntos NN Travel.
Maneja acumulación de puntos por kits, rangos propios y rangos de directos.

Principios aplicados: KISS, DRY, YAGNI, POO
"""

import sqlmodel
from typing import Optional, Dict
from datetime import datetime, timezone

from database.travel_campaigns import (
    TravelCampaigns, NNTravelPoints, NNTravelPointsHistory,
    CampaignStatus, TravelEventType
)


class TravelPointsService:
    """
    Servicio POO para gestión de puntos NN Travel.
    Principio POO: Encapsula lógica de acumulación de puntos de viaje.
    """

    # Puntos por kits (base)
    KIT_POINTS = {
        "full_supplement": 1,
        "full_skin": 2,
        "full_protect": 4
    }

    # Puntos por rangos del usuario (base y promo)
    RANK_POINTS = {
        "Visionario": {"base": 1, "promo": 2},
        "Emprendedor": {"base": 5, "promo": 10},
        "Creativo": {"base": 15, "promo": 30},
        "Innovador": {"base": 25, "promo": 50},
        "Embajador Transformador": {"base": 50, "promo": 100},
        "Embajador Inspirador": {"base": 100, "promo": 200},
        "Embajador Consciente": {"base": 200, "promo": 200},
        "Embajador Solidario": {"base": 200, "promo": 200}
    }

    @classmethod
    def create_campaign(
        cls,
        session,
        name: str,
        start_date: datetime,
        end_date: datetime,
        period_id: int,
        target_points: int = 200,
        is_promo_active: bool = False,
        description: Optional[str] = None
    ) -> Optional[int]:
        """
        Crea una nueva campaña de NN Travel.

        Args:
            session: Sesión de base de datos
            name: Nombre de la campaña (ej: "Campaña 2025-H1")
            start_date: Fecha de inicio
            end_date: Fecha de fin (6 meses después)
            period_id: ID del período asociado
            target_points: Meta de puntos (default: 200)
            is_promo_active: Si hay puntos duplicados
            description: Descripción opcional

        Returns:
            ID de campaña creada o None si falla
        """
        try:
            campaign = TravelCampaigns(
                name=name,
                description=description,
                start_date=start_date,
                end_date=end_date,
                target_points=target_points,
                is_promo_active=is_promo_active,
                period_id=period_id,
                status=CampaignStatus.ACTIVE.value
            )

            session.add(campaign)
            session.flush()

            print(f"✅ Campaña NN Travel creada: {name} (ID: {campaign.id})")
            return campaign.id

        except Exception as e:
            print(f"❌ Error creando campaña NN Travel: {e}")
            import traceback
            traceback.print_exc()
            return None

    @classmethod
    def get_active_campaign(cls, session) -> Optional[TravelCampaigns]:
        """
        Obtiene la campaña activa actual.

        Args:
            session: Sesión de base de datos

        Returns:
            Campaña activa o None
        """
        try:
            now = datetime.now(timezone.utc)

            campaign = session.exec(
                sqlmodel.select(TravelCampaigns)
                .where(
                    (TravelCampaigns.status == CampaignStatus.ACTIVE.value) &
                    (TravelCampaigns.start_date <= now) &
                    (TravelCampaigns.end_date >= now)
                )
                .order_by(sqlmodel.desc(TravelCampaigns.start_date))
            ).first()

            return campaign

        except Exception as e:
            print(f"❌ Error obteniendo campaña activa: {e}")
            return None

    @classmethod
    def get_or_create_user_points(
        cls,
        session,
        member_id: int,
        campaign_id: int
    ) -> Optional[NNTravelPoints]:
        """
        Obtiene o crea el registro de puntos de un usuario para una campaña.

        Args:
            session: Sesión de base de datos
            member_id: ID del usuario
            campaign_id: ID de la campaña

        Returns:
            Registro de puntos o None si falla
        """
        try:
            # Buscar registro existente
            user_points = session.exec(
                sqlmodel.select(NNTravelPoints)
                .where(
                    (NNTravelPoints.member_id == member_id) &
                    (NNTravelPoints.campaign_id == campaign_id)
                )
            ).first()

            if user_points:
                return user_points

            # Crear nuevo registro
            user_points = NNTravelPoints(
                member_id=member_id,
                campaign_id=campaign_id,
                points_from_kits=0,
                points_from_self_ranks=0,
                points_from_direct_ranks=0,
                points_bonus=0,
                total_points=0,
                qualifies_for_travel=False
            )

            session.add(user_points)
            session.flush()

            return user_points

        except Exception as e:
            print(f"❌ Error obteniendo/creando puntos de usuario {member_id}: {e}")
            import traceback
            traceback.print_exc()
            return None

    @classmethod
    def add_points_from_kit(
        cls,
        session,
        member_id: int,
        kit_type: str,
        order_id: int,
        buyer_member_id: int,
        campaign_id: Optional[int] = None
    ) -> bool:
        """
        Añade puntos por compra de kit en la red.

        Args:
            session: Sesión de base de datos
            member_id: ID del usuario que recibe los puntos
            kit_type: Tipo de kit (full_supplement, full_skin, full_protect)
            order_id: ID de la orden
            buyer_member_id: ID del comprador
            campaign_id: ID de campaña (si no se provee, usa la activa)

        Returns:
            True si se añadieron exitosamente, False si falló
        """
        try:
            # Obtener campaña activa si no se especificó
            if campaign_id is None:
                campaign = cls.get_active_campaign(session)
                if not campaign:
                    print(f"⚠️  No hay campaña activa")
                    return False
                campaign_id = campaign.id
                is_promo = campaign.is_promo_active
                target_points = campaign.target_points
            else:
                campaign = session.get(TravelCampaigns, campaign_id)
                is_promo = campaign.is_promo_active if campaign else False
                target_points = campaign.target_points if campaign else 200

            # Obtener o crear registro de puntos
            user_points = cls.get_or_create_user_points(session, member_id, campaign_id)
            if not user_points:
                return False

            # Calcular puntos (promo duplica puntos)
            base_points = cls.KIT_POINTS.get(kit_type, 0)
            if base_points == 0:
                print(f"⚠️  Tipo de kit desconocido: {kit_type}")
                return False

            points_to_add = base_points * 2 if is_promo else base_points

            # Actualizar puntos
            user_points.points_from_kits += points_to_add
            user_points.recalculate_total()
            user_points.update_qualification(target_points)

            # Crear historial
            history = NNTravelPointsHistory(
                member_id=member_id,
                campaign_id=campaign_id,
                event_type=TravelEventType.KIT_PURCHASE.value,
                points_earned=points_to_add,
                source_member_id=buyer_member_id,
                source_order_id=order_id,
                description=f"Puntos por kit {kit_type} comprado por usuario {buyer_member_id}"
            )

            session.add(history)
            session.flush()

            print(f"✅ Usuario {member_id} ganó {points_to_add} puntos por kit {kit_type}")
            return True

        except Exception as e:
            print(f"❌ Error añadiendo puntos de kit para usuario {member_id}: {e}")
            import traceback
            traceback.print_exc()
            return False

    @classmethod
    def add_points_from_rank(
        cls,
        session,
        member_id: int,
        rank_name: str,
        campaign_id: Optional[int] = None
    ) -> bool:
        """
        Añade puntos por rango alcanzado por el usuario.

        Args:
            session: Sesión de base de datos
            member_id: ID del usuario
            rank_name: Nombre del rango alcanzado
            campaign_id: ID de campaña (si no se provee, usa la activa)

        Returns:
            True si se añadieron exitosamente, False si falló
        """
        try:
            # Obtener campaña activa si no se especificó
            if campaign_id is None:
                campaign = cls.get_active_campaign(session)
                if not campaign:
                    print(f"⚠️  No hay campaña activa")
                    return False
                campaign_id = campaign.id
                is_promo = campaign.is_promo_active
                target_points = campaign.target_points
            else:
                campaign = session.get(TravelCampaigns, campaign_id)
                is_promo = campaign.is_promo_active if campaign else False
                target_points = campaign.target_points if campaign else 200

            # Obtener o crear registro de puntos
            user_points = cls.get_or_create_user_points(session, member_id, campaign_id)
            if not user_points:
                return False

            # Obtener puntos del rango
            rank_config = cls.RANK_POINTS.get(rank_name)
            if not rank_config:
                print(f"⚠️  Rango desconocido: {rank_name}")
                return False

            points_to_add = rank_config["promo"] if is_promo else rank_config["base"]

            # Actualizar puntos
            user_points.points_from_self_ranks += points_to_add
            user_points.recalculate_total()
            user_points.update_qualification(target_points)

            # Crear historial
            history = NNTravelPointsHistory(
                member_id=member_id,
                campaign_id=campaign_id,
                event_type=TravelEventType.SELF_RANK.value,
                points_earned=points_to_add,
                rank_achieved=rank_name,
                description=f"Puntos por alcanzar rango {rank_name}"
            )

            session.add(history)
            session.flush()

            print(f"✅ Usuario {member_id} ganó {points_to_add} puntos por rango {rank_name}")
            return True

        except Exception as e:
            print(f"❌ Error añadiendo puntos de rango para usuario {member_id}: {e}")
            import traceback
            traceback.print_exc()
            return False

    @classmethod
    def add_points_from_direct_rank(
        cls,
        session,
        sponsor_id: int,
        direct_member_id: int,
        rank_name: str,
        campaign_id: Optional[int] = None
    ) -> bool:
        """
        Añade puntos al sponsor por rango alcanzado por su directo.

        Args:
            session: Sesión de base de datos
            sponsor_id: ID del sponsor que recibe puntos
            direct_member_id: ID del directo que alcanzó el rango
            rank_name: Nombre del rango alcanzado
            campaign_id: ID de campaña (si no se provee, usa la activa)

        Returns:
            True si se añadieron exitosamente, False si falló
        """
        try:
            # Obtener campaña activa si no se especificó
            if campaign_id is None:
                campaign = cls.get_active_campaign(session)
                if not campaign:
                    print(f"⚠️  No hay campaña activa")
                    return False
                campaign_id = campaign.id
                is_promo = campaign.is_promo_active
                target_points = campaign.target_points
            else:
                campaign = session.get(TravelCampaigns, campaign_id)
                is_promo = campaign.is_promo_active if campaign else False
                target_points = campaign.target_points if campaign else 200

            # Obtener o crear registro de puntos
            sponsor_points = cls.get_or_create_user_points(session, sponsor_id, campaign_id)
            if not sponsor_points:
                return False

            # Obtener puntos del rango (para directos)
            # Nota: Los puntos por directos pueden tener valores diferentes
            # Por ahora usamos la misma tabla, pero podrías tener una configuración separada
            rank_config = cls.RANK_POINTS.get(rank_name)
            if not rank_config:
                print(f"⚠️  Rango desconocido: {rank_name}")
                return False

            points_to_add = rank_config["promo"] if is_promo else rank_config["base"]

            # Actualizar puntos
            sponsor_points.points_from_direct_ranks += points_to_add
            sponsor_points.recalculate_total()
            sponsor_points.update_qualification(target_points)

            # Crear historial
            history = NNTravelPointsHistory(
                member_id=sponsor_id,
                campaign_id=campaign_id,
                event_type=TravelEventType.DIRECT_RANK.value,
                points_earned=points_to_add,
                source_member_id=direct_member_id,
                rank_achieved=rank_name,
                description=f"Puntos por rango {rank_name} alcanzado por directo {direct_member_id}"
            )

            session.add(history)
            session.flush()

            print(f"✅ Sponsor {sponsor_id} ganó {points_to_add} puntos por rango {rank_name} de directo {direct_member_id}")
            return True

        except Exception as e:
            print(f"❌ Error añadiendo puntos de directo para sponsor {sponsor_id}: {e}")
            import traceback
            traceback.print_exc()
            return False

    @classmethod
    def get_user_points_summary(cls, session, member_id: int, campaign_id: Optional[int] = None) -> Optional[Dict]:
        """
        Obtiene el resumen de puntos de un usuario para una campaña.

        Args:
            session: Sesión de base de datos
            member_id: ID del usuario
            campaign_id: ID de campaña (si no se provee, usa la activa)

        Returns:
            Diccionario con resumen de puntos o None
        """
        try:
            # Obtener campaña activa si no se especificó
            if campaign_id is None:
                campaign = cls.get_active_campaign(session)
                if not campaign:
                    return None
                campaign_id = campaign.id
                target_points = campaign.target_points
            else:
                campaign = session.get(TravelCampaigns, campaign_id)
                target_points = campaign.target_points if campaign else 200

            # Obtener puntos del usuario
            user_points = session.exec(
                sqlmodel.select(NNTravelPoints)
                .where(
                    (NNTravelPoints.member_id == member_id) &
                    (NNTravelPoints.campaign_id == campaign_id)
                )
            ).first()

            if not user_points:
                return {
                    "member_id": member_id,
                    "campaign_id": campaign_id,
                    "points_from_kits": 0,
                    "points_from_self_ranks": 0,
                    "points_from_direct_ranks": 0,
                    "points_bonus": 0,
                    "total_points": 0,
                    "target_points": target_points,
                    "qualifies_for_travel": False
                }

            return {
                "member_id": user_points.member_id,
                "campaign_id": user_points.campaign_id,
                "points_from_kits": user_points.points_from_kits,
                "points_from_self_ranks": user_points.points_from_self_ranks,
                "points_from_direct_ranks": user_points.points_from_direct_ranks,
                "points_bonus": user_points.points_bonus,
                "total_points": user_points.total_points,
                "target_points": target_points,
                "qualifies_for_travel": user_points.qualifies_for_travel
            }

        except Exception as e:
            print(f"❌ Error obteniendo resumen de puntos de usuario {member_id}: {e}")
            return None

    @classmethod
    def close_campaign(cls, session, campaign_id: int) -> bool:
        """
        Cierra una campaña de NN Travel.

        Args:
            session: Sesión de base de datos
            campaign_id: ID de la campaña

        Returns:
            True si se cerró exitosamente, False si falló
        """
        try:
            campaign = session.get(TravelCampaigns, campaign_id)
            if not campaign:
                print(f"❌ Campaña {campaign_id} no existe")
                return False

            campaign.status = CampaignStatus.CLOSED.value
            session.flush()

            print(f"✅ Campaña {campaign.name} cerrada exitosamente")
            return True

        except Exception as e:
            print(f"❌ Error cerrando campaña {campaign_id}: {e}")
            import traceback
            traceback.print_exc()
            return False
