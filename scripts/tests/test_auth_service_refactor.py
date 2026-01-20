
import pytest
from unittest.mock import Mock, patch
from NNProtect_new_website.modules.auth.backend.auth_service import AuthService
from NNProtect_new_website.modules.auth.backend.user_data_service import UserDataService
from NNProtect_new_website.modules.network.backend.sponsor_service import SponsorService
from database.users import Users

class TestAuthServiceRefactor:
    
    def test_hash_and_verify_password(self):
        password = "securePassword123"
        hashed = AuthService.hash_password(password)
        
        assert hashed != password
        assert AuthService.verify_password(password, hashed) is True
        assert AuthService.verify_password("wrongPassword", hashed) is False

    def test_jwt_generation_and_decoding(self):
        mock_user = Mock(spec=Users)
        mock_user.id = 1
        mock_user.first_name = "Test"
        mock_user.last_name = "User"
        
        # Test Create
        token = AuthService.create_jwt_token(mock_user)
        assert isinstance(token, str)
        assert len(token) > 20
        
        # Test Decode
        decoded = AuthService.decode_jwt_token(token)
        assert decoded['id'] == 1
        assert decoded['username'] == "Test User"
        assert 'exp' in decoded

class TestUserDataServiceRefactor:
    
    def test_build_profile_name(self):
        assert UserDataService.build_profile_name("Juan Carlos", "Perez", "juanp") == "Juan Perez"
        assert UserDataService.build_profile_name("Juan", "", "juanp") == "Juan"
        assert UserDataService.build_profile_name("", "Perez", "juanp") == "Perez"
        assert UserDataService.build_profile_name("", "", "juanp") == "juanp"

if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
