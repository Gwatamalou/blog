# import pytest
# from unittest.mock import MagicMock, AsyncMock
# from fastapi.testclient import TestClient
#
# import src.services
# from src.app import app
# from src.depends import get_authentication_service, get_session, get_users_service
#
#
#
# @pytest.fixture
# def mock_users_service():
#     mock_service = AsyncMock()
#     return mock_service
#
#
# @pytest.fixture
# def mock_authentication_service():
#     mock_service = AsyncMock()
#     return mock_service
#
#
# @pytest.fixture
# def mock_session():
#     mock_session = AsyncMock()
#     return mock_session
#
#
# @pytest.mark.asyncio
# def test_user_users_all_success(mock_users_service, mock_authentication_service, mock_session, monkeypatch):
#     app.dependency_overrides[get_session] = lambda: mock_session
#     app.dependency_overrides[get_authentication_service] = lambda: mock_authentication_service
#     app.dependency_overrides[get_users_service] = lambda: mock_users_service
#
#
#     mock_users_service.get_users.return_value = [
#         {
#             "name": "testuser1",
#             "email": "testuser1@example.com",
#             "uuid": "c846b311-23cb-4a61-a96a-bd48e39402e1",
#             "role": "user",
#             "created_at": "2025-01-26T18:39:00",
#             "deleted_at": None
#         },
#         {
#             "name": "testuser2",
#             "email": "testuser2@example.com",
#             "uuid": "c846b311-23cb-4a61-a96a-bd48e39402e1",
#             "role": "user",
#             "created_at": "2025-01-26T18:39:00",
#             "deleted_at": None
#         },
#         {
#             "name": "testuser3",
#             "email": "testuser3@example.com",
#             "uuid": "c846b311-23cb-4a61-a96a-bd48e39402e1",
#             "role": "user",
#             "created_at": "2025-01-26T18:39:00",
#             "deleted_at": None
#         }
#     ]
#
#     monkeypatch.setattr("src.services.auth.AuthorizationService.require_role", lambda x: lambda f: f)
#
#     client = TestClient(app)
#     response = client.get("/users/users/all", headers={"x_access_token": "valid-token"})
#
#     app.dependency_overrides = {}
#
#     assert response.status_code == 200
