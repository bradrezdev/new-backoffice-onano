"""
Test Simple: Verificar comisiones del período actual para proyección de ganancias

Este test verifica directamente en la BD sin importar modelos de Reflex
"""

import psycopg2
from datetime import datetime

# Configuración de conexión a Supabase
DATABASE_URL = "postgresql://postgres.wxjknxpyqgxxjtrkuyev:nn_backoffice!@aws-1-us-east-2.pooler.supabase.com:6543/postgres"

def test_commission_projection():
    """Test de proyección de comisiones mensuales"""
    print("=" * 70)
    print("🧪 TEST: Proyección de Ganancias Mensuales (SQL Directo)")
    print("=" * 70)
    
    member_id = 1  # Usuario de prueba
    
    try:
        # Conectar a la base de datos
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # 1. Obtener información del usuario
        cursor.execute("""
            SELECT first_name, last_name, country_cache 
            FROM users 
            WHERE member_id = %s
        """, (member_id,))
        
        user_data = cursor.fetchone()
        if not user_data:
            print(f"❌ Usuario {member_id} no encontrado")
            return False
        
        first_name, last_name, country = user_data
        full_name = f"{first_name} {last_name}"
        print(f"\n👤 Usuario: {full_name} (Member ID: {member_id})")
        print(f"🌎 País: {country}")
        
        # Determinar moneda según país
        currency_map = {
            "Mexico": "MXN",
            "United States": "USD",
            "Colombia": "COP",
            "República Dominicana": "USD"
        }
        user_currency = currency_map.get(country, "MXN")
        print(f"💵 Moneda: {user_currency}")
        
        # 2. Obtener período actual
        now = datetime.utcnow()
        cursor.execute("""
            SELECT id, name 
            FROM periods 
            WHERE EXTRACT(YEAR FROM starts_on) = %s 
            AND EXTRACT(MONTH FROM starts_on) = %s
        """, (now.year, now.month))
        
        period_data = cursor.fetchone()
        if not period_data:
            print(f"\n⚠️  No hay período activo para {now.year}-{now.month}")
            print("✅ Proyección debe mostrar: $0.00")
            return True
        
        period_id, period_name = period_data
        print(f"\n📅 Período actual: {period_name} (ID: {period_id})")
        
        # 3. Obtener comisiones por tipo
        print("\n📊 Comisiones del período actual:")
        
        # Uninivel
        cursor.execute("""
            SELECT COALESCE(SUM(amount_converted), 0) 
            FROM commissions 
            WHERE member_id = %s 
            AND period_id = %s 
            AND bonus_type = 'BONO_UNINIVEL'
        """, (member_id, period_id))
        
        uninivel_total = cursor.fetchone()[0] or 0.0
        print(f"   • Bono Uninivel:  ${uninivel_total:,.2f} {user_currency}")
        
        # Matching
        cursor.execute("""
            SELECT COALESCE(SUM(amount_converted), 0) 
            FROM commissions 
            WHERE member_id = %s 
            AND period_id = %s 
            AND bonus_type = 'BONO_MATCHING'
        """, (member_id, period_id))
        
        matching_total = cursor.fetchone()[0] or 0.0
        print(f"   • Bono Matching:  ${matching_total:,.2f} {user_currency}")
        
        # Alcance
        cursor.execute("""
            SELECT COALESCE(SUM(amount_converted), 0) 
            FROM commissions 
            WHERE member_id = %s 
            AND period_id = %s 
            AND bonus_type = 'BONO_ALCANCE'
        """, (member_id, period_id))
        
        achievement_total = cursor.fetchone()[0] or 0.0
        print(f"   • Bono Alcance:   ${achievement_total:,.2f} {user_currency}")
        
        # 4. Calcular total
        total_earnings = float(uninivel_total) + float(matching_total) + float(achievement_total)
        
        print(f"\n" + "─" * 70)
        print(f"💰 TOTAL PROYECTADO: ${total_earnings:,.2f} {user_currency}")
        print("─" * 70)
        
        # 5. Validación
        print("\n✅ RESULTADO:")
        print(f"   • El dashboard debe mostrar: ${total_earnings:,.2f} {user_currency}")
        print(f"   • Sección: 'Estimado ganancia mes'")
        
        if total_earnings > 0:
            print(f"\n🎉 Usuario tiene comisiones generadas en este período")
            print(f"\n📝 Desglose:")
            print(f"   - Uninivel:  {(uninivel_total/total_earnings*100):.1f}%")
            print(f"   - Matching:  {(matching_total/total_earnings*100):.1f}%")
            print(f"   - Alcance:   {(achievement_total/total_earnings*100):.1f}%")
        else:
            print(f"\n⚠️  Usuario no tiene comisiones en este período")
            print(f"   (mostrará $0.00 {user_currency})")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 70)
        print("✅ TEST COMPLETADO EXITOSAMENTE")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR en el test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import sys
    success = test_commission_projection()
    print("\n")
    sys.exit(0 if success else 1)
