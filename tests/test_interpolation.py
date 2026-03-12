from battle_engine.interpolation import Interpolation, InterpolationManager
from battle_engine.singleton import Singleton


def setup_function():
    Singleton._instances.pop(InterpolationManager, None)


class Target:
    def __init__(self):
        self.x = 0


def test_linear_interpolation_start():
    target = Target()
    interp = Interpolation(target, "x", 0, 100, 1000, Interpolation.LINEAR)
    # At t=0, value should stay at start
    still_running = interp.update(0)
    assert target.x == 0
    assert still_running


def test_linear_interpolation_end():
    target = Target()
    interp = Interpolation(target, "x", 0, 100, 1000, Interpolation.LINEAR)
    still_running = interp.update(1000)
    assert target.x == 100
    assert not still_running


def test_linear_interpolation_midpoint():
    target = Target()
    interp = Interpolation(target, "x", 0, 100, 1000, Interpolation.LINEAR)
    interp.update(500)
    assert target.x == 50


def test_ease_in():
    target = Target()
    interp = Interpolation(target, "x", 0, 100, 1000, Interpolation.EASE_IN)
    interp.update(500)
    # Ease-in at midpoint: 0.5^2 = 0.25 -> value = 25
    assert target.x == 25


def test_ease_out():
    target = Target()
    interp = Interpolation(target, "x", 0, 100, 1000, Interpolation.EASE_OUT)
    interp.update(500)
    # Ease-out at midpoint: 1 - (1 - 0.5)^2 = 0.75 -> value = 75
    assert target.x == 75


def test_floating_point_mode():
    target = Target()
    interp = Interpolation(
        target, "x", 0, 100, 1000, Interpolation.LINEAR, floating_point=True
    )
    interp.update(333)
    assert isinstance(target.x, float)
    assert abs(target.x - 33.3) < 0.1


def test_manager_updates_and_removes():
    manager = InterpolationManager()
    target = Target()
    interp = Interpolation(target, "x", 0, 100, 1000, Interpolation.LINEAR)
    manager.add_interpolation(interp)
    assert len(manager.interpolations) == 1

    manager.update(1000)
    assert target.x == 100
    # Completed interpolations are removed
    assert len(manager.interpolations) == 0
