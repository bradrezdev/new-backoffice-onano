"""
Script para verificar comisiones de Uninivel y Matching del período actual
"""

def check_uninivel_matching():
    import reflex as rx
    import sqlmodel
    from database.users import Users
    from database.comissions import Commissions, BonusType
    from database.periods import Periods
    from NNProtect_new_website.utils.timezone_mx import get_mexico_now
    
    print("="*70)
    print("VERIFICACIÓN: Comisiones Uninivel y Matching")
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
        
        print(f"\n📅 Período Actual: {current_period.name} (ID={current_period.id})")
        print(f"   Desde: {current_period.starts_on}")
        print(f"   Hasta: {current_period.ends_on}")
        
        # 2. Obtener usuario member_id=1
        user = session.exec(
            sqlmodel.select(Users).where(Users.member_id == 1)
        ).first()
        
        if not user:
            print("❌ Usuario no encontrado")
            return
        
        print(f"\n👤 Usuario: {user.first_name} {user.last_name} (member_id={user.member_id})")
        
        # 3. Comisiones por tipo en el período actual
        for bonus_type in [BonusType.BONO_UNINIVEL, BonusType.BONO_MATCHING, BonusType.BONO_ALCANCE]:
            
            # Total
            total = session.exec(
                sqlmodel.select(sqlmodel.func.sum(Commissions.amount_converted))
                .where(
                    (Commissions.member_id == user.member_id) &
                    (Commissions.period_id == current_period.id) &
                    (Commissions.bonus_type == bonus_type.value)
                )
            ).first() or 0.0
            
            # Cantidad de comisiones
            count = session.exec(
                sqlmodel.select(sqlmodel.func.count(Commissions.id))  # type: ignore
                .where(
                    (Commissions.member_id == user.member_id) &
                    (Commissions.period_id == current_period.id) &
                    (Commissions.bonus_type == bonus_type.value)
                )
            ).first() or 0
            
            print(f"\n💰 {bonus_type.value}:")
            print(f"   Total: ${total:,.2f}")
            print(f"   Cantidad: {count} comisiones")
            
            if count > 0 and count <= 10:
                # Mostrar detalle si hay pocas comisiones
                commissions = session.exec(
                    sqlmodel.select(Commissions)
                    .where(
                        (Commissions.member_id == user.member_id) &
                        (Commissions.period_id == current_period.id) &
                        (Commissions.bonus_type == bonus_type.value)
                    )
                    .limit(10)
                ).all()
                
                for comm in commissions:
                    print(f"     - ${comm.amount_converted:,.2f} {comm.currency_destination}")
                    if comm.notes:
                        print(f"       {comm.notes[:80]}")
        
        # 4. Total del período
        grand_total = session.exec(
            sqlmodel.select(sqlmodel.func.sum(Commissions.amount_converted))
            .where(
                (Commissions.member_id == user.member_id) &
                (Commissions.period_id == current_period.id)
            )
        ).first() or 0.0
        
        print(f"\n📊 TOTAL PERÍODO: ${grand_total:,.2f}")
        
        # 5. Verificar si hay órdenes en el período
        from database.orders import Orders, OrderStatus
        from database.usertreepaths import UserTreePath
        
        # Órdenes del downline
        downline_orders = session.exec(
            sqlmodel.select(sqlmodel.func.count(Orders.id))  # type: ignore
            .select_from(Orders)
            .join(UserTreePath, UserTreePath.descendant_member_id == Orders.customer_member_id)
            .where(
                (UserTreePath.ancestor_member_id == user.member_id) &
                (UserTreePath.depth > 0) &
                (Orders.status == OrderStatus.COMPLETED.value) &
                (Orders.created_at >= current_period.starts_on) &
                (Orders.created_at <= current_period.ends_on)
            )
        ).first() or 0
        
        print(f"\n🛒 Órdenes del downline en período: {downline_orders}")
        
        if downline_orders > 0:
            print(f"   ⚠️  HAY ÓRDENES pero puede que no se hayan procesado comisiones Uninivel")
            print(f"   💡 Ejecutar: CommissionService.process_uninivel_commissions()")

if __name__ == "__main__":
    check_uninivel_matching()
