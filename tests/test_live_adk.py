import asyncio

from vetpivot.live_adk import _create_session, _create_session_async


class SyncSessionService:
    def __init__(self):
        self.created = None

    def create_session(self, *, app_name: str, user_id: str, session_id: str):
        self.created = {
            "app_name": app_name,
            "user_id": user_id,
            "session_id": session_id,
        }


class AsyncSessionService:
    def __init__(self):
        self.created = None

    async def create_session(self, *, app_name: str, user_id: str, session_id: str):
        self.created = {
            "app_name": app_name,
            "user_id": user_id,
            "session_id": session_id,
        }


def test_create_session_supports_sync_adk_api():
    service = SyncSessionService()

    _create_session(service, app_name="app", user_id="user", session_id="session")

    assert service.created == {
        "app_name": "app",
        "user_id": "user",
        "session_id": "session",
    }


def test_create_session_supports_async_adk_api():
    service = AsyncSessionService()

    _create_session(service, app_name="app", user_id="user", session_id="session")

    assert service.created == {
        "app_name": "app",
        "user_id": "user",
        "session_id": "session",
    }


def test_create_session_async_supports_sync_adk_api():
    service = SyncSessionService()

    asyncio.run(_create_session_async(service, app_name="app", user_id="user", session_id="session"))

    assert service.created == {
        "app_name": "app",
        "user_id": "user",
        "session_id": "session",
    }


def test_create_session_async_supports_async_adk_api():
    service = AsyncSessionService()

    asyncio.run(_create_session_async(service, app_name="app", user_id="user", session_id="session"))

    assert service.created == {
        "app_name": "app",
        "user_id": "user",
        "session_id": "session",
    }
