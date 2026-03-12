from battle_engine.singleton import Singleton


class DummySingleton(metaclass=Singleton):
    def __init__(self, value=0):
        self.value = value


def setup_function():
    """Clear singleton instances between tests."""
    Singleton._instances.pop(DummySingleton, None)


def test_returns_same_instance():
    a = DummySingleton(1)
    b = DummySingleton(2)
    assert a is b


def test_preserves_first_init():
    DummySingleton(42)
    second = DummySingleton(99)
    assert second.value == 42
