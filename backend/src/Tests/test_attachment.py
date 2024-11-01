# import sys
# import os

# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# import pytest
# from src.main import app
# from src.config import setting
# from src.auth.auth import auth
# from fastapi.testclient import TestClient

# async def override_auth_header_dependency():
#     return setting.TEST_TOKEN

# app.dependency_overrides[auth.api_key_header] = override_auth_header_dependency
