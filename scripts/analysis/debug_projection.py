"""
Script de debug para verificar proyección de ganancias
"""
import os
os.chdir('/Users/bradrez/Documents/NNProtect_new_website')

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

# 1. Obtener member_id del usuario autenticado (asumimos el último registrado para pruebas)
cur.execute("""
    SELECT member_id, first_name, last_name, pv_cache, pvg_cache, country_cache
    FROM users 
    WHERE email = 'bradrezdev@gmail.com'
    LIMIT 1
""")
user = cur.fetchone()

if not user:
    print("❌ Usuario no encontrado")
    exit()

member_id, first_name, last_name, pv, pvg, country = user
print(f"\n👤 Usuario: {first_name} {last_name} (member_id={member_id})")
print(f"   PV: {pv}, PVG: {pvg}, País: {country}")

# 2. Obtener período actual
cur.execute("""
    SELECT id, name, starts_on, ends_on
    FROM periods
    WHERE starts_on <= NOW() AND ends_on >= NOW()
    LIMIT 1
""")
period = cur.fetchone()

if not period:
    print("❌ No hay período actual")
    exit()

period_id, period_name, starts_on, ends_on = period
print(f"\n📅 Período actual: {period_name} (ID={period_id})")
print(f"   Desde: {starts_on} hasta {ends_on}")

# 3. Obtener historial de rangos del usuario
cur.execute("""
    SELECT urh.rank_id, r.name, urh.achieved_on, urh.period_id
    FROM user_rank_history urh
    JOIN ranks r ON r.id = urh.rank_id
    WHERE urh.member_id = %s
    ORDER BY urh.achieved_on DESC
""", (member_id,))
ranks = cur.fetchall()

print(f"\n🏆 Historial de Rangos:")
for rank_id, rank_name, achieved_on, rank_period_id in ranks:
    print(f"   - {rank_name} (ID={rank_id}) alcanzado el {achieved_on} en período {rank_period_id}")

# 4. Obtener bonos por alcance registrados
cur.execute("""
    SELECT id, bonus_type, amount_converted, currency_destination, notes, calculated_at, period_id
    FROM commissions
    WHERE member_id = %s 
    AND bonus_type = 'BONO_ALCANCE'
    ORDER BY calculated_at DESC
""", (member_id,))
achievement_bonuses = cur.fetchall()

print(f"\n💰 Bonos por Alcance Registrados:")
total_alcance = 0
for comm_id, bonus_type, amount, currency, notes, calc_at, comm_period_id in achievement_bonuses:
    print(f"   - ID={comm_id}: ${amount} {currency} - {notes}")
    print(f"     Calculado: {calc_at}, Período: {comm_period_id}")
    total_alcance += float(amount)
print(f"   TOTAL ALCANCE: ${total_alcance}")

# 5. Obtener todas las comisiones del período actual
cur.execute("""
    SELECT bonus_type, COUNT(*) as qty, SUM(amount_converted) as total
    FROM commissions
    WHERE member_id = %s 
    AND period_id = %s
    GROUP BY bonus_type
""", (member_id, period_id))
commissions_summary = cur.fetchall()

print(f"\n📊 Resumen de Comisiones en Período Actual:")
grand_total = 0
for bonus_type, qty, total in commissions_summary:
    print(f"   - {bonus_type}: {qty} comisiones = ${total}")
    grand_total += float(total) if total else 0
print(f"   TOTAL PERÍODO: ${grand_total}")

# 6. Verificar órdenes del período que podrían generar Uninivel
cur.execute("""
    SELECT o.id, o.order_number, o.total_pv, o.customer_member_id, o.status, o.created_at
    FROM orders o
    JOIN usertreepath utp ON o.customer_member_id = utp.descendant_member_id
    WHERE utp.ancestor_member_id = %s
    AND o.created_at >= %s
    AND o.created_at <= %s
    AND o.status = 'COMPLETED'
    ORDER BY o.created_at DESC
""", (member_id, starts_on, ends_on))
downline_orders = cur.fetchall()

print(f"\n🛒 Órdenes de Downline en Período Actual:")
total_downline_pv = 0
for order_id, order_num, pv, customer_id, status, created_at in downline_orders:
    print(f"   - Orden {order_num}: {pv} PV de member_id={customer_id} el {created_at}")
    total_downline_pv += float(pv) if pv else 0
print(f"   TOTAL PV DOWNLINE: {total_downline_pv}")

# 7. Verificar comisiones Uninivel calculadas
cur.execute("""
    SELECT id, level_depth, amount_vn, amount_converted, source_order_id, calculated_at
    FROM commissions
    WHERE member_id = %s 
    AND bonus_type = 'BONO_UNINIVEL'
    AND period_id = %s
    ORDER BY calculated_at DESC
""", (member_id, period_id))
uninivel_commissions = cur.fetchall()

print(f"\n🔢 Comisiones Uninivel del Período:")
total_uninivel = 0
for comm_id, level, vn, converted, order_id, calc_at in uninivel_commissions:
    print(f"   - ID={comm_id}: Nivel {level}, ${converted} (de orden {order_id})")
    total_uninivel += float(converted) if converted else 0
print(f"   TOTAL UNINIVEL: ${total_uninivel}")

# 8. Verificar comisiones Matching calculadas
cur.execute("""
    SELECT id, level_depth, amount_vn, amount_converted, source_member_id, calculated_at
    FROM commissions
    WHERE member_id = %s 
    AND bonus_type = 'BONO_MATCHING'
    AND period_id = %s
    ORDER BY calculated_at DESC
""", (member_id, period_id))
matching_commissions = cur.fetchall()

print(f"\n🤝 Comisiones Matching del Período:")
total_matching = 0
for comm_id, level, vn, converted, source_id, calc_at in matching_commissions:
    print(f"   - ID={comm_id}: Nivel {level}, ${converted} (de member_id={source_id})")
    total_matching += float(converted) if converted else 0
print(f"   TOTAL MATCHING: ${total_matching}")

print(f"\n" + "="*60)
print(f"💵 PROYECCIÓN ACTUAL (suma de comisiones registradas):")
print(f"   Alcance:  ${total_alcance:,.2f}")
print(f"   Uninivel: ${total_uninivel:,.2f}")
print(f"   Matching: ${total_matching:,.2f}")
print(f"   TOTAL:    ${total_alcance + total_uninivel + total_matching:,.2f}")
print("="*60)

cur.close()
conn.close()
