"""
Test para verificar la carga de estadísticas de usuarios en el dashboard
"""

import reflex as rx
import sqlmodel
from database.users import Users, UserStatus

print("\n" + "="*80)
print("🧪 TEST: Estadísticas de usuarios en dashboard")
print("="*80 + "\n")

with rx.session() as session:
    # 1. Contar usuarios calificados
    qualified_count = session.exec(
        sqlmodel.select(sqlmodel.func.count(Users.id))
        .where(Users.status == UserStatus.QUALIFIED)
    ).first() or 0
    
    # 2. Contar usuarios no calificados
    non_qualified_count = session.exec(
        sqlmodel.select(sqlmodel.func.count(Users.id))
        .where(Users.status == UserStatus.NO_QUALIFIED)
    ).first() or 0
    
    # 3. Total
    total = qualified_count + non_qualified_count
    
    # 4. Porcentajes
    if total > 0:
        qualified_pct = (qualified_count / total) * 100
        non_qualified_pct = (non_qualified_count / total) * 100
    else:
        qualified_pct = 0.0
        non_qualified_pct = 0.0
    
    print("📊 DATOS DE USUARIOS:")
    print("-" * 80)
    print(f"{'Tipo':<25} {'Cantidad':<15} {'Porcentaje'}")
    print("-" * 80)
    print(f"{'Calificados (QUALIFIED)':<25} {qualified_count:<15} {qualified_pct:.1f}%")
    print(f"{'No calificados (NO_QUALIFIED)':<25} {non_qualified_count:<15} {non_qualified_pct:.1f}%")
    print("-" * 80)
    print(f"{'TOTAL':<25} {total:<15} 100.0%")
    print()
    
    # 5. Visualización de barras
    print("📊 VISUALIZACIÓN DE BARRAS:")
    print("-" * 80)
    
    # Barra verde (calificados)
    green_bar_length = int((qualified_pct / 100) * 50)
    green_bar = "█" * green_bar_length
    
    # Barra roja (no calificados)
    red_bar_length = int((non_qualified_pct / 100) * 50)
    red_bar = "█" * red_bar_length
    
    print(f"Verde (Calificados):     {green_bar} {qualified_pct:.1f}%")
    print(f"Roja (No calificados):   {red_bar} {non_qualified_pct:.1f}%")
    print()
    
    # 6. Datos para UI
    print("📱 DATOS PARA UI:")
    print("-" * 80)
    print(f"qualified_count: {qualified_count}")
    print(f"non_qualified_count: {non_qualified_count}")
    print(f"qualified_percentage: {qualified_pct:.2f}")
    print(f"non_qualified_percentage: {non_qualified_pct:.2f}")
    print()
    
    # 7. Formato de texto para UI
    print("📝 TEXTO PARA UI:")
    print("-" * 80)
    print(f"Desktop: 'Calificados – {qualified_count}' | 'No calificados – {non_qualified_count}'")
    print(f"Mobile:  'Calificados: {qualified_count}' | 'No calificados: {non_qualified_count}'")
    print()
    
    # 8. Ancho de barras para CSS
    print("🎨 ANCHOS DE BARRAS (CSS):")
    print("-" * 80)
    print(f"Barra verde (calificados):     width=\"{qualified_pct}%\"")
    print(f"Barra roja (no calificados):   width=\"{non_qualified_pct}%\"")
    print()

print("="*80)
print("✅ Test completado - Los datos están listos para la UI")
print("="*80 + "\n")
