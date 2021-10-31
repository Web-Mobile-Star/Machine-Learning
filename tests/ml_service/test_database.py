from ml_service.database import SessionMakerSingleton


def test_session_maker_is_singleton(
    session_maker_singleton: SessionMakerSingleton,
):
    assert session_maker_singleton == SessionMakerSingleton()
