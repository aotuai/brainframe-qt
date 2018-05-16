from enum import Enum

from .base_codecs import Codec
from .detection_codecs import Attribute


condition_test_map = {'>': "Greater than",
                      '>=': "Greater than or equal to",
                      '<': "Less than",
                      '<=': "Less than or equal to",
                      "=": "Exactly"}


class ZoneAlarmCondition(Codec):
    """This holds logic information for a ZoneAlarm."""

    test_types = [">", "<", "=", "!="]

    def __init__(self, *, test, check_value, with_class_name, with_attribute,
                 id_=None):
        self.test = test
        self.check_value = check_value
        self.with_class_name = with_class_name
        self.with_attribute = with_attribute
        self.id = id_

    def __repr__(self):
        condition_str = condition_test_map[self.test]
        attr = self.with_attribute
        attr = attr.value + ' ' if attr else ''
        return f"{condition_str} {self.check_value} " \
               f"{attr}{self.with_class_name}(s) "

    def to_dict(self) -> dict:
        d = dict(self.__dict__)
        if self.with_attribute is not None:
            d["with_attribute"] = self.with_attribute.to_dict()

        return d

    @staticmethod
    def from_dict(d: dict):
        # with_attribute is an optional parameter
        with_attribute = None
        if d["with_attribute"] is not None:
            with_attribute = Attribute.from_dict(d["with_attribute"])

        return ZoneAlarmCondition(
            test=d["test"],
            check_value=d["check_value"],
            with_class_name=d["with_class_name"],
            with_attribute=with_attribute,
            id_=d["id"])


class ZoneAlarmRateCondition(Codec):
    """A condition that must be met for an alarm to go off. Compares the rate of
    change in the count of some object against a test value.
    """

    test_types = [">=", "<="]

    # noinspection PyArgumentList
    # PyCharm incorrectly complains
    DirectionType = Enum("DirectionType",
                         ["entering", "exiting", "entering_or_exiting"])

    direction_map = {DirectionType.entering: "entered",
                     DirectionType.exiting: "exited",
                     DirectionType.entering_or_exiting: "entered or exited"}

    def __init__(self, *, test, duration, change, direction, with_class_name,
                 with_attribute, id_=None):
        self.test = test
        self.duration = duration
        self.change = change
        self.direction = direction
        self.with_class_name = with_class_name
        self.with_attribute = with_attribute
        self.id = id_

    def __repr__(self):
        condition_str = condition_test_map[self.test]
        direction_str = self.direction_map[self.direction]
        return f"{condition_str} {self.change} {self.with_class_name}(s) " \
               f"{direction_str} within {self.duration} seconds"

    def to_dict(self) -> dict:
        d = dict(self.__dict__)
        if self.with_attribute is not None:
            d["with_attribute"] = self.with_attribute.to_dict()

        d["direction"] = self.direction.name

        return d

    @staticmethod
    def from_dict(d: dict):
        # with_attribute is an optional parameter
        with_attribute = None
        if d["with_attribute"] is not None:
            with_attribute = Attribute.from_dict(d["with_attribute"])

        return ZoneAlarmRateCondition(
            test=d["test"],
            duration=d["duration"],
            change=d["change"],
            direction=ZoneAlarmRateCondition.DirectionType[d["direction"]],
            with_class_name=d["with_class_name"],
            with_attribute=with_attribute,
            id_=d["id"])

