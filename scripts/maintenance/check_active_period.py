#!/usr/bin/env python3
"""
Script para verificar qué período está activo actualmente.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import reflex as rx
from sqlmodel import select
from database.periods import Periods
from NNProtect_new_website.utils.timezone_mx import get_mexico_now

def check_active_period():
    print("\n" + "="*80)
    print("📅 Verificando Período Activo")
    print("="*80)
    
    try:
        with rx.session() as session:
            now = get_mexico_now()
            print(f"\n⏰ Fecha/hora actual (México): {now}")
            
            # Buscar período activo
            current_period = session.exec(
                select(Periods)
                .where(
                    (Periods.starts_on <= now) &
                    (Periods.ends_on >= now)
                )
            ).first()
            
            if current_period:
                print(f"\n✅ Período activo encontrado:")
                print(f"   ID: {current_period.id}")
                print(f"   Nombre: {current_period.name}")
                print(f"   Inicio: {current_period.starts_on}")
                print(f"   Fin: {current_period.ends_on}")
                print(f"   Cerrado: {current_period.closed_at}")
            else:
                print(f"\n❌ No hay período activo para la fecha {now}")
            
            # Mostrar todos los períodos
            print(f"\n📋 Todos los períodos en la base de datos:")
            all_periods = session.exec(
                select(Periods).order_by(Periods.starts_on.desc())
            ).all()
            
            for period in all_periods:
                status = "ACTIVO" if period == current_period else "INACTIVO"
                closed = f"(Cerrado: {period.closed_at})" if period.closed_at else "(Abierto)"
                print(f"   • {period.name} (ID={period.id}): {period.starts_on} → {period.ends_on} [{status}] {closed}")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_active_period()
