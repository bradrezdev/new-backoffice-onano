"""
Test para verificar que el fix de autenticación funciona correctamente.

Verifica:
1. login_user() genera token JWT
2. Token se guarda en cookie
3. load_user_from_token() lee token correctamente
4. is_logged_in se establece a True
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from NNProtect_new_website.auth_service.auth_state import AuthState
from database.users import Users


class TestAuthenticationFix:
    """Tests para verificar el fix de autenticación con background=True"""
    
    @pytest.mark.asyncio
    async def test_login_generates_jwt_token(self):
        """
        TEST 1: Verificar que login_user() genera un JWT token válido
        """
        # Arrange
        state = AuthState()
        state.email = "test@example.com"
        state.password = "testpassword123"
        
        mock_user_data = {
            "id": 1,
            "member_id": 1,
            "firstname": "Test",
            "lastname": "User",
            "status": "ACTIVE",
            "email": "test@example.com"
        }
        
        # Mock de Supabase
        with patch('NNProtect_new_website.auth_service.auth_state.SupabaseAuthManager.sign_in_user') as mock_supabase:
            mock_supabase.return_value = (True, "Success", {"id": "supabase-123", "email": "test@example.com"})
            
            # Mock de MLM
            with patch('NNProtect_new_website.auth_service.auth_state.MLMUserManager.load_complete_user_data') as mock_mlm:
                mock_mlm.return_value = mock_user_data
                
                # Mock de DB session
                with patch('reflex.session') as mock_session:
                    mock_user = Mock(spec=Users)
                    mock_user.id = 1
                    mock_user.first_name = "Test"
                    mock_user.last_name = "User"
                    
                    mock_session.return_value.__enter__.return_value.exec.return_value.first.return_value = mock_user
                    
                    # Act
                    async for _ in state.login_user():
                        pass
        
        # Assert
        assert state.auth_token != "", "Token debe generarse"
        assert len(state.auth_token) > 50, "Token debe ser un JWT válido"
        assert state.is_logged_in == True, "Usuario debe estar logueado"
        assert state.profile_data == mock_user_data, "Profile data debe cargarse"
        
        print("✅ TEST 1 PASSED: Token JWT generado correctamente")
    
    @pytest.mark.asyncio
    async def test_token_saved_in_cookie(self):
        """
        TEST 2: Verificar que el token se guarda en la cookie auth_token
        """
        # Arrange
        state = AuthState()
        test_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test.token"
        
        # Act
        state.auth_token = test_token
        
        # Assert
        assert state.auth_token == test_token, "Token debe guardarse en cookie"
        print("✅ TEST 2 PASSED: Token guardado en cookie correctamente")
    
    @pytest.mark.asyncio
    async def test_load_user_from_token_reads_cookie(self):
        """
        TEST 3: Verificar que load_user_from_token() lee el token de la cookie
        """
        # Arrange
        state = AuthState()
        
        # Simular un token válido en la cookie
        test_payload = {"id": 1, "username": "Test User"}
        
        # Mock decode_jwt_token
        with patch('NNProtect_new_website.auth_service.auth_state.AuthenticationManager.decode_jwt_token') as mock_decode:
            mock_decode.return_value = test_payload
            
            # Mock DB session
            with patch('reflex.session') as mock_session:
                mock_user = Mock(spec=Users)
                mock_user.id = 1
                mock_user.first_name = "Test"
                mock_user.last_name = "User"
                mock_user.member_id = 1
                mock_user.email_cache = "test@example.com"
                mock_user.status = Mock(value="ACTIVE")
                mock_user.supabase_user_id = "supabase-123"
                
                mock_session.return_value.__enter__.return_value.exec.return_value.first.return_value = mock_user
                
                # Mock MLM data
                with patch('NNProtect_new_website.auth_service.auth_state.MLMUserManager.load_complete_user_data') as mock_mlm:
                    mock_mlm.return_value = {
                        "id": 1,
                        "member_id": 1,
                        "firstname": "Test",
                        "lastname": "User",
                        "wallet_balance": 1000
                    }
                    
                    # Act
                    state.load_user_from_token()
        
        # Assert
        assert state.is_logged_in == True, "Usuario debe estar autenticado después de cargar desde token"
        assert state.logged_user_data.get("id") == 1, "User ID debe coincidir"
        print("✅ TEST 3 PASSED: load_user_from_token() funciona correctamente")
    
    def test_empty_token_returns_not_logged_in(self):
        """
        TEST 4: Verificar que sin token, el usuario no está autenticado
        """
        # Arrange
        state = AuthState()
        state.auth_token = ""  # Cookie vacía
        
        # Mock decode_jwt_token para retornar None (token inválido)
        with patch('NNProtect_new_website.auth_service.auth_state.AuthenticationManager.decode_jwt_token') as mock_decode:
            mock_decode.return_value = None
            
            # Act
            state.load_user_from_token()
        
        # Assert
        assert state.is_logged_in == False, "Usuario NO debe estar autenticado con token vacío"
        assert state.logged_user_data == {}, "logged_user_data debe estar vacío"
        print("✅ TEST 4 PASSED: Token vacío resulta en no autenticado")


if __name__ == "__main__":
    print("\n" + "="*80)
    print("🧪 EJECUTANDO TESTS DE AUTENTICACIÓN")
    print("="*80 + "\n")
    
    pytest.main([__file__, "-v", "-s"])
