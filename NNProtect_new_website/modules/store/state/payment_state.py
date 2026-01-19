import reflex as rx

import sqlmodel
from typing import Optional
from datetime import datetime, timezone

from database.orders import Orders, OrderStatus
from database.order_items import OrderItems


from .store_state import CountProducts
from NNProtect_new_website.modules.auth.state.auth_state import AuthState
from ..backend.payment_service import PaymentService


class PaymentState(rx.State):
    """
    Estado para la gestión del proceso de pago.
    Maneja la selección de método de pago y la confirmación de compra.
    """
    
    # Método de pago seleccionado (wallet, stripe, oxxo)
    payment_method: str = "wallet"
    
    # Estado de procesamiento
    is_processing: bool = False
    
    # CEDIS seleccionado (si aplica)
    selected_cedis_id: Optional[int] = None
    
    # Resultado del proceso de pago
    order_result: Optional[dict] = None
    
    # Mensajes de error
    error_message: str = ""
    success_message: str = ""

    @rx.event
    def select_payment_method(self, method: str):
        """Actualiza el método de pago seleccionado."""
        self.payment_method = method
        self.error_message = ""

    @rx.event
    async def confirm_payment(self):
        """
        Confirma el pago y crea la orden con sus items.
        Flujo:
        1. Validar que hay productos en el carrito
        2. Obtener datos del usuario autenticado
        3. Crear orden con status PENDING_PAYMENT
        4. Crear order_items para cada producto del carrito
        5. Llamar al PaymentService para procesar el pago
        6. Manejar resultado (success/error)
        """
        print("\n" + "="*80)
        print("🔄 INICIANDO PROCESO DE CONFIRMACIÓN DE PAGO")
        print("="*80)
        
        self.is_processing = True
        self.error_message = ""
        self.success_message = ""
        
        try:
            print("📝 Paso 1: Obteniendo estado del carrito...")
            # Obtener estado del carrito
            cart_state = await self.get_state(CountProducts)
            print(f"   ✓ Estado del carrito obtenido")
            print(f"   📦 Productos en carrito: {cart_state.cart_items}")
            print(f"   🔢 Total de items: {cart_state.cart_total}")
            
            # Validar que hay productos en el carrito
            if not cart_state.cart_items or cart_state.cart_total == 0:
                print("   ❌ ERROR: Carrito vacío")
                self.error_message = "El carrito está vacío. Agrega productos antes de confirmar el pago."
                self.is_processing = False
                return
            
            print(f"   ✅ Carrito válido con {cart_state.cart_total} productos")
            
            print("\n👤 Paso 2: Obteniendo datos del usuario...")
            # Obtener datos del usuario
            auth_state = await self.get_state(AuthState)
            print(f"   ✓ Estado de autenticación obtenido")
            print(f"   🔐 Usuario autenticado: {auth_state.is_logged_in}")
            
            if not auth_state.is_logged_in or not auth_state.profile_data:
                print("   ❌ ERROR: Usuario no autenticado o sin datos de perfil")
                self.error_message = "Debes iniciar sesión para realizar una compra."
                self.is_processing = False
                return
            
            # Obtener member_id del usuario
            member_id = auth_state.profile_data.get("member_id")
            country = auth_state.profile_data.get("country", "MX")
            print(f"   📋 Member ID: {member_id}")
            print(f"   🌎 País: {country}")
            
            if not member_id:
                print("   ❌ ERROR: No se pudo obtener member_id")
                self.error_message = "No se pudo obtener la información del usuario."
                self.is_processing = False
                return
            
            print(f"   ✅ Datos de usuario válidos")
            
            print("\n💰 Paso 3: Calculando totales...")
            # Obtener moneda según país
            currency_map = {
                "MX": "MXN",
                "US": "USD",
                "CO": "COP"
            }
            currency = currency_map.get(country, "MXN")
            print(f"   💵 Moneda: {currency}")
            
            # Calcular totales del carrito
            subtotal = cart_state.cart_subtotal
            shipping_cost = cart_state.cart_shipping_cost
            total_pv = cart_state.cart_volume_points
            total = subtotal + shipping_cost
            
            print(f"   📊 Subtotal: ${subtotal:.2f}")
            print(f"   🚚 Envío: ${shipping_cost:.2f}")
            print(f"   📈 Puntos PV: {total_pv}")
            print(f"   💳 Total: ${total:.2f}")
            
            print("\n🗄️  Paso 4: Creando orden en la base de datos...")
            # Crear orden en la base de datos
            with rx.session() as session:
                print("   ✓ Sesión de base de datos abierta")
                
                print("   📝 Creando orden con status PENDING_PAYMENT...")
                # Crear orden con status PENDING_PAYMENT
                new_order = Orders(
                    member_id=member_id,
                    country=country,
                    currency=currency,
                    subtotal=subtotal,
                    shipping_cost=shipping_cost,
                    tax=0.0,
                    discount=0.0,
                    total=total,
                    total_pv=total_pv,
                    total_vn=total,  # VN = total en moneda local
                    status=OrderStatus.PENDING_PAYMENT.value,
                    payment_method=self.payment_method,
                    submitted_at=datetime.now(timezone.utc)
                )
                print(f"   ✓ Objeto Orders creado")
                print(f"   💳 Método de pago: {self.payment_method}")
                
                session.add(new_order)
                print("   ✓ Orden agregada a la sesión")
                
                session.commit()  # Commit para obtener el order_id
                print("   ✓ Commit realizado")
                
                session.refresh(new_order)
                print("   ✓ Orden refrescada")
                
                # Verificar que se obtuvo el order_id
                if new_order.id is None:
                    print("   ❌ ERROR: No se obtuvo order_id después del commit")
                    self.error_message = "Error al crear la orden en la base de datos."
                    self.is_processing = False
                    return
                
                order_id = new_order.id
                print(f"   ✅ Orden creada con ID: {order_id}")
                
                print("\n📦 Paso 5: Creando order_items...")
                # Crear order_items para cada producto del carrito
                cart_items_detailed = cart_state.cart_items_detailed
                print(f"   📋 Productos a procesar: {len(cart_items_detailed)}")
                
                for idx, cart_item in enumerate(cart_items_detailed, 1):
                    print(f"   → Item {idx}/{len(cart_items_detailed)}: {cart_item.get('name', 'N/A')}")
                    order_item = OrderItems(
                        order_id=order_id,
                        product_id=cart_item["id"],
                        quantity=cart_item["quantity"],
                        unit_price=cart_item["price"],
                        unit_pv=cart_item["volume_points"],
                        unit_vn=cart_item["price"]  # VN = precio unitario
                    )
                    print(f"     • Qty: {cart_item['quantity']}, Precio: ${cart_item['price']:.2f}, PV: {cart_item['volume_points']}")
                    
                    # Calcular totales de la línea
                    order_item.calculate_totals()
                    print(f"     • Totales calculados: ${order_item.line_total:.2f}, {order_item.line_pv} PV")
                    
                    session.add(order_item)
                
                print("   ✓ Todos los order_items agregados")
                session.commit()
                print("   ✅ Order_items guardados en BD")
                
                print("\n💳 Paso 6: Procesando pago...")
                print(f"   🎯 Método seleccionado: {self.payment_method}")
                
                # Procesar pago según método seleccionado
                if self.payment_method == "wallet":
                    print("   💰 Iniciando pago con billetera...")
                    print(f"   📝 Parámetros: order_id={order_id}, member_id={member_id}")
                    
                    # Llamar al PaymentService para procesar el pago con wallet
                    payment_result = PaymentService.process_wallet_payment(
                        session=session,
                        order_id=order_id,
                        member_id=member_id
                    )
                    
                    print(f"   ✓ PaymentService ejecutado")
                    print(f"   📊 Resultado: {payment_result}")
                    
                    # Manejar resultado
                    if payment_result["success"]:
                        print("   ✅ ¡PAGO EXITOSO!")
                        print(f"   💬 Mensaje: {payment_result['message']}")
                        
                        self.success_message = payment_result["message"]
                        self.order_result = payment_result
                        
                        print("\n📊 Paso 7: Actualizando UnilevelReports para usuario y ancestros...")
                        try:
                            from NNProtect_new_website.modules.network.backend.mlm_user_manager import MLMUserManager
                            from database.periods import Periods
                            from sqlmodel import desc
                            
                            # Obtener período actual
                            current_period = session.exec(
                                sqlmodel.select(Periods).order_by(desc(Periods.starts_on)).limit(1)
                            ).first()
                            
                            if not current_period:
                                print("   ⚠️  No se encontró período actual")
                            else:
                                print(f"   ✓ Período actual: {current_period.name} (ID={current_period.id})")
                                print(f"   🔄 Llamando a update_unilevel_report_for_order...")
                                
                                # Llamar al método que actualiza PV del comprador Y PVG de todos los ancestros por nivel
                                MLMUserManager.update_unilevel_report_for_order(
                                    order_member_id=member_id,
                                    period_id=current_period.id
                                )
                                
                                print("   ✅ UnilevelReports actualizado para usuario y todos los ancestros")
                                    
                        except Exception as e_unilevel:
                            print(f"   ⚠️  Error actualizando UnilevelReports: {e_unilevel}")
                            import traceback
                            traceback.print_exc()
                            # No fallar el proceso si esto falla
                        
                        print("\n   🧹 Limpiando carrito...")
                        # Limpiar carrito
                        cart_state.clear_cart()
                        print("   ✓ Carrito limpio")
                        
                        # Redirigir a página de confirmación
                        print("   🔄 Redirigiendo a /order_confirmation...")
                        self.is_processing = False
                        
                        print("="*80)
                        print("✅ PROCESO COMPLETADO EXITOSAMENTE")
                        print("="*80 + "\n")
                        
                        return rx.redirect("/order_confirmation")
                    else:
                        print("   ❌ PAGO FALLIDO")
                        print(f"   💬 Mensaje de error: {payment_result['message']}")
                        
                        self.error_message = payment_result["message"]
                        
                        print("   🚫 Cancelando orden...")
                        # Si el pago falló, actualizar el estado de la orden a CANCELLED
                        new_order.status = OrderStatus.CANCELLED.value
                        session.commit()
                        print("   ✓ Orden cancelada")
                        
                else:
                    print(f"   ⚠️  Método '{self.payment_method}' no implementado")
                    # Otros métodos de pago (stripe, oxxo) - próximamente
                    self.error_message = f"El método de pago '{self.payment_method}' aún no está disponible."
                    
                    print("   🚫 Cancelando orden...")
                    # Cancelar orden
                    new_order.status = OrderStatus.CANCELLED.value
                    session.commit()
                    print("   ✓ Orden cancelada")
        
        except Exception as e:
            print("\n" + "="*80)
            print("❌ ERROR EN EL PROCESO")
            print("="*80)
            print(f"🔥 Exception: {type(e).__name__}")
            print(f"💬 Mensaje: {str(e)}")
            print(f"📍 Traceback:")
            import traceback
            traceback.print_exc()
            print("="*80 + "\n")
            
            self.error_message = f"Error al procesar el pago: {str(e)}"
        
        finally:
            self.is_processing = False
            print(f"🏁 Finalizando... is_processing = {self.is_processing}\n")