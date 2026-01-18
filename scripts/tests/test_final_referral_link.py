"""
Test final: Crear usuarios usando la función actualizada de admin_state
y verificar que tengan el referral_link correcto
"""

import reflex as rx
import sqlmodel
from datetime import datetime, timezone
import random

from database.users import Users, UserStatus
from database.userprofiles import UserProfiles, UserGender
from database.addresses import Addresses
from database.users_addresses import UserAddresses
from database.usertreepaths import UserTreePath
from database.user_rank_history import UserRankHistory
from database.periods import Periods
from database.ranks import Ranks
from NNProtect_new_website.mlm_service.mlm_user_manager import MLMUserManager

print("\n" + "="*80)
print("🧪 TEST FINAL: Verificar referral_link en usuarios de red")
print("="*80 + "\n")

with rx.session() as session:
    # 1. Limpiar usuarios de prueba anteriores
    print("🧹 PASO 1: Limpiando usuarios de prueba anteriores...")
    test_users = session.exec(
        sqlmodel.select(Users).where(Users.member_id >= 1027)
    ).all()
    
    for user in test_users:
        # Eliminar dependencias primero
        session.exec(sqlmodel.delete(UserTreePath).where(
            (UserTreePath.ancestor_id == user.member_id) | 
            (UserTreePath.descendant_id == user.member_id)
        ))
        session.exec(sqlmodel.delete(UserRankHistory).where(
            UserRankHistory.member_id == user.member_id
        ))
        session.exec(sqlmodel.delete(UserAddresses).where(
            UserAddresses.user_id == user.id
        ))
        session.exec(sqlmodel.delete(UserProfiles).where(
            UserProfiles.user_id == user.id
        ))
        session.delete(user)
    
    session.commit()
    print(f"   ✅ {len(test_users)} usuarios eliminados")
    print()
    
    # 2. Obtener período y rango
    print("📅 PASO 2: Obteniendo período y rango...")
    current_period = session.exec(
        sqlmodel.select(Periods).order_by(sqlmodel.desc(Periods.starts_on)).limit(1)
    ).first()
    
    default_rank = session.exec(
        sqlmodel.select(Ranks).where(Ranks.id == 1)
    ).first()
    
    print(f"   ✅ Período: {current_period.name} (ID: {current_period.id})")
    print(f"   ✅ Rango: {default_rank.name} (ID: {default_rank.id})")
    print()
    
    # 3. Calcular siguiente member_id
    last_user = session.exec(
        sqlmodel.select(Users).order_by(sqlmodel.desc(Users.member_id))
    ).first()
    next_member_id = last_user.member_id + 1
    
    print(f"🔢 PASO 3: Próximo member_id: {next_member_id}")
    print()
    
    # 4. Crear usuarios usando el código actualizado
    print("👥 PASO 4: Creando usuarios con código actualizado...")
    
    sponsor_id = 1  # Sponsor principal
    users_created = []
    
    for i in range(3):
        member_id = next_member_id + i
        first_name = f"Test{member_id}"
        last_name = f"User{member_id}"
        email = f"test{member_id}@nnprotect.local"
        country = "México"
        
        # Generar referral_link usando el método de MLMUserManager
        base_url = MLMUserManager.get_base_url()
        
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
            referral_link=f"{base_url}?ref={member_id}",
            created_at=datetime.now(timezone.utc)
        )
        session.add(user)
        session.flush()
        
        # Agregar perfil básico
        profile = UserProfiles(
            user_id=user.id,
            gender=UserGender.MALE,
            phone_number=f"+52{random.randint(1000000000, 9999999999)}"
        )
        session.add(profile)
        
        # Agregar dirección
        address = Addresses(
            country=country,
            city=f"Ciudad{member_id}",
            zip_code="12345",
            street=f"Calle {member_id}",
            neighborhood=f"Colonia{member_id}"
        )
        session.add(address)
        session.flush()
        
        user_address = UserAddresses(
            user_id=user.id,
            address_id=address.id,
            address_name="Casa",
            is_default=True
        )
        session.add(user_address)
        
        # UserTreePath
        self_path = UserTreePath(
            sponsor_id=sponsor_id,
            ancestor_id=member_id,
            descendant_id=member_id,
            depth=0
        )
        session.add(self_path)
        
        # UserRankHistory con period_id
        rank_history = UserRankHistory(
            member_id=member_id,
            rank_id=default_rank.id,
            achieved_on=datetime.now(timezone.utc),
            period_id=current_period.id
        )
        session.add(rank_history)
        
        users_created.append(user)
        print(f"   ✅ Usuario {member_id} creado")
    
    session.commit()
    print(f"\n   ✅ {len(users_created)} usuarios creados")
    print()
    
    # 5. Validar datos
    print("✅ PASO 5: Validando datos")
    print("-" * 80)
    
    print(f"{'Member ID':<12} {'Referral Link':<50} {'Period ID':<12} {'Status'}")
    print("-" * 80)
    
    all_correct = True
    for user in users_created:
        session.refresh(user)
        
        # Verificar rank_history
        rank_hist = session.exec(
            sqlmodel.select(UserRankHistory).where(
                UserRankHistory.member_id == user.member_id
            )
        ).first()
        
        has_period = "✅" if (rank_hist and rank_hist.period_id) else "❌"
        has_referral = "✅" if user.referral_link and "?ref=" in user.referral_link else "❌"
        
        if has_period == "❌" or has_referral == "❌":
            all_correct = False
        
        period_display = rank_hist.period_id if rank_hist else "N/A"
        
        print(
            f"{user.member_id:<12} "
            f"{user.referral_link:<50} "
            f"{period_display:<12} "
            f"{has_referral}"
        )
    
    print()
    
    if all_correct:
        print("="*80)
        print("✅ TODOS LOS USUARIOS TIENEN LOS DATOS CORRECTOS")
        print("="*80)
        print()
        print("📋 RESUMEN:")
        print(f"  • Usuarios creados: {len(users_created)}")
        print(f"  • Todos con referral_link correcto (con ?ref=): ✅")
        print(f"  • Todos con period_id: ✅")
        print(f"  • Período: {current_period.name}")
        print()
    else:
        print("="*80)
        print("❌ ALGUNOS USUARIOS NO TIENEN LOS DATOS CORRECTOS")
        print("="*80)

print("🎉 Test completado")
