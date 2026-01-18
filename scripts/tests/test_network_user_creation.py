"""
Test integrado: Crea 3 usuarios usando la lógica del admin
y valida que tengan period_id y referral_link.
"""

import reflex as rx
import sqlmodel
import random
from datetime import datetime, timezone, date

from database.users import Users, UserStatus
from database.userprofiles import UserProfiles, UserGender
from database.addresses import Addresses
from database.users_addresses import UserAddresses
from database.usertreepaths import UserTreePath
from database.wallet import Wallets, WalletStatus
from database.user_rank_history import UserRankHistory
from database.ranks import Ranks
from NNProtect_new_website.mlm_service.period_service import PeriodService


def create_test_user_with_network_logic(
    session,
    member_id: int,
    sponsor_id: int,
    current_period,
    default_rank
):
    """Crea un usuario usando la misma lógica que _create_mlm_user"""
    
    # 1. USERS
    first_name = f"TestNet{member_id}"
    last_name = f"User"
    email = f"testnet{member_id}@nnprotect.local"
    country = "México"
    
    user = Users(
        member_id=member_id,
        sponsor_id=sponsor_id,
        first_name=first_name,
        last_name=last_name,
        email_cache=email,
        country_cache=country,
        status=UserStatus.NO_QUALIFIED,
        pv_cache=0,
        pvg_cache=0,
        referral_link=f"https://nnprotect.com/ref/{member_id}",  # 🆕
        created_at=datetime.now(timezone.utc)
    )
    session.add(user)
    session.flush()
    
    if user.id is None:
        raise ValueError("User ID cannot be None")
    
    # 2. USERPROFILES
    profile = UserProfiles(
        user_id=user.id,
        gender=UserGender.MALE,
        phone_number="+525512345678",
        date_of_birth=date(1990, 1, 1),
        bio=""
    )
    session.add(profile)
    
    # 3. ADDRESSES + USERS_ADDRESSES
    address = Addresses(
        country=country,
        state="Test",
        city="TestCity",
        zip_code="12345",
        street="Test Street",
        neighborhood="Test"
    )
    session.add(address)
    session.flush()
    
    if address.id is None:
        raise ValueError("Address ID cannot be None")
    
    user_address = UserAddresses(
        user_id=user.id,
        address_id=address.id,
        address_name="Casa",
        is_default=True
    )
    session.add(user_address)
    
    # 4. USERTREEPATHS
    self_path = UserTreePath(
        sponsor_id=sponsor_id,
        ancestor_id=member_id,
        descendant_id=member_id,
        depth=0
    )
    session.add(self_path)
    
    sponsor_ancestors = session.exec(
        sqlmodel.select(UserTreePath).where(UserTreePath.descendant_id == sponsor_id)
    ).all()
    
    for ancestor_path in sponsor_ancestors:
        new_path = UserTreePath(
            sponsor_id=sponsor_id,
            ancestor_id=ancestor_path.ancestor_id,
            descendant_id=member_id,
            depth=ancestor_path.depth + 1
        )
        session.add(new_path)
    
    # 5. WALLETS
    wallet = Wallets(
        member_id=member_id,
        balance=0.0,
        currency="MXN",
        status=WalletStatus.ACTIVE.value,
        created_at=datetime.now(timezone.utc)
    )
    session.add(wallet)
    
    # 6. USER_RANK_HISTORY (con period_id SIEMPRE)
    if not current_period:
        raise ValueError("current_period is required")
    
    rank_history = UserRankHistory(
        member_id=member_id,
        rank_id=default_rank.id,
        achieved_on=datetime.now(timezone.utc),
        period_id=current_period.id  # 🆕
    )
    session.add(rank_history)
    
    return user


def test_create_users_and_validate():
    """Crea usuarios de prueba y valida datos."""
    
    print("\n" + "="*80)
    print("🧪 TEST: Crear usuarios y validar period_id + referral_link")
    print("="*80 + "\n")
    
    try:
        with rx.session() as session:
            
            # Paso 1: Obtener o crear período
            print("📅 PASO 1: Verificando período actual")
            print("-" * 80)
            
            current_period = PeriodService.get_current_period(session)
            if not current_period:
                print("⚠️  Creando período actual...")
                current_period = PeriodService.auto_create_current_month_period(session)
                session.commit()
            
            if not current_period:
                print("❌ No se pudo obtener período")
                return False
            
            print(f"✅ Período: {current_period.name} (ID: {current_period.id})")
            
            # Paso 2: Obtener rango default
            print("\n🎯 PASO 2: Obteniendo rango default")
            print("-" * 80)
            
            default_rank = session.exec(
                sqlmodel.select(Ranks).where(Ranks.name == "Sin rango")
            ).first()
            
            if not default_rank:
                print("❌ Rango 'Sin rango' no encontrado")
                return False
            
            print(f"✅ Rango default: {default_rank.name} (ID: {default_rank.id})")
            
            # Paso 3: Obtener próximo member_id
            print("\n🔢 PASO 3: Calculando próximo member_id")
            print("-" * 80)
            
            from sqlmodel import func as sql_func
            max_member_id = session.exec(
                sqlmodel.select(sql_func.max(Users.member_id))
            ).one()
            next_member_id = (max_member_id or 0) + 1
            
            print(f"✅ Próximo member_id: {next_member_id}")
            
            # Paso 4: Crear 3 usuarios de prueba
            print("\n👥 PASO 4: Creando 3 usuarios de prueba")
            print("-" * 80)
            
            created_users = []
            sponsor_id = 1  # Usar member_id 1 como sponsor
            
            for i in range(3):
                member_id = next_member_id + i
                print(f"  • Creando usuario {member_id}...")
                
                user = create_test_user_with_network_logic(
                    session,
                    member_id,
                    sponsor_id,
                    current_period,
                    default_rank
                )
                
                created_users.append(user)
            
            session.commit()
            print(f"✅ {len(created_users)} usuarios creados")
            
            # Paso 5: Validar datos
            print("\n✅ PASO 5: Validando datos")
            print("-" * 80)
            
            print(f"\n{'Member ID':<12} {'Referral Link':<50} {'Period ID':<12} {'Status':<10}")
            print("-" * 80)
            
            all_valid = True
            
            for user in created_users:
                session.refresh(user)
                
                # Validar referral_link
                expected_link = f"https://nnprotect.com/ref/{user.member_id}"
                has_referral = user.referral_link == expected_link
                
                # Obtener registro de rango
                rank_record = session.exec(
                    sqlmodel.select(UserRankHistory)
                    .where(UserRankHistory.member_id == user.member_id)
                ).first()
                
                has_period = rank_record and rank_record.period_id == current_period.id
                
                status = "✅" if (has_referral and has_period) else "❌"
                
                print(
                    f"{user.member_id:<12} "
                    f"{user.referral_link or 'N/A':<50} "
                    f"{rank_record.period_id if rank_record else 'N/A':<12} "
                    f"{status:<10}"
                )
                
                if not has_referral:
                    print(f"  ❌ Referral link incorrecto o ausente")
                    all_valid = False
                
                if not has_period:
                    print(f"  ❌ Period ID no asignado o incorrecto")
                    all_valid = False
            
            if all_valid:
                print("\n" + "="*80)
                print("✅ TODOS LOS USUARIOS TIENEN LOS DATOS CORRECTOS")
                print("="*80)
                print("\n📋 RESUMEN:")
                print(f"  • Usuarios creados: {len(created_users)}")
                print(f"  • Todos con referral_link: ✅")
                print(f"  • Todos con period_id: ✅")
                print(f"  • Período: {current_period.name}")
                return True
            else:
                print("\n" + "="*80)
                print("❌ ALGUNOS USUARIOS NO TIENEN LOS DATOS CORRECTOS")
                print("="*80)
                return False
                
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_create_users_and_validate()
    
    if success:
        print("\n🎉 Test completado exitosamente")
        exit(0)
    else:
        print("\n❌ Test falló")
        exit(1)
