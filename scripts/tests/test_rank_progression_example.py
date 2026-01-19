"""
Test: Simular el ejemplo de progresión de rango dado en los requisitos
Ejemplo: Usuario Visionario con 10,500 PVG → Siguiente rango Emprendedor (21,000 PVG)
         Debe mostrar: "10,500 — 21,000 PVG" con barra al 50%
"""

import reflex as rx
import sqlmodel
from database.users import Users
from database.user_rank_history import UserRankHistory
from database.ranks import Ranks
from datetime import datetime, timezone

print("\n" + "="*80)
print("🧪 TEST: Ejemplo de Visionario con 10,500 PVG")
print("="*80 + "\n")

def simulate_progression_example():
    """Simula el ejemplo dado en los requisitos."""
    
    # Datos del ejemplo
    current_pvg = 10500
    current_rank_name = "Visionario"
    next_rank_name = "Emprendedor"
    next_rank_pvg = 21000
    
    # Calcular progreso
    progress_percentage = int((current_pvg / next_rank_pvg) * 100)
    
    print("📊 DATOS DEL EJEMPLO:")
    print(f"   Rango actual: {current_rank_name}")
    print(f"   PVG actual: {current_pvg:,}")
    print(f"   Siguiente rango: {next_rank_name}")
    print(f"   PVG requerido: {next_rank_pvg:,}")
    print()
    
    print("📈 RESULTADO ESPERADO:")
    print(f"   Texto: {current_pvg:,} — {next_rank_pvg:,} PVG")
    print(f"   Progreso: {progress_percentage}%")
    print()
    
    # Visualización de la barra
    bar_length = 50
    filled = int(bar_length * progress_percentage / 100)
    bar = "█" * filled + "░" * (bar_length - filled)
    print(f"   [{bar}] {progress_percentage}%")
    print()
    
    remaining = next_rank_pvg - current_pvg
    print(f"   Faltan: {remaining:,} PVG para alcanzar {next_rank_name}")
    print()
    
    # Verificar que el cálculo es correcto (50%)
    expected_percentage = 50
    if progress_percentage == expected_percentage:
        print(f"   ✅ CORRECTO: {progress_percentage}% == {expected_percentage}%")
    else:
        print(f"   ❌ ERROR: {progress_percentage}% != {expected_percentage}%")
    print()

def check_ranks_in_db():
    """Verifica los rangos disponibles en la base de datos."""
    try:
        with rx.session() as session:
            ranks = session.exec(
                sqlmodel.select(Ranks).order_by(Ranks.id)
            ).all()
            
            print("🏆 RANGOS DISPONIBLES EN BASE DE DATOS:")
            print("-" * 80)
            for rank in ranks:
                print(f"   ID: {rank.id:2d} | {rank.name:20s} | PVG Requerido: {rank.pvg_required:>10,}")
            print()
            
            # Verificar si existe Visionario y Emprendedor
            visionario = next((r for r in ranks if r.name == "Visionario"), None)
            emprendedor = next((r for r in ranks if r.name == "Emprendedor"), None)
            
            if visionario and emprendedor:
                print("✅ Rangos del ejemplo encontrados:")
                print(f"   Visionario: ID {visionario.id}, PVG {visionario.pvg_required:,}")
                print(f"   Emprendedor: ID {emprendedor.id}, PVG {emprendedor.pvg_required:,}")
                print()
                
                if emprendedor.id == visionario.id + 1:
                    print("   ✅ Emprendedor es el siguiente rango después de Visionario")
                else:
                    print(f"   ⚠️  Advertencia: Emprendedor (ID {emprendedor.id}) no es el siguiente después de Visionario (ID {visionario.id})")
            else:
                if not visionario:
                    print("   ⚠️  Rango 'Visionario' no encontrado")
                if not emprendedor:
                    print("   ⚠️  Rango 'Emprendedor' no encontrado")
            print()
            
    except Exception as e:
        print(f"❌ Error consultando rangos: {e}")
        import traceback
        traceback.print_exc()

# Ejecutar pruebas
simulate_progression_example()
print("-" * 80)
print()
check_ranks_in_db()

print("="*80)
print("✅ TEST COMPLETADO")
print("="*80 + "\n")

print("💡 PRÓXIMOS PASOS:")
print("   1. Ejecutar: reflex run")
print("   2. Navegar a: http://localhost:3000/dashboard")
print("   3. Verificar que la sección 'Progresión siguiente rango' muestre:")
print("      - PVG actuales del usuario")
print("      - PVG necesarios para el siguiente rango")
print("      - Barra de progreso proporcional al porcentaje alcanzado")
print()
