"""
Script para calcular comisiones Uninivel del período actual.
Las comisiones Uninivel normalmente se calculan al cierre del mes,
pero este script permite calcularlas antes para ver la proyección.
"""

def calculate_uninivel_now():
    import reflex as rx
    import sqlmodel
    from database.periods import Periods
    from database.users import Users
    from NNProtect_new_website.utils.timezone_mx import get_mexico_now
    from NNProtect_new_website.modules.network.backend.commission_service import CommissionService
    
    print("="*70)
    print("CÁLCULO: Comisiones Uninivel del Período Actual")
    print("="*70)
    
    with rx.session() as session:
        # 1. Obtener período actual
        now = get_mexico_now()
        current_period = session.exec(
            sqlmodel.select(Periods)
            .where(
                (Periods.starts_on <= now) &
                (Periods.ends_on >= now)
            )
        ).first()
        
        if not current_period:
            print("❌ No hay período activo")
            return
        
        if current_period.id is None:
            print("❌ Período sin ID")
            return
        
        print(f"\n📅 Período: {current_period.name} (ID={current_period.id})")
        
        # 2. Obtener todos los usuarios
        users = session.exec(
            sqlmodel.select(Users)
        ).all()
        
        print(f"\n👥 Usuarios totales: {len(users)}")
        
        if len(users) == 0:
            print("⚠️  No hay usuarios")
            return
        
        # 3. Calcular comisiones Uninivel para cada usuario
        print(f"\n💰 Calculando comisiones Uninivel...")
        
        processed = 0
        errors = 0
        total_commissions = 0
        
        for user in users:
            try:
                # Usar CommissionService.calculate_unilevel_bonus
                # Este método calcula Uninivel basado en el VN de la red
                commission_ids = CommissionService.calculate_unilevel_bonus(
                    session=session,
                    member_id=user.member_id,
                    period_id=current_period.id
                )
                
                if commission_ids and len(commission_ids) > 0:
                    processed += 1
                    total_commissions += len(commission_ids)
                    user_name = f"{user.first_name} {user.last_name}" if user.first_name else user.email_cache
                    print(f"   ✅ {user_name}: {len(commission_ids)} comisiones")
                
            except Exception as e:
                errors += 1
                user_name = f"{user.first_name} {user.last_name}" if user.first_name else user.email_cache
                print(f"   ❌ {user_name}: {str(e)}")
        
        # 4. Commit cambios
        session.commit()
        
        print(f"\n📊 RESUMEN:")
        print(f"   Usuarios con comisiones: {processed}/{len(users)}")
        print(f"   Total comisiones creadas: {total_commissions}")
        print(f"   Errores: {errors}")
        
        # 5. Verificar comisiones creadas
        from database.comissions import Commissions, BonusType
        
        total_uninivel = session.exec(
            sqlmodel.select(sqlmodel.func.sum(Commissions.amount_converted))
            .where(
                (Commissions.period_id == current_period.id) &
                (Commissions.bonus_type == BonusType.BONO_UNINIVEL.value)
            )
        ).first() or 0.0
        
        count = session.exec(
            sqlmodel.select(sqlmodel.func.count(Commissions.id))  # type: ignore
            .where(
                (Commissions.period_id == current_period.id) &
                (Commissions.bonus_type == BonusType.BONO_UNINIVEL.value)
            )
        ).first() or 0
        
        print(f"\n💰 Comisiones Uninivel totales:")
        print(f"   Total: ${total_uninivel:,.2f}")
        print(f"   Cantidad: {count} comisiones")
        
        # 6. Mostrar detalle del usuario principal (member_id=1)
        user_uninivel = session.exec(
            sqlmodel.select(sqlmodel.func.sum(Commissions.amount_converted))
            .where(
                (Commissions.member_id == 1) &
                (Commissions.period_id == current_period.id) &
                (Commissions.bonus_type == BonusType.BONO_UNINIVEL.value)
            )
        ).first() or 0.0
        
        print(f"\n🎯 Tu comisión Uninivel (member_id=1): ${user_uninivel:,.2f}")

if __name__ == "__main__":
    calculate_uninivel_now()
