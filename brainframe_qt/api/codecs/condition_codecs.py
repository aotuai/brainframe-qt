from .base_codecs import Codec
from .detection_codecs import Attribute
from brainframe.shared import codec_enums


condition_test_map = {'>': "Greater than",
                      '>=': "Greater than or equal to",
                      '<': "Less than",
                      '<=': "Less than or equal to",
                      "=": "Exactly"}


IntersectionPointType = codec_enums.IntersectionPointType


class ZoneAlarmCountCondition(Codec):
    """A condition that must be met for an alarm to go off. Compares the number
    of objects in a zone to some number.
    """

    TestType = codec_enums.CountConditionTestType
    IntersectionPointType = codec_enums.IntersectionPointType

    def __init__(self, *, test, check_value, with_class_name, with_attribute,
                 window_duration, window_threshold, intersection_point,
                 id_=None):
        self.test = test
        self.check_value = check_value
        self.with_class_name = with_class_name
        self.with_attribute = with_attribute
        self.window_duration = window_duration
        self.window_threshold = window_threshold
        self.intersection_point = intersection_point
        self.id = id_

    def __repr__(self):
        condition_str = condition_test_map[self.test]
        attr = self.with_attribute
        attr = attr.value + ' ' if attr else ''
        return f"{condition_str} {self.check_value} " \
               f"{attr}{self.with_class_name}(s) "

    def to_dict(self) -> dict:
        d = dict(self.__dict__)
        d["intersection_point"] = self.intersection_point.value
        if self.with_attribute is not None:
            d["with_attribute"] = self.with_attribute.to_dict()

        return d

    @staticmethod
    def from_dict(d: dict):
        intersection_point = IntersectionPointType(
            d["intersection_point"])
        # with_attribute is an optional parameter
        with_attribute = None
        if d["with_attribute"] is not None:
            with_attribute = Attribute.from_dict(d["with_attribute"])

        return ZoneAlarmCountCondition(
            test=d["test"],
            check_value=d["check_value"],
            with_class_name=d["with_class_name"],
            with_attribute=with_attribute,
            window_duration=d["window_duration"],
            window_threshold=d["window_threshold"],
            intersection_point=intersection_point,
            id_=d["id"])


class ZoneAlarmRateCondition(Codec):
    """A condition that must be met for an alarm to go off. Compares the rate of
    change in the count of some object against a test value.
    """

    TestType = codec_enums.RateConditionTestType
    DirectionType = codec_enums.DirectionType

    direction_map = {DirectionType.ENTERING: "entered",
                     DirectionType.EXITING: "exited",
                     DirectionType.ENTERING_OR_EXITING: "entered or exited"}

    def __init__(self, *, test, duration, change, direction, with_class_name,
                 with_attribute, intersection_point, id_=None):
        self.test = test
        self.duration = duration
        self.change = change
        self.direction = direction
        self.with_class_name = with_class_name
        self.with_attribute = with_attribute
        self.intersection_point = intersection_point
        self.id = id_

    def __repr__(self):
        condition_str = condition_test_map[self.test]
        direction_str = self.direction_map[self.direction]
        return f"{condition_str} {self.change} {self.with_class_name}(s) " \
               f"{direction_str} within {self.duration} seconds"

    def to_dict(self) -> dict:
        d = dict(self.__dict__)
        d["intersection_point"] = self.intersection_point.value
        if self.with_attribute is not None:
            d["with_attribute"] = self.with_attribute.to_dict()

        d["direction"] = self.direction.value

        return d

    @staticmethod
    def from_dict(d: dict):
        intersection_point = IntersectionPointType(
            d["intersection_point"])
        # with_attribute is an optional parameter
        with_attribute = None
        if d["with_attribute"] is not None:
            with_attribute = Attribute.from_dict(d["with_attribute"])

        return ZoneAlarmRateCondition(
            test=d["test"],
            duration=d["duration"],
            change=d["change"],
            direction=ZoneAlarmRateCondition.DirectionType(d["direction"]),
            with_class_name=d["with_class_name"],
            with_attribute=with_attribute,
            intersection_point=intersection_point,
            id_=d["id"])

