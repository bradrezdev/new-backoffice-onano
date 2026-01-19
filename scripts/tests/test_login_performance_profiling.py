"""
⏱️ TEST DE PROFILING: Login Performance

Objetivo: Medir tiempos exactos de cada fase del login para identificar bottleneck.

Instrucciones:
1. Modificar temporalmente auth_state.py para agregar métricas
2. Ejecutar reflex run
3. Hacer login
4. Analizar output con timestamps
"""

import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def generate_profiling_code():
    """
    Genera el código de profiling para agregar a login_user().
    """
    print("\n" + "╔" + "═"*78 + "╗")
    print("║" + " "*78 + "║")
    print("║" + "  ⏱️  CÓDIGO DE PROFILING PARA login_user()".center(78) + "║")
    print("║" + " "*78 + "║")
    print("╚" + "═"*78 + "╝\n")
    
    profiling_code = '''
# ⏱️ AGREGAR AL INICIO DE login_user() (después de línea 771):

import time
from datetime import datetime

def get_timestamp():
    """Helper para timestamps."""
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]

def measure_time(label):
    """Decorator para medir tiempo de ejecución."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start = time.time()
            print(f"⏱️  [{get_timestamp()}] {label} - INICIO")
            result = await func(*args, **kwargs)
            elapsed = time.time() - start
            print(f"✅ [{get_timestamp()}] {label} - COMPLETADO en {elapsed:.2f}s")
            return result
        return wrapper
    return decorator


# ⏱️ MODIFICAR login_user() PARA MEDIR CADA FASE:

@rx.event(background=True)
async def login_user(self):
    """Login híbrido con profiling."""
    
    # Timestamp de inicio
    t_start = time.time()
    print(f"\\n{'='*80}")
    print(f"⏱️  [{get_timestamp()}] LOGIN_USER - INICIO")
    print(f"{'='*80}\\n")
    
    async with self:
        self.is_loading = True
        self.error_message = ""
        yield
    
    t_after_init = time.time()
    print(f"⏱️  [{get_timestamp()}] Fase 0: Init state = {t_after_init - t_start:.3f}s")
    
    try:
        await asyncio.sleep(0.1)
        
        # Validación
        async with self:
            login_identifier = self.email or self.username
        
        if not login_identifier or not self.password:
            async with self:
                self.error_message = "El email y la contraseña no pueden estar vacíos."
                self.is_loading = False
            return
        
        # FASE 1: Supabase Authentication
        t_before_supabase = time.time()
        print(f"⏱️  [{get_timestamp()}] Fase 1: Supabase Auth - INICIO")
        
        success, message, supabase_user_data = await SupabaseAuthManager.sign_in_user(
            login_identifier, self.password
        )
        
        t_after_supabase = time.time()
        supabase_time = t_after_supabase - t_before_supabase
        print(f"✅ [{get_timestamp()}] Fase 1: Supabase Auth - COMPLETADO en {supabase_time:.3f}s")
        
        if not success or not supabase_user_data:
            async with self:
                self.error_message = message or "Credenciales incorrectas"
                self.is_loading = False
            return
        
        supabase_user_id = supabase_user_data.get('id')
        if not supabase_user_id:
            async with self:
                self.error_message = "Error al obtener ID de usuario de Supabase"
                self.is_loading = False
            return
        
        # FASE 2: Cargar datos MLM
        t_before_mlm = time.time()
        print(f"⏱️  [{get_timestamp()}] Fase 2: MLM Data Load - INICIO")
        
        try:
            complete_user_data = MLMUserManager.load_complete_user_data(supabase_user_id)
            
            t_after_mlm = time.time()
            mlm_time = t_after_mlm - t_before_mlm
            print(f"✅ [{get_timestamp()}] Fase 2: MLM Data Load - COMPLETADO en {mlm_time:.3f}s")
            
            if not complete_user_data:
                async with self:
                    self.error_message = "Usuario no encontrado en el sistema MLM"
                    self.is_loading = False
                return
            
            # FASE 3: Generar JWT Token
            t_before_jwt = time.time()
            print(f"⏱️  [{get_timestamp()}] Fase 3: JWT Generation - INICIO")
            
            with rx.session() as session:
                user = session.exec(
                    sqlmodel.select(Users).where(Users.id == complete_user_data["id"])
                ).first()
                
                if not user:
                    async with self:
                        self.error_message = "Error al obtener usuario para generar token"
                        self.is_loading = False
                    return
                
                token = AuthenticationManager.create_jwt_token(user)
            
            t_after_jwt = time.time()
            jwt_time = t_after_jwt - t_before_jwt
            print(f"✅ [{get_timestamp()}] Fase 3: JWT Generation - COMPLETADO en {jwt_time:.3f}s")
            
            # FASE 4: Establecer sesión
            t_before_session = time.time()
            print(f"⏱️  [{get_timestamp()}] Fase 4: Session Setup - INICIO")
            
            async with self:
                self.is_logged_in = True
                self.auth_token = token
                self.logged_user_data = {
                    "id": complete_user_data["id"],
                    "username": f"{complete_user_data['firstname']} {complete_user_data['lastname']}".strip(),
                    "email": supabase_user_data.get('email', ''),
                    "member_id": complete_user_data["member_id"],
                    "status": complete_user_data["status"],
                    "supabase_user_id": supabase_user_data.get('id'),
                }
                self.profile_data = complete_user_data
                self.is_loading = False
                yield rx.redirect("/dashboard")
            
            t_after_session = time.time()
            session_time = t_after_session - t_before_session
            print(f"✅ [{get_timestamp()}] Fase 4: Session Setup - COMPLETADO en {session_time:.3f}s")
            
            # RESUMEN
            t_end = time.time()
            total_time = t_end - t_start
            
            print(f"\\n{'='*80}")
            print(f"📊 RESUMEN DE TIEMPOS")
            print(f"{'='*80}")
            print(f"Fase 0 - Init:            {(t_after_init - t_start):.3f}s")
            print(f"Fase 1 - Supabase Auth:   {supabase_time:.3f}s ({supabase_time/total_time*100:.1f}%)")
            print(f"Fase 2 - MLM Data:        {mlm_time:.3f}s ({mlm_time/total_time*100:.1f}%)")
            print(f"Fase 3 - JWT:             {jwt_time:.3f}s ({jwt_time/total_time*100:.1f}%)")
            print(f"Fase 4 - Session:         {session_time:.3f}s ({session_time/total_time*100:.1f}%)")
            print(f"{'-'*80}")
            print(f"TOTAL:                    {total_time:.3f}s")
            print(f"{'='*80}\\n")
            
        except Exception as mlm_error:
            print(f"❌ Error cargando datos MLM: {mlm_error}")
            async with self:
                self.error_message = "Error cargando datos del usuario"
                self.is_loading = False
            return
    
    except Exception as e:
        print(f"❌ ERROR login híbrido: {e}")
        import traceback
        traceback.print_exc()
        async with self:
            self.error_message = "Error procesando login"
            self.is_loading = False
        return
'''
    
    print(profiling_code)
    print("\n" + "="*80)
    print("📋 INSTRUCCIONES:")
    print("="*80)
    print("1. Copiar el código de arriba")
    print("2. Reemplazar el método login_user() en auth_state.py")
    print("3. Ejecutar: reflex run")
    print("4. Hacer login")
    print("5. Observar output en terminal con timestamps detallados")
    print("6. Identificar fase más lenta")
    print("7. Optimizar esa fase específica")
    print("="*80 + "\n")
    
    print("🎯 TARGETS ESPERADOS:")
    print("   • Fase 1 (Supabase):  <2s  (actualmente: 5-10s ❌)")
    print("   • Fase 2 (MLM Data):  <1s  (actualmente: 2-5s ❌)")
    print("   • Fase 3 (JWT):       <0.1s (actualmente: <100ms ✅)")
    print("   • Fase 4 (Session):   <0.5s (actualmente: rápido ✅)")
    print("   • TOTAL:              <4s  (actualmente: 7-15s ❌)")
    print()


if __name__ == "__main__":
    print("\n⚠️  NOTA: Este script genera código de profiling.")
    print("No ejecuta el profiling directamente.")
    print("Necesitas aplicar el código manualmente a auth_state.py\\n")
    
    response = input("¿Generar código de profiling? (y/n): ")
    
    if response.lower() == 'y':
        generate_profiling_code()
    else:
        print("\\nCancelado. Para ejecutar más tarde, usa:")
        print("  python test_login_performance_profiling.py")
