from .singleton import Singleton


class Interpolation:
    LINEAR = 0
    EASE_IN = 1
    EASE_OUT = 2
    EASE_IN_OUT = 3

    def __init__(
        self, obj, attr, start, end, duration, easing_mode=LINEAR, floating_point=False
    ):
        self.obj = obj
        self.attr = attr
        self.start = start
        self.end = end
        self.duration = duration
        self.easing_mode = easing_mode
        self.elapsed_time = 0
        self.floating_point = floating_point

    def update(self, delta_time):
        self.elapsed_time += delta_time
        t = self.elapsed_time / self.duration
        if self.elapsed_time >= self.duration:
            t = 1

        if self.easing_mode == self.LINEAR:
            value = self.start + (self.end - self.start) * t
        elif self.easing_mode == self.EASE_IN:
            value = self.start + (self.end - self.start) * t * t
        elif self.easing_mode == self.EASE_OUT:
            value = self.start + (self.end - self.start) * (1 - (1 - t) * (1 - t))
        elif self.easing_mode == self.EASE_IN_OUT:
            if t < 0.5:
                value = self.start + (self.end - self.start) / 2 * t * t * 2
            else:
                value = (
                    self.start
                    + (self.end - self.start)
                    / 2
                    * (1 - (1 - (t * 2 - 1)) * (1 - (t * 2 - 1)))
                    + (self.end - self.start) / 2
                )

        setattr(self.obj, self.attr, value if self.floating_point else int(value))
        return t != 1


class InterpolationManager(metaclass=Singleton):

    def __init__(self):
        self.interpolations = []

    def add_interpolation(self, interpolation):
        interpolation.elapsed_time = 0
        self.interpolations.append(interpolation)

    def remove_interpolation(self, interpolation):
        self.interpolations.remove(interpolation)

    def update(self, delta_time):
        self.interpolations = [
            interpolation
            for interpolation in self.interpolations
            if interpolation.update(delta_time)
        ]
