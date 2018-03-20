import pytest

from visionapp.client.api.data_structures import *

ATTRIBUTE = {"category": "Gender",
             "value": "male"}

DETECTION_1 = {"class_name": "face",
               "rect": [220, 340, 100, 400],
               "children": [],
               "attributes": [ATTRIBUTE, ATTRIBUTE]}
DETECTION = {"class_name": "person",
             "rect": [100, 200, 400, 500],
             "children": [DETECTION_1, DETECTION_1, DETECTION_1],
             "attributes": [ATTRIBUTE, ATTRIBUTE, ATTRIBUTE]}

ZONE_ALARM_CONDITION = {
                "test": ">",
                "check_value": 3,
                "with_class_name": "person",
                "with_attribute": ATTRIBUTE
             }
ZONE_ALARM = {"id": 1,
              "name": "Smoking in Building",
              "conditions": [ZONE_ALARM_CONDITION, ZONE_ALARM_CONDITION],
              "use_active_time": True,
              "active_start_time": "07:00:59",
              "active_end_time": "18:00:13"}

ALERT = {"id": 1,
         "alarm_id": 2,
         "start_time": 123123123,
         "end_time": 234234234}

ZONE = {"id": 1,
        "name": "Couch Area",
        "alarms": [ZONE_ALARM, ZONE_ALARM, ZONE_ALARM, ZONE_ALARM],
        "coords": [[0, 0], [10, 10], [100, 500], [0, 500], [10, 250]]}

ZONE_STATUS = {"zone": ZONE,
               "tstamp": 123123123,
               "total_entered": {"person": 100, "car": 50},
               "total_exited": {"person": 80, "car": 30},
               "detections": [DETECTION, DETECTION, DETECTION, DETECTION],
               "alerts": [ALERT, ALERT, ALERT]}

STREAM_CONFIGURATION = {"name": "Mall Lobby",
                        "id": 1,
                        "connection_type": "IPCamera",
                        "parameters": {
                            "url": "http://IP_ADDRESS:PORT/video/",}
                        }

ENGINE_CONFIGURATION = {"version": "0.0.0.1",
                        "detectable": {"person": ["boy", "girl", "smoking", "drinking"],
                                       "dog": ["barking", "biting"],
                                       "car": ["crash"]},
                        "max_streams": 4 }

codec_to_dict = {Alert: ALERT,
                 Attribute: ATTRIBUTE,
                 Detection: DETECTION,
                 ZoneAlarmCondition: ZONE_ALARM_CONDITION,
                 ZoneAlarm: ZONE_ALARM,
                 Zone: ZONE,
                 ZoneStatus: ZONE_STATUS,
                 StreamConfiguration: STREAM_CONFIGURATION,
                 EngineConfiguration: ENGINE_CONFIGURATION}


@pytest.mark.parametrize(('codec_type', 'dict_format'), codec_to_dict.items())
def test_serialization_and_deserialization(codec_type, dict_format):
    """
    This will:
    Initialize the class FROM a dict
    Convert the initialized class TO a json.
    Initialize the class FROM a json.
    Convert the initialized class TO a dict

    Then, it asserts that it is the same as the original dict format.
    :param codec_type: Any object subclassing Codec
    :param dict_format: The dict to feed into the object
    """

    initialized = codec_type.from_dict(dict_format)
    json_format = initialized.to_json()
    back_to_codec = codec_type.from_json(json_format)
    final_dict_format = back_to_codec.to_dict()
    assert final_dict_format == dict_format


