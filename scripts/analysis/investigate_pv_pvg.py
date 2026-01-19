"""
═══════════════════════════════════════════════════════════════════════════════
📋 INVESTIGACIÓN: PV/PVG Y COMISIONES UNINIVEL
═══════════════════════════════════════════════════════════════════════════════

Investiga dos problemas:
1. Por qué pvg_cache no incluye el pv_cache del usuario
2. Por qué hay $732.50 perdidos en comisiones Uninivel

Autor: Arquitecto de Datos + Auditor de Comisiones
"""

import sqlmodel
from database.users import Users
from database.usertreepaths import UserTreePath
from database.comissions import Commissions, BonusType
import os

def main():
    print("\n═══════════════════════════════════════════════════════════════════════════════")
    print("📋 INVESTIGACIÓN: PV/PVG Y COMISIONES UNINIVEL")
    print("═══════════════════════════════════════════════════════════════════════════════\n")
    
    # Conectar a base de datos
    db_url = os.environ.get("DATABASE_URL", "")
    if not db_url:
        print("❌ Error: DATABASE_URL no está configurada")
        return
    
    engine = sqlmodel.create_engine(db_url, echo=False)
    
    with sqlmodel.Session(engine) as session:
        
        # ═══════════════════════════════════════════════════════════════════
        # OBJETIVO 1: INVESTIGAR PV/PVG
        # ═══════════════════════════════════════════════════════════════════
        
        print("🔍 OBJETIVO 1: VERIFICAR POR QUÉ PV_CACHE NO SE SUMA A PVG_CACHE")
        print("═══════════════════════════════════════════════════════════════════════════════\n")
        
        # Obtener usuarios 1, 2, 3
        users_data = {}
        for member_id in [1, 2, 3]:
            user = session.exec(
                sqlmodel.select(Users).where(Users.member_id == member_id)
            ).first()
            
            if user:
                users_data[member_id] = {
                    "full_name": user.full_name,
                    "sponsor_id": user.sponsor_id,
                    "pv_cache": user.pv_cache,
                    "pvg_cache": user.pvg_cache,
                    "vn_cache": user.vn_cache,
                    "status": user.status
                }
        
        print("📊 ESTADO ACTUAL (BASE DE DATOS):\n")
        for member_id in [1, 2, 3]:
            if member_id in users_data:
                data = users_data[member_id]
                print(f"   Member {member_id} ({data['full_name']}):")
                print(f"      PV={data['pv_cache']}, PVG={data['pvg_cache']}, VN={data['vn_cache']:.2f}")
                print(f"      Sponsor={data['sponsor_id']}, Status={data['status']}\n")
        
        # Verificar árbol genealógico
        print("\n📐 ÁRBOL GENEALÓGICO:\n")
        paths = session.exec(
            sqlmodel.select(UserTreePath)
            .where(UserTreePath.depth > 0)
        ).all()
        
        paths = [p for p in paths if p.ancestor_id in [1, 2, 3] or p.descendant_id in [1, 2, 3]]
        
        for path in paths:
            print(f"   Descendiente {path.descendant_id} → Ancestro {path.ancestor_id} (Profundidad {path.depth})")
        
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
        print("   Member 3: PVG = 0 (no se incluye su propio PV)")
        print("   Member 2: PVG = 1465 (solo el PV de member 3, no el suyo)")
        print("   Member 1: PVG = 1465 (solo el PV de member 2, no el de 3 ni el suyo)\n")
        
        # ═══════════════════════════════════════════════════════════════════
        # OBJETIVO 2: INVESTIGAR COMISIONES UNINIVEL
        # ═══════════════════════════════════════════════════════════════════
        
        print("\n" + "═" * 79)
        print("🔍 OBJETIVO 2: VERIFICAR GANANCIAS UNINIVEL PARA MEMBER_ID 1")
        print("═══════════════════════════════════════════════════════════════════════════════\n")
        
        # Obtener comisiones Uninivel para member_id 1
        commissions = session.exec(
            sqlmodel.select(Commissions)
            .where(Commissions.member_id == 1)
            .where(Commissions.bonus_type == BonusType.BONO_UNINIVEL.value)
        ).all()
        
        print("📊 COMISIONES REALES (AGRUPADAS POR NIVEL):\n")
        
        commissions_by_level = {}
        for comm in commissions:
            level = comm.level_depth
            if level not in commissions_by_level:
                commissions_by_level[level] = {"count": 0, "total": 0.0}
            commissions_by_level[level]["count"] += 1
            commissions_by_level[level]["total"] += comm.amount_converted
        
        for level in sorted(commissions_by_level.keys()):
            data = commissions_by_level[level]
            print(f"   Nivel {level}: {data['count']} comisiones → ${data['total']:.2f} MXN")
        
        # Calcular esperado vs real
        print("\n📊 DESCENDIENTES POR NIVEL:\n")
        
        descendants_by_level = {}
        descendants = session.exec(
            sqlmodel.select(UserTreePath)
            .where(UserTreePath.ancestor_id == 1)
            .where(UserTreePath.depth > 0)
        ).all()
        
        for desc in descendants:
            level = desc.depth
            if level not in descendants_by_level:
                descendants_by_level[level] = []
            descendants_by_level[level].append(desc.descendant_id)
        
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
                vn_total = 0.0
                for member_id in descendants_by_level[level]:
                    user = session.exec(
                        sqlmodel.select(Users).where(Users.member_id == member_id)
                    ).first()
                    if user:
                        vn_total += user.vn_cache
                
                percentage = percentages.get(level, 0)
                expected = vn_total * percentage
                real = commissions_by_level.get(level, {}).get("total", 0.0)
                
                total_expected += expected
                total_real += real
                
                print(f"│   {level}   │    {len(descendants_by_level[level]):2d}    │    {int(percentage*100)}%     │ ${vn_total:10,.2f} │ ${expected:9,.2f} │ ${real:10,.2f} │")
        
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
        print("   Cambio necesario:")
        print("   ")
        print("   # ANTES (INCORRECTO):")
        print("   user.pvg_cache += total_pv")
        print("   ")
        print("   # DESPUÉS (CORRECTO):")
        print("   # El PVG debe incluir el PV propio del usuario desde el inicio")
        print("   # La línea 1010 ya suma el PV al usuario, así que está bien")
        print("   # El problema es que NO se está sumando el PV del usuario a su propio PVG")
        print("   ")
        print("   # Al crear la orden, el PVG del comprador NO incluye su propio PV")
        print("   # Solución: La línea 1010 debe ser:")
        print("   user.pvg_cache = user.pv_cache  # PVG siempre incluye el PV propio")
        print("   ")
        print("✅ SOLUCIÓN 2: Verificar cálculo de Uninivel en payment_service.py\n")
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
        print("1. 🔴 CRÍTICO: Corregir lógica de PVG en admin_state.py")
        print("2. 🔴 CRÍTICO: Verificar por qué hay dinero perdido en Uninivel")
        print("3. 🟡 MEDIO: Revisar si payment_service.py también tiene el bug de PVG")
        print("4. 🟡 MEDIO: Crear script de corrección para datos existentes")
        print("5. 🟢 BAJO: Agregar validaciones para evitar futuros errores\n")
        
        print("═" * 79)

if __name__ == "__main__":
    main()
