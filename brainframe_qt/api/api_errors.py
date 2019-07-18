import re

from brainframe.shared import error_kinds


kind_to_error_type = {}
"""Maps error kinds to their corresponding error type."""


def register_error_type(cls):
    """A class decorator. Registers the given class so that it can be retrieved
    based on its kind.
    """
    obj = cls("")
    global kind_to_error_type
    kind_to_error_type[obj.kind] = cls
    return cls


class BaseAPIError(Exception):
    """All API errors subclass this error."""
    def __init__(self, kind, description):
        self.kind = kind
        self.description = description
        super().__init__(f"{self.kind}: {description}")

    @property
    def pretty_name(self):
        name = self.__class__.__name__

        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1 \2', name)
        s2 = re.sub('([a-z0-9])([A-Z])', r'\1 \2', s1).capitalize()
        s3 = s2.rsplit(" error")[0]

        return s3


@register_error_type
class UnknownError(BaseAPIError):
    """Something unexpected happened. The server may be in an invalid state."""
    def __init__(self, description):
        super().__init__(error_kinds.UNKNOWN, description)


@register_error_type
class StreamConfigNotFoundError(BaseAPIError):
    """A StreamConfiguration specified by the client could not be found."""
    def __init__(self, description):
        super().__init__(error_kinds.STREAM_CONFIG_NOT_FOUND, description)


@register_error_type
class ZoneNotFoundError(BaseAPIError):
    """A Zone specified by the client could not be found."""
    def __init__(self, description):
        super().__init__(error_kinds.ZONE_NOT_FOUND, description)


@register_error_type
class ZoneNotDeletableError(BaseAPIError):
    """A client tried to delete a default Zone"""
    def __init__(self, description):
        super().__init__(error_kinds.ZONE_NOT_DELETABLE, description)


@register_error_type
class AlertNotFoundError(BaseAPIError):
    """An Alert specified by the client could not be found."""
    def __init__(self, description):
        super().__init__(error_kinds.ALERT_NOT_FOUND, description)


@register_error_type
class StreamNotFoundError(BaseAPIError):
    """The corresponding stream for a StreamConfiguration is not available."""
    def __init__(self, description):
        super().__init__(error_kinds.STREAM_NOT_FOUND, description)


@register_error_type
class InvalidSyntaxError(BaseAPIError):
    """The syntax of the request could not be parsed."""
    def __init__(self, description):
        super().__init__(error_kinds.INVALID_SYNTAX, description)


@register_error_type
class InvalidFormatError(BaseAPIError):
    """The request was parsed, but some value within the request is invalid."""
    def __init__(self, description):
        super().__init__(error_kinds.INVALID_FORMAT, description)


@register_error_type
class NotImplementedInAPIError(BaseAPIError):
    """The client requested something that is not currently implemented."""
    def __init__(self, description):
        super().__init__(error_kinds.NOT_IMPLEMENTED, description)


@register_error_type
class StreamNotOpenedError(BaseAPIError):
    """A stream failed to open when it was required to."""
    def __init__(self, description):
        super().__init__(error_kinds.STREAM_NOT_OPENED, description)


@register_error_type
class DuplicateStreamSourceError(BaseAPIError):
    """There was an attempted to create a stream configuration with the same
    source as an existing one.
    """
    def __init__(self, description):
        super().__init__(error_kinds.DUPLICATE_STREAM_SOURCE, description)


@register_error_type
class DuplicateZoneNameError(BaseAPIError):
    """There was an attempt to make a zone with the same name as another zone
    within the same stream.
    """
    def __init__(self, description):
        super().__init__(error_kinds.DUPLICATE_ZONE_NAME, description)


@register_error_type
class DuplicateIdentityNameError(BaseAPIError):
    """There was an attempt to create a new identity with the same name as
    another identity.
    """
    def __init__(self, description):
        super().__init__(error_kinds.DUPLICATE_IDENTITY_NAME, description)


@register_error_type
class NoDetectorForClassError(BaseAPIError):
    """There was an attempt to use a class name that is not detectable."""
    def __init__(self, description):
        super().__init__(error_kinds.NO_DETECTOR_FOR_CLASS, description)


@register_error_type
class NoEncoderForClassError(BaseAPIError):
    """There was an attempt to create an identity for a class that is not
    encodable.
    """
    def __init__(self, description):
        super().__init__(error_kinds.NO_ENCODER_FOR_CLASS, description)


@register_error_type
class IdentityNotFoundError(BaseAPIError):
    """An identity specified by the client could not be found."""
    def __init__(self, description):
        super().__init__(error_kinds.IDENTITY_NOT_FOUND, description)


@register_error_type
class ImageNotFoundForIdentityError(BaseAPIError):
    """An image specified by the client could not be found for the specified
    identity.
    """
    def __init__(self, description):
        super().__init__(error_kinds.IMAGE_NOT_FOUND_FOR_IDENTITY, description)


@register_error_type
class InvalidImageTypeError(BaseAPIError):
    """An image could not be decoded by OpenCV"""
    def __init__(self, description):
        super().__init__(error_kinds.INVALID_IMAGE_TYPE, description)


@register_error_type
class AnalysisLimitExceededError(BaseAPIError):
    """There was an attempt to start analysis on a stream, but the maximum
    amount of streams that may have analysis run on them at once has already
    been reached.
    """
    def __init__(self, description):
        super().__init__(error_kinds.ANALYSIS_LIMIT_EXCEEDED, description)


@register_error_type
class NoDetectionsInImageError(BaseAPIError):
    """There was an attempt to encode an image with no objects of the given
    class in the frame.
    """
    def __init__(self, description):
        super().__init__(error_kinds.NO_DETECTIONS_IN_IMAGE, description)


@register_error_type
class TooManyDetectionsInImageError(BaseAPIError):
    """There was an attempt to encode an image with more than one object of the
    given class in the frame, causing ambiguity on which one to encode.
    """
    def __init__(self, description):
        super().__init__(error_kinds.TOO_MANY_DETECTIONS_IN_IMAGE, description)


@register_error_type
class ImageAlreadyEncodedError(BaseAPIError):
    """There was an attempt to encode an image that has already been encoded for
    a given identity and a given class.
    """
    def __init__(self, description):
        super().__init__(error_kinds.IMAGE_ALREADY_ENCODED, description)


@register_error_type
class DuplicateVectorError(BaseAPIError):
    """There was an attempt to add a vector that already exists for the given
    identity and class.
    """
    def __init__(self, description):
        super().__init__(error_kinds.DUPLICATE_VECTOR, description)


@register_error_type
class FrameNotFoundForAlertError(BaseAPIError):
    """There was an attempt to get a frame for an alert that has no frame."""
    def __init__(self, description):
        super().__init__(error_kinds.FRAME_NOT_FOUND_FOR_ALERT, description)


@register_error_type
class PluginNotFoundError(BaseAPIError):
    """There was an attempt to reference a plugin that does not exist."""
    def __init__(self, description):
        super().__init__(error_kinds.PLUGIN_NOT_FOUND, description)


@register_error_type
class InvalidPluginOptionError(BaseAPIError):
    """The provided plugin options do not work for the given plugin. This could
    be because the option does not exist or the value for that option doesn't
    fit the constraints.
    """
    def __init__(self, description):
        super().__init__(error_kinds.INVALID_PLUGIN_OPTION, description)


@register_error_type
class StorageNotFoundError(BaseAPIError):
    """There was an attempt to access a storage object that does not exist."""
    def __init__(self, description):
        super().__init__(error_kinds.STORAGE_NOT_FOUND, description)


@register_error_type
class ZoneAlarmNotFoundError(BaseAPIError):
    """There was an attempt to access a zone alarm that does not exist."""
    def __init__(self, description):
        super().__init__(error_kinds.ZONE_ALARM_NOT_FOUND, description)


@register_error_type
class InvalidRuntimeOptionError(BaseAPIError):
    """There was an attempt to set a runtime option that is not supported or is
    of the wrong type.
    """
    def __init__(self, description):
        super().__init__(error_kinds.INVALID_RUNTIME_OPTION, description)


@register_error_type
class EncodingNotFoundError(BaseAPIError):
    """There was an attempt to access an encoding that does not exist."""
    def __init__(self, description):
        super().__init__(error_kinds.ENCODING_NOT_FOUND, description)


@register_error_type
class UnauthorizedError(BaseAPIError):
    """There was an attempt to access the API without proper authorization."""
    def __init__(self, description):
        super().__init__(error_kinds.UNAUTHORIZED, description)


@register_error_type
class InvalidSessionError(BaseAPIError):
    """There was an attempt to access the API with an invalid session ID,
    either because the session expired or no session with that ID has ever
    existed. The client should authenticate again to get a new session.
    """
    def __init__(self, description):
        super().__init__(error_kinds.INVALID_SESSION, description)
