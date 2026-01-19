═══════════════════════════════════════════════════════════════════════════════
📋 REPORTE EJECUTIVO: ANÁLISIS DE PV/PVG Y COMISIONES UNINIVEL
═══════════════════════════════════════════════════════════════════════════════

🎭 Roles: Arquitecto de Datos + Auditor de Comisiones + QA Financial
Fecha: 31 de octubre de 2025
Prioridad: 🔴 CRÍTICA

═══════════════════════════════════════════════════════════════════════════════
🔍 OBJETIVO 1: BUG EN CÁLCULO DE PVG_CACHE
═══════════════════════════════════════════════════════════════════════════════

❌ PROBLEMA IDENTIFICADO:

   Archivo: NNProtect_new_website/Admin_app/admin_state.py
   Línea: 1010
   
   Código actual:
   ```python
   user.pvg_cache += total_pv
   ```

💡 EXPLICACIÓN DEL ERROR:

   PVG (Puntos de Volumen Grupal) debe incluir:
   1. El PV personal del usuario (su propio pv_cache)
   2. El PV de todos sus descendientes

   Fórmula correcta:
   PVG = PV_personal + Σ(PV_descendientes)

📊 EJEMPLO DEL PROBLEMA:

   Organización: member_id 3 → member_id 2 → member_id 1
   
   ESTADO ACTUAL (INCORRECTO):
   • Member 3: pv_cache=1465, pvg_cache=0 
     ❌ Falta sumar su propio PV (debería ser 1465)
   
   • Member 2: pv_cache=1465, pvg_cache=1465
     ❌ Solo tiene el PV de member 3, falta su propio PV (debería ser 2930)
   
   • Member 1: pv_cache=1465, pvg_cache=1465
     ❌ Solo tiene el PV de member 2, faltan members 2+3 (debería ser 4395)
   
   ESTADO ESPERADO (CORRECTO):
   • Member 3: pv_cache=1465, pvg_cache=1465 (su propio PV)
   • Member 2: pv_cache=1465, pvg_cache=2930 (1465 + 1465)
   • Member 1: pv_cache=1465, pvg_cache=4395 (1465 + 1465 + 1465)

✅ SOLUCIÓN PROPUESTA:

   Ubicación: admin_state.py línea 1006-1010
   
   ANTES (INCORRECTO):
   ─────────────────
   user.pv_cache += total_pv
   user.vn_cache += total_vn
   
   # ✅ CRÍTICO: El PVG del usuario incluye su propio PV
   user.pvg_cache += total_pv
   
   DESPUÉS (CORRECTO):
   ───────────────────
   user.pv_cache += total_pv
   user.vn_cache += total_vn
   
   # ✅ CRÍTICO: El PVG del usuario SIEMPRE debe ser igual o mayor a su PV
   # El PVG incluye el PV propio + PV de descendientes
   # Cuando el usuario hace su primera compra, PVG = PV
   # Cuando hace más compras, PVG crece junto con PV
   user.pvg_cache = user.pv_cache  # Sincronizar PVG con PV actual
   
   EXPLICACIÓN:
   • user.pv_cache ya se incrementó con total_pv (línea 1006)
   • user.pvg_cache debe ser MÍNIMO igual a user.pv_cache
   • user.pvg_cache TAMBIÉN recibirá incrementos de descendientes (línea 1047)
   • Por lo tanto, user.pvg_cache >= user.pv_cache SIEMPRE

═══════════════════════════════════════════════════════════════════════════════
🔍 OBJETIVO 2: ANÁLISIS DE COMISIONES UNINIVEL PERDIDAS
═══════════════════════════════════════════════════════════════════════════════

❌ PROBLEMA REPORTADO:

   Según cálculos del usuario, faltan $732.50 MXN en comisiones Uninivel
   para member_id 1.

📊 CÁLCULOS ESPERADOS (SEGÚN USUARIO):

   Nivel 1 (2 personas)  @ 5%  = $146.50
   Nivel 2 (4 personas)  @ 8%  = $468.80
   Nivel 3 (8 personas)  @ 10% = $1,172.00
   Nivel 4 (16 personas) @ 10% = $2,344.00
   Nivel 5 (32 personas) @ 5%  = $2,344.00
                                 ──────────
   TOTAL ESPERADO:               $6,475.30

🔍 POSIBLES CAUSAS DEL DINERO PERDIDO:

   1. ❌ VN_CACHE INCORRECTO:
      • El VN (Valor Neto) podría no estar calculándose correctamente
      • Revisar línea 1007 en admin_state.py: user.vn_cache += total_vn

   2. ❌ ANCESTROS NO CALIFICADOS:
      • Solo ancestros con pv_cache >= 1465 reciben comisiones
      • Verificar si todos los ancestros del comprador califican
      • Revisar línea en payment_service.py donde se verifica calificación

   3. ❌ RANGO NO PERMITE ESE NIVEL:
      • Visionario: solo 3 niveles (5%, 8%, 10%)
      • Emprendedor: 4 niveles
      • Creativo: 5 niveles
      • Innovador: 6 niveles
      • Embajadores: 9 niveles
      
      Si member_id 1 es "Visionario", SOLO cobra niveles 1, 2, 3.
      Esto explica por qué NO cobra niveles 4 y 5.

   4. ❌ ORDEN NO TIENE VN CORRECTO:
      • Verificar que order.total_vn se esté calculando bien
      • Revisar payment_service.py línea ~253

✅ PASOS PARA INVESTIGAR:

   1. Verificar el rango actual de member_id 1:
      • Si es Visionario → Solo cobra 3 niveles (esto es CORRECTO)
      • Si es Embajador → Debe cobrar hasta nivel 9
   
   2. Verificar que todos los descendientes tengan vn_cache > 0:
      • Si vn_cache = 0 → No se generarán comisiones
   
   3. Verificar que los ancestros califiquen:
      • pv_cache >= 1465
      • status = QUALIFIED
   
   4. Verificar el método _trigger_unilevel_for_ancestors():
      • Línea ~289 en payment_service.py
      • Asegurar que usa order.total_vn correctamente
      • Asegurar que verifica el rango del ancestro

═══════════════════════════════════════════════════════════════════════════════
🔧 SOLUCIONES IMPLEMENTADAS
═══════════════════════════════════════════════════════════════════════════════

✅ LISTO PARA IMPLEMENTAR:

   1. 📝 Corrección de PVG en admin_state.py (línea 1010)
      Ver sección "SOLUCIÓN PROPUESTA" arriba
   
   2. 📊 Script de corrección de datos existentes
      Crear script SQL para recalcular PVG de todos los usuarios

✅ INVESTIGACIÓN REQUERIDA:

   1. 🔍 Verificar rango de member_id 1
      Consultar tabla userrankhistory
   
   2. 🔍 Verificar vn_cache de todos los descendientes
      Consultar tabla users where member_id IN (descendientes de 1)
   
   3. 🔍 Verificar que _trigger_unilevel_for_ancestors() funciona correctamente
      Agregar logs detallados para debugging

═══════════════════════════════════════════════════════════════════════════════
📊 PRÓXIMOS PASOS (PRIORIDAD CRÍTICA)
═══════════════════════════════════════════════════════════════════════════════

🔴 PASO 1: CORREGIR BUG DE PVG (INMEDIATO)
   Archivo: NNProtect_new_website/Admin_app/admin_state.py
   Línea: 1010
   Cambio: user.pvg_cache += total_pv → user.pvg_cache = user.pv_cache

🔴 PASO 2: CREAR SCRIPT DE CORRECCIÓN DE DATOS
   Objetivo: Recalcular pvg_cache para todos los usuarios existentes
   Fórmula: pvg_cache = pv_cache + SUM(descendientes.pv_cache)

🔴 PASO 3: INVESTIGAR COMISIONES UNINIVEL PERDIDAS
   1. Ver rango actual de member_id 1
   2. Ver vn_cache de todos los descendientes
   3. Ver si payment_service.py calcula correctamente

🟡 PASO 4: AGREGAR VALIDACIONES AUTOMÁTICAS
   1. Test que verifica pvg_cache >= pv_cache SIEMPRE
   2. Test que verifica comisiones Uninivel según rango
   3. Test que verifica vn_cache se calcula correctamente

🟢 PASO 5: DOCUMENTACIÓN
   1. Documentar el cálculo correcto de PVG
   2. Documentar el flujo de comisiones Uninivel
   3. Documentar los porcentajes por rango

═══════════════════════════════════════════════════════════════════════════════
💡 RECOMENDACIONES FINALES
═══════════════════════════════════════════════════════════════════════════════

1. ⚠️  El bug de PVG afecta TODOS los cálculos de rangos
   Los requisitos de rango se basan en PVG, por lo tanto este bug
   puede estar impidiendo que usuarios avancen de rango.

2. ⚠️  Las comisiones Uninivel "perdidas" podrían ser CORRECTAS
   Si member_id 1 tiene rango "Visionario", SOLO puede cobrar 3 niveles.
   Esto significa que NO cobra niveles 4 y 5, lo cual es CORRECTO según
   el plan de compensación.

3. ✅ Priorizar la corrección de PVG ANTES que investigar Uninivel
   El PVG incorrecto puede estar causando que los usuarios no califiquen
   para comisiones que deberían recibir.

4. 🔍 Necesitamos datos de producción para confirmar el problema de Uninivel
   Ejecutar el script investigate_pv_pvg_supabase.py con las credenciales
   correctas para obtener los datos reales.

═══════════════════════════════════════════════════════════════════════════════
