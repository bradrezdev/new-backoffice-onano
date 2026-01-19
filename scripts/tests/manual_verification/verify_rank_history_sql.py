"""
Script para verificar el historial de rangos del usuario member_id=1 usando SQL directo
"""
import psycopg2
from datetime import datetime

# Conexión a Supabase
conn = psycopg2.connect(
    host="aws-0-us-west-1.pooler.supabase.com",
    database="postgres",
    user="postgres.hdqxuagfshuhaeefvkuh",
    password="Frida+2019",
    port=6543
)

cur = conn.cursor()

print("="*70)
print("VERIFICACIÓN: Historial de Rangos en user_rank_history")
print("="*70)

# 1. Obtener usuario
cur.execute("""
    SELECT member_id, first_name, last_name, pv_cache, pvg_cache, country_cache
    FROM users 
    WHERE member_id = 1
""")
user = cur.fetchone()

if not user:
    print("❌ Usuario no encontrado")
    exit()

member_id, first_name, last_name, pv, pvg, country = user
print(f"\n👤 Usuario: {first_name} {last_name} (member_id={member_id})")
print(f"   PV: {pv}, PVG: {pvg}, País: {country}")

# 2. Obtener historial de rangos
cur.execute("""
    SELECT urh.id, urh.rank_id, r.name, urh.achieved_on, urh.period_id
    FROM user_rank_history urh
    JOIN ranks r ON r.id = urh.rank_id
    WHERE urh.member_id = %s
    ORDER BY urh.achieved_on ASC
""", (member_id,))
rank_history = cur.fetchall()

print(f"\n🏆 Historial de Rangos en user_rank_history ({len(rank_history)} registros):")

for i, (id, rank_id, rank_name, achieved_on, period_id) in enumerate(rank_history, 1):
    print(f"   {i}. Rango: {rank_name} (ID={rank_id})")
    print(f"      Fecha: {achieved_on}")
    print(f"      Period ID: {period_id}")

# 3. Obtener bonos de alcance PAGADOS
cur.execute("""
    SELECT id, amount_converted, currency_destination, notes, calculated_at
    FROM commissions
    WHERE member_id = %s 
    AND bonus_type = 'BONO_ALCANCE'
    ORDER BY calculated_at ASC
""", (member_id,))
bonos_pagados = cur.fetchall()

print(f"\n💰 Bonos de Alcance PAGADOS ({len(bonos_pagados)}):")
total_pagado = 0
for id, amount, currency, notes, calc_at in bonos_pagados:
    print(f"   - ${amount:,.2f} {currency}")
    print(f"     {notes}")
    print(f"     Calculado: {calc_at}")
    total_pagado += float(amount)

print(f"\n   TOTAL PAGADO: ${total_pagado:,.2f}")

# 4. Identificar rangos SIN PAGAR
print(f"\n🔍 Análisis de Rangos vs Bonos:")

rangos_en_historial = set(r[2] for r in rank_history)  # rank_name
print(f"   Rangos alcanzados: {', '.join(sorted(rangos_en_historial))}")

# Montos esperados por rango
RANK_ADVANCEMENT_AMOUNTS = {
    "Emprendedor": {"MXN": 1500, "USD": 85, "COP": 330000},
    "Creativo": {"MXN": 3000, "USD": 165, "COP": 660000},
    "Innovador": {"MXN": 5000, "USD": 280, "COP": 1100000},
    "Embajador Transformador": {"MXN": 7500, "USD": 390, "COP": 1650000},
    "Embajador Inspirador": {"MXN": 10000, "USD": 555, "COP": 2220000},
    "Embajador Consciente": {"MXN": 20000, "USD": 1111, "COP": 4400000},
    "Embajador Solidario": {"MXN": 40000, "USD": 2222, "COP": 8800000}
}

# Determinar moneda del usuario
user_currency = "MXN"  # Por defecto
if country == "US":
    user_currency = "USD"
elif country == "CO":
    user_currency = "COP"

print(f"\n   Estado de bonos por rango (moneda: {user_currency}):")
bonos_esperados_total = 0
rangos_faltantes = []

for rango_nombre in sorted(rangos_en_historial):
    # Verificar si tiene bono pagado
    bono_existe = any(rango_nombre in notes for (_, _, _, notes, _) in bonos_pagados)
    
    # Obtener monto esperado
    bonus_amounts = RANK_ADVANCEMENT_AMOUNTS.get(rango_nombre, {})
    monto_esperado = bonus_amounts.get(user_currency, 0)
    
    if monto_esperado > 0:
        bonos_esperados_total += monto_esperado
        status = "✅ PAGADO" if bono_existe else "❌ FALTA PAGAR"
        print(f"   - {rango_nombre}: ${monto_esperado:,.2f} {user_currency} - {status}")
        
        if not bono_existe:
            rangos_faltantes.append((rango_nombre, monto_esperado, user_currency))
    else:
        print(f"   - {rango_nombre}: Sin bono definido")

print(f"\n📊 RESUMEN:")
print(f"   Rangos alcanzados: {len(rangos_en_historial)}")
print(f"   Bonos pagados: {len(bonos_pagados)} = ${total_pagado:,.2f}")
print(f"   Bonos esperados: ${bonos_esperados_total:,.2f}")
print(f"   Diferencia: ${bonos_esperados_total - total_pagado:,.2f}")

if rangos_faltantes:
    print(f"\n⚠️  BONOS FALTANTES POR PAGAR:")
    for rango, monto, currency in rangos_faltantes:
        print(f"   - {rango}: ${monto:,.2f} {currency}")

cur.close()
conn.close()

print(f"\n" + "="*70)
print("VERIFICACIÓN COMPLETADA")
print("="*70)
