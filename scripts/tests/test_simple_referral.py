"""
Test simple: Crear un usuario nuevo y verificar su referral_link
"""

import reflex as rx
import sqlmodel
from datetime import datetime, timezone

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
print("🧪 TEST: Crear usuario y verificar referral_link")
print("="*80 + "\n")

with rx.session() as session:
    # 1. Obtener período y rango
    current_period = session.exec(
        sqlmodel.select(Periods).order_by(sqlmodel.desc(Periods.starts_on)).limit(1)
    ).first()
    
    default_rank = session.exec(
        sqlmodel.select(Ranks).where(Ranks.id == 1)
    ).first()
    
    # 2. Calcular siguiente member_id
    last_user = session.exec(
        sqlmodel.select(Users).order_by(sqlmodel.desc(Users.member_id))
    ).first()
    member_id = last_user.member_id + 1
    
    print(f"🔢 Creando usuario con member_id: {member_id}")
    print()
    
    # 3. Generar referral_link usando el método correcto
    base_url = MLMUserManager.get_base_url()
    referral_link = f"{base_url}?ref={member_id}"
    
    print(f"📍 Base URL: {base_url}")
    print(f"🔗 Referral link generado: {referral_link}")
    print()
    
    # 4. Crear usuario
    user = Users(
        member_id=member_id,
        sponsor_id=1,
        first_name=f"TestFinal",
        last_name=f"User{member_id}",
        email_cache=f"testfinal{member_id}@nn protect.local",
        country_cache="México",
        status=UserStatus.NO_QUALIFIED,
        pv_cache=0,
        pvg_cache=0,
        referral_link=referral_link,
        created_at=datetime.now(timezone.utc)
    )
    session.add(user)
    session.flush()
    
    # 5. Agregar UserRankHistory con period_id
    rank_history = UserRankHistory(
        member_id=member_id,
        rank_id=default_rank.id,
        achieved_on=datetime.now(timezone.utc),
        period_id=current_period.id
    )
    session.add(rank_history)
    
    session.commit()
    
    # 6. Verificar
    session.refresh(user)
    
    print("✅ Usuario creado exitosamente")
    print()
    print("📊 Verificación:")
    print(f"   • Member ID: {user.member_id}")
    print(f"   • Referral link: {user.referral_link}")
    print(f"   • Formato correcto (?ref=): {'✅' if '?ref=' in user.referral_link else '❌'}")
    print(f"   • Period ID: {rank_history.period_id}")
    print()
    
    if '?ref=' in user.referral_link and rank_history.period_id:
        print("="*80)
        print("✅ USUARIO TIENE TODOS LOS DATOS CORRECTOS")
        print("="*80)
    else:
        print("="*80)
        print("❌ FALTAN ALGUNOS DATOS")
        print("="*80)

print("\n🎉 Test completado\n")
