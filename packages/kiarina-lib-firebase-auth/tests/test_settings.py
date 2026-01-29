from kiarina.lib.firebase.auth import FirebaseAuthSettings, settings_manager


def test_settings_manager():
    """Test that settings_manager is properly initialized."""
    assert settings_manager is not None
    assert settings_manager.settings_cls == FirebaseAuthSettings


def test_firebase_auth_settings():
    """Test FirebaseAuthSettings instantiation."""
    settings = FirebaseAuthSettings()
    assert settings is not None
