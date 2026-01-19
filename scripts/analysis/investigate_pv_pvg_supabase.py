"""
═══════════════════════════════════════════════════════════════════════════════
📋 INVESTIGACIÓN: PV/PVG Y COMISIONES UNINIVEL (SQL DIRECTO)
═══════════════════════════════════════════════════════════════════════════════

Investiga dos problemas:
1. Por qué pvg_cache no incluye el pv_cache del usuario
2. Por qué hay $732.50 perdidos en comisiones Uninivel

Autor: Arquitecto de Datos + Auditor de Comisiones
"""

import os
from supabase import create_client

def main():
    print("\n═══════════════════════════════════════════════════════════════════════════════")
    print("📋 INVESTIGACIÓN: PV/PVG Y COMISIONES UNINIVEL")
    print("═══════════════════════════════════════════════════════════════════════════════\n")
    
    # Conectar a Supabase
    supabase_url = os.environ.get("SUPABASE_URL", "")
    supabase_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    
    if not supabase_url or not supabase_key:
        print("❌ Error: SUPABASE_URL o SUPABASE_SERVICE_ROLE_KEY no están configuradas")
        return
    
    supabase = create_client(supabase_url, supabase_key)
    
    # ═══════════════════════════════════════════════════════════════════
    # OBJETIVO 1: INVESTIGAR PV/PVG
    # ═══════════════════════════════════════════════════════════════════
    
    print("🔍 OBJETIVO 1: VERIFICAR POR QUÉ PV_CACHE NO SE SUMA A PVG_CACHE")
    print("═══════════════════════════════════════════════════════════════════════════════\n")
    
    # Obtener usuarios 1, 2, 3
    response = supabase.table("users").select("*").in_("member_id", [1, 2, 3]).order("member_id").execute()
    users = response.data
    
    print("📊 ESTADO ACTUAL (BASE DE DATOS):\n")
    for user in users:
        print(f"   Member {user['member_id']} ({user['full_name']}):")
        print(f"      PV={user['pv_cache']}, PVG={user['pvg_cache']}, VN={user['vn_cache']:.2f}")
        print(f"      Sponsor={user.get('sponsor_id', 'NULL')}, Status={user['status']}\n")
    
    # Verificar árbol genealógico
    print("\n📐 ÁRBOL GENEALÓGICO:\n")
    response = supabase.table("usertreepaths")\
        .select("*")\
        .or_(f"ancestor_id.in.(1,2,3),descendant_id.in.(1,2,3)")\
        .gt("depth", 0)\
        .order("descendant_id,depth")\
        .execute()
    
    paths = response.data
    for path in paths:
        print(f"   Descendiente {path['descendant_id']} → Ancestro {path['ancestor_id']} (Profundidad {path['depth']})")
    
    print("\n" + "─" * 79)
    print("\n❌ PROBLEMA IDENTIFICADO:\n")
    print("   La lógica actual en admin_state.py (línea 1010) dice:")
    print("   ")
    print("   user.pvg_cache += total_pv")
    print("   ")
    print("   Esto significa que SOLO se suma el PV de la compra actual, pero NO incluye")
    print("   el PV acumulado del usuario (pv_cache).\n")
    
    print("💡 EXPLICACIÓN DEL ERROR:\n")
    print("   Según la documentación del plan de compensación, el PVG (Puntos de Volumen Grupal)")
    print("   debe incluir:")
    print("   ")
    print("   1. El PV personal del usuario (su propio pv_cache)")
    print("   2. El PV de todos sus descendientes")
    print("   ")
    print("   Fórmula correcta:")
    print("   PVG = PV_personal + Σ(PV_descendientes)\n")
    
    print("📊 CÁLCULO ESPERADO:\n")
    print("   Member 3: PVG = 1465 (su propio pv_cache)")
    print("   Member 2: PVG = 1465 (member 2 pv_cache) + 1465 (member 3 pv_cache) = 2930")
    print("   Member 1: PVG = 1465 + 1465 + 1465 = 4,395\n")
    
    print("📊 CÁLCULO ACTUAL (INCORRECTO):\n")
    if len(users) >= 3:
        print(f"   Member 3: PVG = {users[2]['pvg_cache']} (debería ser 1465)")
        print(f"   Member 2: PVG = {users[1]['pvg_cache']} (debería ser 2930)")
        print(f"   Member 1: PVG = {users[0]['pvg_cache']} (debería ser 4395)\n")
    
    # ═══════════════════════════════════════════════════════════════════
    # OBJETIVO 2: INVESTIGAR COMISIONES UNINIVEL
    # ═══════════════════════════════════════════════════════════════════
    
    print("\n" + "═" * 79)
    print("🔍 OBJETIVO 2: VERIFICAR GANANCIAS UNINIVEL PARA MEMBER_ID 1")
    print("═══════════════════════════════════════════════════════════════════════════════\n")
    
    # Obtener comisiones Uninivel para member_id 1
    response = supabase.table("commissions")\
        .select("*")\
        .eq("member_id", 1)\
        .eq("bonus_type", "BONO_UNINIVEL")\
        .execute()
    
    commissions = response.data
    
    print("📊 COMISIONES REALES (AGRUPADAS POR NIVEL):\n")
    
    commissions_by_level = {}
    for comm in commissions:
        level = comm['level_depth']
        if level not in commissions_by_level:
            commissions_by_level[level] = {"count": 0, "total": 0.0}
        commissions_by_level[level]["count"] += 1
        commissions_by_level[level]["total"] += comm['amount_converted']
    
    for level in sorted(commissions_by_level.keys()):
        data = commissions_by_level[level]
        print(f"   Nivel {level}: {data['count']} comisiones → ${data['total']:.2f} MXN")
    
    # Calcular esperado vs real
    print("\n📊 DESCENDIENTES POR NIVEL:\n")
    
    response = supabase.table("usertreepaths")\
        .select("*")\
        .eq("ancestor_id", 1)\
        .gt("depth", 0)\
        .execute()
    
    descendants = response.data
    descendants_by_level = {}
    
    for desc in descendants:
        level = desc['depth']
        if level not in descendants_by_level:
            descendants_by_level[level] = []
        descendants_by_level[level].append(desc['descendant_id'])
    
    for level in sorted(descendants_by_level.keys())[:5]:
        print(f"   Nivel {level}: {len(descendants_by_level[level])} personas")
    
    # Calcular comisiones esperadas vs reales
    print("\n📊 CÁLCULO ESPERADO VS REAL:\n")
    print("┌───────┬──────────┬────────────┬─────────────┬────────────┬─────────────┐")
    print("│ Nivel │ Personas │ Porcentaje │ VN_Total    │ Esperado   │ Real        │")
    print("├───────┼──────────┼────────────┼─────────────┼────────────┼─────────────┤")
    
    percentages = {1: 0.05, 2: 0.08, 3: 0.10, 4: 0.10, 5: 0.05}
    total_expected = 0.0
    total_real = 0.0
    
    for level in range(1, 6):
        if level in descendants_by_level:
            # Obtener VN total de ese nivel
            member_ids = descendants_by_level[level]
            response = supabase.table("users")\
                .select("vn_cache")\
                .in_("member_id", member_ids)\
                .execute()
            
            vn_total = sum(u['vn_cache'] for u in response.data)
            
            percentage = percentages.get(level, 0)
            expected = vn_total * percentage
            real = commissions_by_level.get(level, {}).get("total", 0.0)
            
            total_expected += expected
            total_real += real
            
            print(f"│   {level}   │    {len(member_ids):2d}    │    {int(percentage*100)}%     │ ${vn_total:10,.2f} │ ${expected:9,.2f} │ ${real:10,.2f} │")
    
    print("└───────┴──────────┴────────────┴─────────────┴────────────┴─────────────┘")
    
    print(f"\n💰 RESUMEN DE GANANCIAS:\n")
    print(f"   Total Esperado: ${total_expected:,.2f} MXN")
    print(f"   Total Real:     ${total_real:,.2f} MXN")
    print(f"   Dinero Perdido: ${total_expected - total_real:,.2f} MXN")
    
    if total_expected - total_real > 0:
        print(f"\n   ⚠️  Se perdieron ${total_expected - total_real:,.2f} MXN en comisiones Uninivel")
    
    # ═══════════════════════════════════════════════════════════════════
    # SOLUCIONES PROPUESTAS
    # ═══════════════════════════════════════════════════════════════════
    
    print("\n" + "═" * 79)
    print("🔧 SOLUCIONES PROPUESTAS")
    print("═══════════════════════════════════════════════════════════════════════════════\n")
    
    print("✅ SOLUCIÓN 1: Corregir cálculo de PVG en admin_state.py\n")
    print("   Ubicación: admin_state.py línea 1010")
    print("   ")
    print("   ANTES (INCORRECTO):")
    print("   ──────────────────")
    print("   user.pvg_cache += total_pv")
    print("   ")
    print("   DESPUÉS (CORRECTO - OPCIÓN A):")
    print("   ───────────────────────────────")
    print("   # El PVG debe incluir el PV propio del usuario")
    print("   # La línea 1010 ya suma el PV al cache del usuario")
    print("   user.pvg_cache = user.pv_cache  # PVG siempre = PV propio + descendientes")
    print("   ")
    print("   DESPUÉS (CORRECTO - OPCIÓN B - MÁS CONSERVADORA):")
    print("   ──────────────────────────────────────────────────")
    print("   # Si es la primera compra del usuario, inicializar PVG")
    print("   if user.pvg_cache == 0 and total_pv == user.pv_cache:")
    print("       user.pvg_cache = total_pv  # Primera vez: PVG = PV")
    print("   else:")
    print("       user.pvg_cache += total_pv  # Siguientes: solo sumar incremento")
    print("   ")
    print("✅ SOLUCIÓN 2: Recalcular PVG para todos los usuarios existentes\n")
    print("   Crear script SQL que:")
    print("   1. Para cada usuario, calcular su PVG real:")
    print("      PVG = pv_cache + SUM(descendientes.pv_cache)")
    print("   2. Actualizar pvg_cache con el valor correcto")
    print("   ")
    print("✅ SOLUCIÓN 3: Verificar cálculo de Uninivel\n")
    print("   El método _trigger_unilevel_for_ancestors() debe:")
    print("   1. Usar el VN correcto de cada orden")
    print("   2. Calcular % según rango y nivel")
    print("   3. Crear comisión para CADA ancestro calificado")
    print("   ")
    print("   Posibles causas del dinero perdido:")
    print("   • VN_cache no se está calculando correctamente")
    print("   • Algunos ancestros no califican (pv_cache < 1465)")
    print("   • El rango del ancestro no permite cobrar ese nivel\n")
    
    print("═" * 79)
    print("📊 PRÓXIMOS PASOS")
    print("═══════════════════════════════════════════════════════════════════════════════\n")
    print("1. 🔴 CRÍTICO: Corregir lógica de PVG en admin_state.py (línea 1010)")
    print("2. 🔴 CRÍTICO: Crear script para recalcular PVG de usuarios existentes")
    print("3. 🔴 CRÍTICO: Verificar por qué hay dinero perdido en Uninivel")
    print("4. 🟡 MEDIO: Revisar si payment_service.py también tiene el bug de PVG")
    print("5. 🟡 MEDIO: Agregar validaciones automáticas en tests")
    print("6. 🟢 BAJO: Documentar el cálculo correcto de PVG\n")
    
    print("═" * 79)

if __name__ == "__main__":
    main()
