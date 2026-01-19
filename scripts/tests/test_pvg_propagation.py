"""
Script para verificar la propagación de PVG en órdenes creadas desde Admin Panel
"""

import sqlmodel
from database import engine
from database.users import Users
from database.orders import Orders

def test_pvg_propagation():
    """Verifica que el PVG se propague correctamente"""
    
    with sqlmodel.Session(engine) as session:
        print("="*80)
        print("📊 VERIFICACIÓN DE PROPAGACIÓN DE PVG")
        print("="*80)
        
        # Obtener usuarios con órdenes
        users_with_orders = session.exec(
            sqlmodel.select(Users)
            .join(Orders, Users.member_id == Orders.member_id)
            .distinct()
        ).all()
        
        print(f"\n✅ Usuarios con órdenes: {len(users_with_orders)}")
        
        # Mostrar resumen de primeros 10 usuarios
        print("\n📋 RESUMEN DE USUARIOS (primeros 10):")
        print(f"{'Member ID':<12} {'PV':<10} {'PVG':<10} {'VN':<12} {'Status':<15}")
        print("-" * 60)
        
        for user in users_with_orders[:10]:
            print(f"{user.member_id:<12} {user.pv_cache:<10} {user.pvg_cache:<10} {user.vn_cache:<12.2f} {user.status.value:<15}")
        
        # Verificar que PVG > PV para usuarios con red
        print("\n🔍 VERIFICACIÓN DE LÓGICA PVG:")
        users_with_network = []
        
        for user in users_with_orders:
            if user.pvg_cache > user.pv_cache:
                users_with_network.append(user)
        
        print(f"✅ Usuarios con PVG > PV (tienen red): {len(users_with_network)}")
        
        if users_with_network:
            print("\n📈 EJEMPLOS DE USUARIOS CON RED:")
            for user in users_with_network[:5]:
                print(f"   User {user.member_id}: PV={user.pv_cache}, PVG={user.pvg_cache} (Diferencia: {user.pvg_cache - user.pv_cache})")
        
        # Contar usuarios sin red
        users_without_network = len([u for u in users_with_orders if u.pvg_cache == u.pv_cache])
        print(f"\n👤 Usuarios sin red (PVG = PV): {users_without_network}")
        
        print("\n" + "="*80)

if __name__ == "__main__":
    test_pvg_propagation()
