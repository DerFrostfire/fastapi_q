import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import pytest

from src.main import app
from src.auth.auth import auth
from src.config import setting

import httpx 

from fastapi.testclient import TestClient
from fastapi import HTTPException
from aiohttp import ClientError

class TestAuth:
    api_key = setting.TEST_TOKEN 
    _URL_QUNIQ = setting.URL_UNIQUE

    class MockResponse:
        def __init__(self, status, json_data={}):
            self.status = status
            self.json_data = json_data
        async def __aenter__(self):
            return self
        async def __aexit__(self, exc_type, exc, tb):
            pass
        async def json(self):
            return self.json_data

    @pytest.mark.asyncio
    async def test_get_user_id_and_name_api(self, mocker):
        
        def mocked_get(url, headers, timeout):
            return self.MockResponse(status=200, json_data={"id": 8})

        mocker.patch("src.auth.auth.aiohttp.ClientSession.get", side_effect=mocked_get)
        response = await auth.get_user_id_and_name_api()

        assert response == {'quniq_id': 8}

    @pytest.mark.asyncio
    @pytest.mark.parametrize("mocked_response", [
        ({}), 
    ])
    async def test_get_user_id_and_name_api_auth_error(self, mocker, mocked_response):
        def mocked_get(url, headers, timeout):
            return self.MockResponse(status=200, json_data=mocked_response)
        mocker.patch("src.auth.auth.aiohttp.ClientSession.get", side_effect=mocked_get)

        with pytest.raises(HTTPException) as exception:
            response = await auth.get_user_id_and_name_api()
            assert response == None
        assert exception.value.status_code == 401
        assert exception.value.detail == "Ошибка аутентификации"
    

    # поведение функции при ошибках TimeoutError и ClientError
    @pytest.mark.asyncio
    @pytest.mark.parametrize("mocked_error_response", [
        ({"error": TimeoutError, "error_message": "нет подключения к серверу", "status": 500}),         
        ({"error": ClientError("Client Error"), "error_message": "Client Error", "status": 500})
    ])
    async def test_get_user_id_and_name_api_timeout(self, mocker, mocked_error_response):
        error = mocked_error_response["error"]
        error_message = mocked_error_response["error_message"]
        status = mocked_error_response["status"]

        def mocked_get(url, headers, timeout, error=error):
            raise error

        mocker.patch("src.auth.auth.aiohttp.ClientSession.get", side_effect=mocked_get)

        with pytest.raises(HTTPException) as exception:
            response = await auth.get_user_id_and_name_api()
            assert response == None
        assert exception.value.status_code == status
        assert exception.value.detail == error_message
    
    # поведение функции при ответе отличным от 200
    @pytest.mark.asyncio
    @pytest.mark.parametrize("mocked_status", [
        100, 201, 301, 400, 500
    ])
    async def test_get_user_id_and_name_api_external_error(self, mocker, mocked_status):
        status = mocked_status
        def mocked_get(url, headers, timeout, status=status):
            return self.MockResponse(status=status)
        mocker.patch("src.auth.auth.aiohttp.ClientSession.get")

        with pytest.raises(HTTPException) as exception:
            response = await auth.get_user_id_and_name_api()
            assert response == None
        
        assert exception.value.detail == "Ошибка при обращении к серверу"