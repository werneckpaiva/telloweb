import pygame
import threading
import time


def map(value, min_a, max_a, min_b, max_b):
    rate_value = abs(value - min_a) / (max_a - min_a)
    value_b = ((max_b - min_b) * rate_value) + min_b
    return round(value_b)


class PSController:

    tello = None
    joy = None

    joy_thread = None
    is_running = True

    axisValues = {}

    zero_limit_min = -5
    zero_limit_max = 5

    def __init__(self, tello):
        self.tello = tello
        pygame.init()

        self.joy = pygame.joystick.Joystick(0)
        self.joy.init()

        self.status_thread = threading.Thread(target=self.refresh_commands)
        self.status_thread.daemon = True
        self.status_thread.start()

    def normalize_axis(self, value):
        if self.zero_limit_min < value < self.zero_limit_max:
            return 0
        return value

    def refresh_commands(self):
        while self.is_running:
            curr_axis_values = {}
            events = pygame.event.get()
            if not events:
                time.sleep(.1)
            for event in events:
                if event.type == pygame.JOYAXISMOTION:
                    curr_axis_values[event.axis] = map(event.value, -1, 1, -100, 100)
                elif event.type == pygame.JOYBUTTONDOWN:
                    if event.button == 1 or event.button == 14:
                        self.tello.takeoff()
                    elif event.button == 2 or event.button == 13:
                        self.tello.land()
                    elif event.button == 3 or event.button == 12:
                        self.tello.send_command("streamon")
            self.processAxis(curr_axis_values)

    def processAxis(self, curr_axis_values):
        if not curr_axis_values:
            return
        self.axisValues.update(curr_axis_values)
        a = self.normalize_axis(self.axisValues.get(2, 0))
        b = self.normalize_axis(self.axisValues.get(3, 0)) * -1
        c = self.normalize_axis(self.axisValues.get(1, 0)) * -1
        d = self.normalize_axis(self.axisValues.get(0, 0))
        self.tello.send_rc_command(a, b, c, d)

    def stop(self):
        self.is_running = False