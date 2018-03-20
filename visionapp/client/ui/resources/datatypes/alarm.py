# TODO: Python 3.7 use @dataclass
class Alarm:
    def __init__(self, alarm_name, test_type, count, countable, behavior, zone,
                 start_time, stop_time):
        self.alarm_name = alarm_name
        self.test_type = test_type
        self.count = count
        self.countable = countable
        self.behavior = behavior
        self.zone = zone
        self.start_time = start_time
        self.stop_time = stop_time