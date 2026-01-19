#!/usr/bin/env python3
"""
Script para crear automáticamente los rangos del sistema MLM en Supabase.
Basado en el plan de compensación de NNProtect.

Principios aplicados: KISS, DRY, YAGNI, POO
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv
import psycopg2
from typing import List, Dict, Any

# Añadir el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configurar variables de entorno
load_dotenv()


class RankManager:
    """
    Gestor POO para la creación automática de rangos del sistema MLM.
    Principio POO: Encapsula toda la lógica de gestión de rangos.
    """
    
    # ✅ Principio DRY: Rangos definidos en un solo lugar
    MLM_RANKS = [
        {
            "name": "Sin rango",
            "pv_required": 0,
            "pvg_required": 0,
        },
        {
            "name": "Visionario", 
            "pv_required": 1465,
            "pvg_required": 1465,
        },
        {
            "name": "Emprendedor",
            "pv_required": 1465,
            "pvg_required": 21000,
        },
        {
            "name": "Creativo",
            "pv_required": 1465,
            "pvg_required": 58000,
        },
        {
            "name": "Innovador",
            "pv_required": 1465,
            "pvg_required": 120000,
        },
        {
            "name": "Embajador Transformador",
            "pv_required": 1465,
            "pvg_required": 300000,
        },
        {
            "name": "Embajador Inspirador",
            "pv_required": 1465,
            "pvg_required": 650000,
        },
        {
            "name": "Embajador Consciente",
            "pv_required": 1465,
            "pvg_required": 1300000,
        },
        {
            "name": "Embajador Solidario",
            "pv_required": 1465,
            "pvg_required": 2900000,
        }
    ]
    
    def __init__(self):
        """Inicializar conexión a base de datos."""
        self.database_url = os.getenv('DATABASE_URL')
        if not self.database_url:
            raise ValueError("DATABASE_URL no encontrada en variables de entorno")
    
    def get_connection(self) -> psycopg2.extensions.connection:
        """
        Obtiene conexión a la base de datos.
        Principio KISS: Método simple para conexión.
        """
        try:
            return psycopg2.connect(self.database_url)
        except Exception as e:
            raise ConnectionError(f"Error conectando a base de datos: {e}")
    
    def rank_exists(self, conn: psycopg2.extensions.connection, rank_name: str) -> bool:
        """
        Verifica si un rango ya existe en la base de datos.
        Principio YAGNI: Solo verifica lo necesario para evitar duplicados.
        """
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM ranks WHERE name = %s", (rank_name,))
                result = cur.fetchone()
                count = result[0] if result else 0
                return count > 0
        except Exception as e:
            print(f"⚠️  Error verificando rango {rank_name}: {e}")
            return False
    
    def insert_rank(self, conn: psycopg2.extensions.connection, rank_data: Dict[str, Any]) -> bool:
        """
        Inserta un rango en la base de datos.
        Principio POO: Método específico para inserción de rangos.
        """
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO ranks (name, pv_required, pvg_required) 
                    VALUES (%s, %s, %s)
                """, (
                    rank_data["name"],
                    rank_data["pv_required"], 
                    rank_data["pvg_required"]
                ))
                
                print(f"✅ Rango '{rank_data['name']}' creado exitosamente")
                print(f"   PV requerido: {rank_data['pv_required']}")
                print(f"   PVG requerido: {rank_data['pvg_required']}")
                return True
                
        except Exception as e:
            print(f"❌ Error insertando rango {rank_data['name']}: {e}")
            return False
    
    def create_all_ranks(self) -> bool:
        """
        Método principal: Crea todos los rangos del sistema MLM.
        Principio KISS: Un método que hace todo el trabajo necesario.
        """
        print("🚀 Iniciando creación de rangos MLM en Supabase...")
        print(f"📊 Total de rangos a crear: {len(self.MLM_RANKS)}")
        
        conn = None
        success_count = 0
        
        try:
            conn = self.get_connection()
            print("✅ Conexión a Supabase establecida")
            
            for rank_data in self.MLM_RANKS:
                print(f"\n🔍 Procesando rango: {rank_data['name']}")
                
                # Verificar si ya existe
                if self.rank_exists(conn, rank_data["name"]):
                    print(f"⚠️  Rango '{rank_data['name']}' ya existe, omitiendo...")
                    continue
                
                # Insertar nuevo rango
                if self.insert_rank(conn, rank_data):
                    success_count += 1
            
            # Confirmar cambios
            conn.commit()
            print(f"\n🎉 Proceso completado: {success_count} rangos creados exitosamente")
            
            return success_count > 0
            
        except Exception as e:
            print(f"\n💥 Error general: {e}")
            if conn:
                conn.rollback()
            return False
            
        finally:
            if conn:
                conn.close()
                print("🔐 Conexión a base de datos cerrada")
    
    def verify_ranks_created(self) -> bool:
        """
        Verifica que todos los rangos se hayan creado correctamente.
        Principio YAGNI: Solo valida lo esencial.
        """
        print("\n🧪 Verificando rangos creados...")
        
        conn = None
        try:
            conn = self.get_connection()
            
            with conn.cursor() as cur:
                # Obtener todos los rangos ordenados por PV requerido
                cur.execute("""
                    SELECT id, name, pv_required, pvg_required 
                    FROM ranks 
                    ORDER BY pv_required ASC
                """)
                
                ranks = cur.fetchall()
                
                print(f"📋 Total de rangos en base de datos: {len(ranks)}")
                print("\n📊 Rangos disponibles:")
                
                for rank in ranks:
                    rank_id, name, pv_req, pvg_req = rank
                    print(f"  {rank_id:2d}. {name:15s} - PV: {pv_req:5d} | PVG: {pvg_req:6d}")
                
                # Verificar que tenemos al menos los rangos básicos
                expected_ranks = [r["name"] for r in self.MLM_RANKS]
                found_ranks = [r[1] for r in ranks]
                
                missing_ranks = set(expected_ranks) - set(found_ranks)
                
                if missing_ranks:
                    print(f"\n⚠️  Rangos faltantes: {missing_ranks}")
                    return False
                else:
                    print("\n✅ Todos los rangos esperados están presentes")
                    return True
                    
        except Exception as e:
            print(f"❌ Error verificando rangos: {e}")
            return False
            
        finally:
            if conn:
                conn.close()


def main():
    """
    Función principal del script.
    Principio KISS: Ejecución simple y directa.
    """
    print("=" * 60)
    print("🏆 CREADOR AUTOMÁTICO DE RANGOS MLM - NNProtect")
    print("=" * 60)
    
    try:
        # Crear instancia del gestor
        rank_manager = RankManager()
        
        # Crear todos los rangos
        creation_success = rank_manager.create_all_ranks()
        
        if creation_success:
            # Verificar que se crearon correctamente
            verification_success = rank_manager.verify_ranks_created()
            
            if verification_success:
                print("\n" + "=" * 60)
                print("🎉 ¡PROCESO COMPLETADO EXITOSAMENTE!")
                print("✅ Todos los rangos MLM están listos para usar")
                print("🚀 El sistema de rangos está operativo")
                print("=" * 60)
                return True
            else:
                print("\n💥 Error en la verificación de rangos")
                return False
        else:
            print("\n💥 Error en la creación de rangos")
            return False
            
    except Exception as e:
        print(f"\n💥 Error crítico: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)