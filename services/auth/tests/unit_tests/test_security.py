import pytest
from src.core.security import create_access_token, decode_token

@pytest.mark.parametrize("sub", ["10", "test_user"])
def test_create_and_decode_token(sub):
    # Создаем токен
    token = create_access_token(sub=sub)
    assert isinstance(token, str)
    
    # Декодируем
    payload = decode_token(token)
    assert payload["sub"] == sub
    assert payload["type"] == "access"
    assert "exp" in payload

def test_token_expiration():
    # Проверка, что exp устанавливается
    token = create_access_token(sub="123", expires_delta_minutes=10)
    payload = decode_token(token)
    assert payload["exp"] is not None