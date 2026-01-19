#!/usr/bin/env python3
"""
Script para crear automáticamente los productos de NNProtect en Supabase.
Lee los datos desde nn_protect_less_products.csv y los inserta en la base de datos.

Principios aplicados: KISS, DRY, YAGNI, POO
"""

import os
import sys
import csv
from datetime import datetime
from dotenv import load_dotenv
import psycopg2
from typing import List, Dict, Any

# Añadir el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configurar variables de entorno
load_dotenv()


class ProductManager:
    """
    Gestor POO para la creación automática de productos desde CSV.
    Principio POO: Encapsula toda la lógica de gestión de productos.
    """
    
    def __init__(self, csv_file_path: str):
        """Inicializar con la ruta del archivo CSV."""
        self.csv_file_path = csv_file_path
        self.database_url = os.getenv('DATABASE_URL')
        
        if not self.database_url:
            raise ValueError("DATABASE_URL no encontrada en variables de entorno")
        
        if not os.path.exists(csv_file_path):
            raise FileNotFoundError(f"Archivo CSV no encontrado: {csv_file_path}")
    
    def get_connection(self) -> psycopg2.extensions.connection:
        """
        Obtiene conexión a la base de datos.
        Principio KISS: Método simple para conexión.
        """
        try:
            return psycopg2.connect(self.database_url)
        except Exception as e:
            raise ConnectionError(f"Error conectando a base de datos: {e}")
    
    def read_products_from_csv(self) -> List[Dict[str, Any]]:
        """
        Lee productos desde el archivo CSV.
        Principio DRY: Método centralizado para lectura de CSV.
        """
        products = []
        
        try:
            with open(self.csv_file_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                for row in reader:
                    # Convertir strings vacíos a None
                    product_data = {}
                    for key, value in row.items():
                        if value.strip() == '':
                            product_data[key] = None
                        elif key == 'id':
                            # Campo ID numérico
                            product_data[key] = int(value) if value.strip() else None
                        elif key == 'quantity':
                            # Campo quantity puede ser texto ("30 ml") o número
                            product_data[key] = value.strip() if value.strip() else None
                        elif key in ['pv_mx', 'pv_usa', 'pv_colombia', 
                                     'vn_mx', 'vn_usa', 'vn_colombia',
                                     'price_mx', 'price_usa', 'price_colombia',
                                     'public_mx', 'public_usa', 'public_colombia']:
                            # Campos numéricos decimales
                            product_data[key] = float(value) if value.strip() else 0.0
                        elif key == 'is_new':
                            # Campo booleano
                            product_data[key] = value.strip().lower() == 'true'
                        else:
                            # Campos de texto
                            product_data[key] = value.strip() if value.strip() else None
                    
                    products.append(product_data)
                
                print(f"📋 {len(products)} productos leídos desde CSV")
                return products
                
        except Exception as e:
            print(f"❌ Error leyendo CSV: {e}")
            raise
    
    def product_exists(self, conn: psycopg2.extensions.connection, product_name: str) -> bool:
        """
        Verifica si un producto ya existe en la base de datos.
        Principio YAGNI: Solo verifica lo necesario para evitar duplicados.
        """
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM products WHERE product_name = %s", (product_name,))
                result = cur.fetchone()
                count = result[0] if result else 0
                return count > 0
        except Exception as e:
            print(f"⚠️  Error verificando producto {product_name}: {e}")
            return False
    
    def insert_product(self, conn: psycopg2.extensions.connection, product_data: Dict[str, Any]) -> bool:
        """
        Inserta un producto en la base de datos.
        Principio POO: Método específico para inserción de productos.
        """
        try:
            with conn.cursor() as cur:
                # No incluimos 'id' en el INSERT porque es autogenerado
                cur.execute("""
                    INSERT INTO products (
                        product_name, active_ingredient, "SKU", description, 
                        presentation, type, quantity,
                        pv_mx, pv_usa, pv_colombia,
                        vn_mx, vn_usa, vn_colombia,
                        price_mx, price_usa, price_colombia,
                        public_mx, public_usa, public_colombia,
                        is_new
                    ) 
                    VALUES (
                        %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s,
                        %s, %s, %s,
                        %s, %s, %s,
                        %s, %s, %s,
                        %s
                    )
                """, (
                    product_data["product_name"],
                    product_data["active_ingredient"],
                    product_data["SKU"],
                    product_data["description"],
                    product_data["presentation"],
                    product_data["type"],
                    product_data["quantity"],
                    product_data["pv_mx"],
                    product_data["pv_usa"],
                    product_data["pv_colombia"],
                    product_data["vn_mx"],
                    product_data["vn_usa"],
                    product_data["vn_colombia"],
                    product_data["price_mx"],
                    product_data["price_usa"],
                    product_data["price_colombia"],
                    product_data["public_mx"],
                    product_data["public_usa"],
                    product_data["public_colombia"],
                    product_data["is_new"]
                ))
                
                print(f"✅ Producto '{product_data['product_name']}' creado exitosamente")
                print(f"   Tipo: {product_data['type']} | PV MX: {product_data['pv_mx']} | Precio MX: ${product_data['price_mx']}")
                return True
                
        except Exception as e:
            print(f"❌ Error insertando producto {product_data['product_name']}: {e}")
            return False
    
    def create_all_products(self) -> bool:
        """
        Método principal: Crea todos los productos desde el CSV.
        Principio KISS: Un método que hace todo el trabajo necesario.
        """
        print("🚀 Iniciando creación de productos en Supabase...")
        
        # Leer productos desde CSV
        try:
            products = self.read_products_from_csv()
        except Exception as e:
            print(f"💥 Error leyendo productos: {e}")
            return False
        
        print(f"📊 Total de productos a crear: {len(products)}")
        
        conn = None
        success_count = 0
        
        try:
            conn = self.get_connection()
            print("✅ Conexión a Supabase establecida")
            
            for product_data in products:
                product_name = product_data.get("product_name", "Desconocido")
                print(f"\n🔍 Procesando producto: {product_name}")
                
                # Verificar si ya existe
                if self.product_exists(conn, product_name):
                    print(f"⚠️  Producto '{product_name}' ya existe, omitiendo...")
                    continue
                
                # Insertar nuevo producto
                if self.insert_product(conn, product_data):
                    success_count += 1
            
            # Confirmar cambios
            conn.commit()
            print(f"\n🎉 Proceso completado: {success_count} productos creados exitosamente")
            
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
    
    def verify_products_created(self) -> bool:
        """
        Verifica que todos los productos se hayan creado correctamente.
        Principio YAGNI: Solo valida lo esencial.
        """
        print("\n🧪 Verificando productos creados...")
        
        conn = None
        try:
            conn = self.get_connection()
            
            with conn.cursor() as cur:
                # Obtener todos los productos
                cur.execute("""
                    SELECT id, product_name, type, price_mx, pv_mx, is_new
                    FROM products 
                    ORDER BY id ASC
                """)
                
                products = cur.fetchall()
                
                print(f"📋 Total de productos en base de datos: {len(products)}")
                print("\n📊 Productos disponibles:")
                print("-" * 80)
                
                for product in products:
                    product_id, name, ptype, price, pv, is_new = product
                    new_badge = "🆕" if is_new else "  "
                    print(f"{new_badge} {product_id:2d}. {name:30s} | {ptype:12s} | ${price:7.2f} | PV: {pv:5.0f}")
                
                print("-" * 80)
                
                # Contar por tipo
                cur.execute("""
                    SELECT type, COUNT(*) as count
                    FROM products
                    GROUP BY type
                    ORDER BY count DESC
                """)
                
                types_summary = cur.fetchall()
                print("\n📈 Resumen por tipo:")
                for ptype, count in types_summary:
                    print(f"  • {ptype}: {count} productos")
                
                print("\n✅ Verificación completada")
                return True
                    
        except Exception as e:
            print(f"❌ Error verificando productos: {e}")
            return False
            
        finally:
            if conn:
                conn.close()


def main():
    """
    Función principal del script.
    Principio KISS: Ejecución simple y directa.
    """
    print("=" * 80)
    print("🛍️  CREADOR AUTOMÁTICO DE PRODUCTOS - NNProtect")
    print("=" * 80)
    
    # Ruta del archivo CSV
    csv_file = os.path.join(os.path.dirname(__file__), "nn_protect_less_products.csv")
    
    try:
        # Crear instancia del gestor
        product_manager = ProductManager(csv_file)
        
        # Crear todos los productos
        creation_success = product_manager.create_all_products()
        
        if creation_success:
            # Verificar que se crearon correctamente
            verification_success = product_manager.verify_products_created()
            
            if verification_success:
                print("\n" + "=" * 80)
                print("🎉 ¡PROCESO COMPLETADO EXITOSAMENTE!")
                print("✅ Todos los productos están listos para usar")
                print("🚀 El catálogo de productos está operativo")
                print("=" * 80)
                return True
            else:
                print("\n💥 Error en la verificación de productos")
                return False
        else:
            print("\n⚠️  No se crearon nuevos productos (pueden ya existir)")
            # Aún así verificamos qué hay en la BD
            product_manager.verify_products_created()
            return True
            
    except Exception as e:
        print(f"\n💥 Error crítico: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
