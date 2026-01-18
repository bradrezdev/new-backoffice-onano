#!/usr/bin/env python3
"""
Script de Población de Datos MLM 2x2 - NNProtect
================================================

OBJETIVO:
Crear una red de 5,000 usuarios con estructura 2x2 (árbol binario), 
con datos completos y una orden completada por usuario.

ESTRUCTURA:
- Árbol binario: cada usuario tiene exactamente 2 referidos directos
- Profundidad: ~13 niveles (2^13 = 8,192)

TABLAS POBLADAS POR USUARIO:
1. users
2. usertreepaths
3. wallets
4. user_rank_history
5. userprofiles
6. users_addresses

ÓRDENES:
- 1 orden COMPLETADA por usuario
- Registrada en: orders, order_items, periods

AUTOR: Elena (Backend Architect)
FECHA: 2025-10-21
"""

import sys
import os
from datetime import datetime, timezone
from typing import Optional
import random

# Agregar directorio raíz al path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Imports Reflex y SQLModel
import reflex as rx
import sqlmodel
from sqlmodel import select, func

# Imports de modelos
from datetime import date
from database.users import Users, UserStatus
from database.userprofiles import UserProfiles, UserGender
from database.usertreepaths import UserTreePath
from database.products import Products
from database.orders import Orders, OrderStatus
from database.order_items import OrderItems
from database.periods import Periods
from database.addresses import Addresses
from database.users_addresses import UserAddresses
from database.wallet import Wallets, WalletStatus
from database.user_rank_history import UserRankHistory
from database.ranks import Ranks

# Imports de servicios
from NNProtect_new_website.mlm_service.period_service import PeriodService


class MLMSeeder2x2:
    """
    Seeder para crear red MLM 2x2 con 5,000 usuarios.
    
    Principios aplicados: KISS, DRY, YAGNI, POO
    """
    
    TOTAL_USERS = 5000
    BRANCH_FACTOR = 2  # Estructura 2x2 (binario)
    COMMIT_BATCH_SIZE = 100  # Commit cada 100 usuarios para performance
    
    REQUIRED_PRODUCTS = ["Cúrcuma", "Dreaming Deep", "Chia", "Citrus", "Jengibre"]
    COUNTRIES = ["México", "USA", "Colombia", "República Dominicana"]
    
    def __init__(self, session):
        self.session = session
        self.current_period: Optional[Periods] = None
        self.products_map = {}
        self.default_rank: Optional[Ranks] = None
        self.next_member_id = 1
        
        # Contadores
        self.created_users = 0
        self.created_wallets = 0
        self.created_rank_history = 0
        self.created_orders = 0
        self.created_tree_paths = 0
    
    def run(self) -> bool:
        """Ejecuta el proceso completo de seeding."""
        print("=" * 80)
        print("  SEED MLM 2x2 - 5,000 USUARIOS")
        print("=" * 80)
        print()
        
        try:
            # Paso 1: Verificar prerequisitos
            if not self._verify_prerequisites():
                return False
            
            # Paso 2: Crear red de usuarios (2x2)
            print(f"\n[CREANDO] Red 2x2 de {self.TOTAL_USERS} usuarios...")
            if not self._create_binary_tree():
                return False
            
            # Paso 3: Commit final
            print("\n[FINALIZANDO] Guardando cambios...")
            self.session.commit()
            
            self._print_report()
            return True
            
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            self.session.rollback()
            return False
    
    def _verify_prerequisites(self) -> bool:
        """Verifica período actual, productos y rango default."""
        print("\n[VERIFICANDO] Prerequisitos...")
        
        # 1. Período actual
        self.current_period = PeriodService.get_current_period(self.session)
        if not self.current_period:
            print("   Creando período actual...")
            self.current_period = PeriodService.auto_create_current_month_period(self.session)
            self.session.commit()
        
        if not self.current_period:
            print("❌ No se pudo crear período")
            return False
        
        print(f"✅ Período: {self.current_period.name}")
        
        # 2. Productos
        missing = []
        for product_name in self.REQUIRED_PRODUCTS:
            product = self.session.exec(
                select(Products).where(Products.product_name == product_name)
            ).first()
            
            if product:
                self.products_map[product_name] = product
            else:
                missing.append(product_name)
        
        if missing:
            print(f"❌ Productos faltantes: {', '.join(missing)}")
            return False
        
        print(f"✅ {len(self.REQUIRED_PRODUCTS)} productos encontrados")
        
        # 3. Rango default
        self.default_rank = self.session.exec(
            select(Ranks).where(Ranks.name == "Sin rango")
        ).first()
        
        if not self.default_rank:
            print("❌ Rango 'Sin rango' no encontrado")
            return False
        
        print(f"✅ Rango default: {self.default_rank.name}")
        
        # 4. Obtener próximo member_id
        max_member_id = self.session.exec(select(func.max(Users.member_id))).one()
        self.next_member_id = (max_member_id or 0) + 1
        print(f"✅ Próximo member_id: {self.next_member_id}")
        
        return True
    
    def _create_binary_tree(self) -> bool:
        """
        Crea árbol binario (2x2) usando BFS.
        Cada usuario tiene EXACTAMENTE 2 referidos directos.
        """
        try:
            queue = []  # Cola BFS: [(member_id, level)]
            
            # Usuario raíz (sin sponsor)
            root = self._create_complete_user(
                member_id=self.next_member_id,
                sponsor_id=None,
                level=0
            )
            queue.append((root.member_id, 0))
            self.created_users += 1
            
            print(f"   ✅ Usuario raíz: member_id={root.member_id}")
            
            # Crear resto de usuarios (BFS)
            while self.created_users < self.TOTAL_USERS and queue:
                sponsor_id, level = queue.pop(0)
                
                # Crear EXACTAMENTE 2 hijos (2x2)
                for child_num in range(2):
                    if self.created_users >= self.TOTAL_USERS:
                        break
                    
                    new_member_id = self.next_member_id + self.created_users
                    new_user = self._create_complete_user(
                        member_id=new_member_id,
                        sponsor_id=sponsor_id,
                        level=level + 1
                    )
                    
                    queue.append((new_user.member_id, level + 1))
                    self.created_users += 1
                    
                    # Commit en lotes para performance
                    if self.created_users % self.COMMIT_BATCH_SIZE == 0:
                        self.session.commit()
                        print(f"   [{self.created_users}/{self.TOTAL_USERS}] Guardado lote...")
            
            # Flush final antes de commit
            self.session.flush()
            print(f"\n✅ {self.created_users} usuarios creados")
            return True
            
        except Exception as e:
            print(f"❌ Error creando árbol: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _create_complete_user(
        self,
        member_id: int,
        sponsor_id: Optional[int],
        level: int
    ) -> Users:
        """
        Crea usuario con TODOS los datos requeridos:
        1. users
        2. userprofiles
        3. users_addresses
        4. usertreepaths
        5. wallets
        6. user_rank_history
        7. orders (1 completada)
        """
        # 1. USERS
        first_name = f"Test{member_id}"
        last_name = f"User{level}"
        email = f"test{member_id}@nnprotect.local"
        country = random.choice(self.COUNTRIES)
        
        user = Users(
            member_id=member_id,
            sponsor_id=sponsor_id,
            first_name=first_name,
            last_name=last_name,
            email_cache=email,
            country_cache=country,
            status=UserStatus.NO_QUALIFIED,
            pv_cache=0,
            pvg_cache=0,
            created_at=datetime.now(timezone.utc)
        )
        self.session.add(user)
        self.session.flush()  # Obtener user.id
        
        # 2. USERPROFILES
        profile = UserProfiles(
            user_id=user.id,
            gender=random.choice([UserGender.MALE, UserGender.FEMALE]),
            phone_number=f"+52{random.randint(1000000000, 9999999999)}",
            date_of_birth=date(1990, 1, 1),
            bio=""
        )
        self.session.add(profile)
        
        # 3. ADDRESSES + USERS_ADDRESSES
        address = Addresses(
            country=country,
            state=f"Estado{level}",
            city=f"Ciudad{member_id}",
            zip_code=f"{random.randint(10000, 99999)}",
            street=f"Calle {random.randint(1, 1000)}",
            neighborhood=f"Colonia{member_id}"
        )
        self.session.add(address)
        self.session.flush()  # Obtener address.id
        
        user_address = UserAddresses(
            user_id=user.id,
            address_id=address.id,
            address_name="Casa",
            is_default=True
        )
        self.session.add(user_address)
        
        # 4. USERTREEPATHS
        if sponsor_id is None:
            # Usuario raíz: solo auto-referencia (sin sponsor_id ya que es opcional)
            self_path = UserTreePath(
                ancestor_id=member_id,
                descendant_id=member_id,
                depth=0
            )
            self.session.add(self_path)
            self.created_tree_paths += 1
        else:
            # Usuario con sponsor: copiar árbol del sponsor + agregar sponsor directo
            # Auto-referencia
            self_path = UserTreePath(
                sponsor_id=sponsor_id,
                ancestor_id=member_id,
                descendant_id=member_id,
                depth=0
            )
            self.session.add(self_path)
            self.created_tree_paths += 1
            
            # Copiar ancestros del sponsor
            sponsor_ancestors = self.session.exec(
                select(UserTreePath).where(UserTreePath.descendant_id == sponsor_id)
            ).all()
            
            for ancestor_path in sponsor_ancestors:
                new_path = UserTreePath(
                    sponsor_id=sponsor_id,
                    ancestor_id=ancestor_path.ancestor_id,
                    descendant_id=member_id,
                    depth=ancestor_path.depth + 1
                )
                self.session.add(new_path)
                self.created_tree_paths += 1
        
        # 5. WALLETS
        currency = self._get_currency(country)
        wallet = Wallets(
            member_id=member_id,
            balance=0.0,
            currency=currency,
            status=WalletStatus.ACTIVE.value,
            created_at=datetime.now(timezone.utc)
        )
        self.session.add(wallet)
        self.created_wallets += 1
        
        # 6. USER_RANK_HISTORY
        rank_history = UserRankHistory(
            member_id=member_id,
            rank_id=self.default_rank.id,
            achieved_on=datetime.now(timezone.utc),
            period_id=self.current_period.id
        )
        self.session.add(rank_history)
        self.created_rank_history += 1
        
        # 7. ORDERS (1 completada)
        self._create_order(user, country)
        
        return user
    
    def _create_order(self, user: Users, country: str):
        """Crea 1 orden completada con 5 productos."""
        currency = self._get_currency(country)
        
        order = Orders(
            member_id=user.member_id,
            country=country,
            currency=currency,
            subtotal=0.0,
            shipping_cost=100.0,
            tax=0.0,
            discount=0.0,
            total=0.0,
            total_pv=0,
            total_vn=0.0,
            status=OrderStatus.PAYMENT_CONFIRMED.value,
            created_at=datetime.now(timezone.utc),
            payment_confirmed_at=datetime.now(timezone.utc),
            period_id=self.current_period.id if self.current_period else None,
            payment_method="wallet"
        )
        self.session.add(order)
        self.session.flush()  # Obtener order.id
        
        # Agregar 5 productos
        subtotal = 0.0
        total_pv = 0
        total_vn = 0.0
        
        for product_name in self.REQUIRED_PRODUCTS:
            product = self.products_map[product_name]
            
            unit_price = self._get_price(product, country)
            unit_pv = self._get_pv(product, country)
            unit_vn = self._get_vn(product, country)
            
            order_item = OrderItems(
                order_id=order.id,
                product_id=product.id,
                quantity=1,
                unit_price=unit_price,
                unit_pv=unit_pv,
                unit_vn=unit_vn,
                line_total=unit_price,
                line_pv=unit_pv,
                line_vn=unit_vn
            )
            self.session.add(order_item)
            
            subtotal += unit_price
            total_pv += unit_pv
            total_vn += unit_vn
        
        order.subtotal = subtotal
        order.total = subtotal + order.shipping_cost
        order.total_pv = total_pv
        order.total_vn = total_vn
        
        self.created_orders += 1
    
    def _get_currency(self, country: str) -> str:
        """Retorna moneda según país."""
        mapping = {
            "México": "MXN",
            "USA": "USD",
            "Colombia": "COP",
            "República Dominicana": "DOP"
        }
        return mapping.get(country, "MXN")
    
    def _get_price(self, product: Products, country: str) -> float:
        """Obtiene precio según país."""
        if country == "México":
            return product.price_mx or 0.0
        elif country == "USA":
            return product.price_usa or 0.0
        elif country == "Colombia":
            return product.price_colombia or 0.0
        return product.price_mx or 0.0
    
    def _get_pv(self, product: Products, country: str) -> int:
        """Obtiene PV según país."""
        if country == "México":
            return product.pv_mx or 0
        elif country == "USA":
            return product.pv_usa or 0
        elif country == "Colombia":
            return product.pv_colombia or 0
        return product.pv_mx or 0
    
    def _get_vn(self, product: Products, country: str) -> float:
        """Obtiene VN según país."""
        if country == "México":
            return product.vn_mx or 0.0
        elif country == "USA":
            return product.vn_usa or 0.0
        elif country == "Colombia":
            return product.vn_colombia or 0.0
        return product.vn_mx or 0.0
    
    def _print_report(self):
        """Imprime reporte final."""
        print("\n" + "=" * 80)
        print("  REPORTE FINAL")
        print("=" * 80)
        print(f"\n✅ Usuarios creados: {self.created_users}")
        print(f"✅ Wallets creadas: {self.created_wallets}")
        print(f"✅ Rank history creados: {self.created_rank_history}")
        print(f"✅ Tree paths creados: {self.created_tree_paths}")
        print(f"✅ Órdenes creadas: {self.created_orders}")
        
        if self.current_period:
            print(f"\nPeríodo: {self.current_period.name}")
        print(f"Estructura: Árbol binario 2x2")
        print("\n" + "=" * 80)


def main():
    """Punto de entrada."""
    print("\n🚀 Iniciando seed MLM 2x2...\n")
    
    try:
        with rx.session() as session:
            seeder = MLMSeeder2x2(session)
            success = seeder.run()
            
            if success:
                print("\n✅ COMPLETADO EXITOSAMENTE\n")
                return 0
            else:
                print("\n❌ FALLÓ\n")
                return 1
    
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrumpido por usuario\n")
        return 2
    
    except Exception as e:
        print(f"\n❌ ERROR FATAL: {e}")
        import traceback
        traceback.print_exc()
        return 3


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
