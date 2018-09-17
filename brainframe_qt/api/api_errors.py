import re

from brainframe.shared import error_kinds


kind_to_error_type = {}
"""Maps error kinds to their corresponding error type."""


class BaseAPIError(BaseException):
    """All API errors subclass this error."""
    def __init__(self, kind, description):
        self.kind = kind
        super().__init__(f"{self.kind}: {description}")

    def __str__(self):

        name = self.__class__.__name__

        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1 \2', name)
        s2 = re.sub('([a-z0-9])([A-Z])', r'\1 \2', s1).capitalize()
        s3 = s2.rsplit(" error")[0]

        return s3


class UnknownError(BaseAPIError):
    """Something unexpected happened. The server may be in an invalid state."""
    def __init__(self, description):
        super().__init__(error_kinds.UNKNOWN, description)


kind_to_error_type[error_kinds.UNKNOWN] = UnknownError


class StreamConfigNotFoundError(BaseAPIError):
    """A StreamConfiguration specified by the client could not be found."""
    def __init__(self, description):
        super().__init__(error_kinds.STREAM_CONFIG_NOT_FOUND, description)


kind_to_error_type[error_kinds.STREAM_CONFIG_NOT_FOUND] = \
    StreamConfigNotFoundError


class ZoneNotFoundError(BaseAPIError):
    """A Zone specified by the client could not be found."""
    def __init__(self, description):
        super().__init__(error_kinds.ZONE_NOT_FOUND, description)


kind_to_error_type[error_kinds.ZONE_NOT_FOUND] = ZoneNotFoundError


class ZoneNotDeletableError(BaseAPIError):
    """A client tried to delete a default Zone"""
    def __init__(self, description):
        super().__init__(error_kinds.ZONE_NOT_DELETABLE, description)


kind_to_error_type[error_kinds.ZONE_NOT_DELETABLE] = ZoneNotDeletableError


class AlertNotFoundError(BaseAPIError):
    """An Alert specified by the client could not be found."""
    def __init__(self, description):
        super().__init__(error_kinds.ALERT_NOT_FOUND, description)


kind_to_error_type[error_kinds.ALERT_NOT_FOUND] = AlertNotFoundError


class StreamNotFoundError(BaseAPIError):
    """The corresponding stream for a StreamConfiguration is not available."""
    def __init__(self, description):
        super().__init__(error_kinds.STREAM_NOT_FOUND, description)


kind_to_error_type[error_kinds.STREAM_NOT_FOUND] = StreamNotFoundError


class InvalidSyntaxError(BaseAPIError):
    """The syntax of the request could not be parsed."""
    def __init__(self, description):
        super().__init__(error_kinds.INVALID_SYNTAX, description)


kind_to_error_type[error_kinds.INVALID_SYNTAX] = InvalidSyntaxError


class InvalidFormatError(BaseAPIError):
    """The request was parsed, but some value within the request is invalid."""
    def __init__(self, description):
        super().__init__(error_kinds.INVALID_FORMAT, description)


kind_to_error_type[error_kinds.INVALID_FORMAT] = InvalidFormatError


class NotImplementedInAPIError(BaseAPIError):
    """The client requested something that is not currently implemented."""
    def __init__(self, description):
        super().__init__(error_kinds.NOT_IMPLEMENTED, description)


kind_to_error_type[error_kinds.NOT_IMPLEMENTED] = NotImplementedInAPIError


class StreamNotOpenedError(BaseAPIError):
    """A stream failed to open when it was required to."""
    def __init__(self, description):
        super().__init__(error_kinds.STREAM_NOT_OPENED, description)


kind_to_error_type[error_kinds.STREAM_NOT_OPENED] = StreamNotOpenedError


class DuplicateStreamSourceError(BaseAPIError):
    """There was an attempted to create a stream configuration with the same
    source as an existing one.
    """
    def __init__(self, description):
        super().__init__(error_kinds.DUPLICATE_STREAM_SOURCE, description)


kind_to_error_type[error_kinds.DUPLICATE_STREAM_SOURCE] = \
    DuplicateStreamSourceError


class DuplicateZoneNameError(BaseAPIError):
    """There was an attempt to make a zone with the same name as another zone
    within the same stream.
    """
    def __init__(self, description):
        super().__init__(error_kinds.DUPLICATE_ZONE_NAME, description)


kind_to_error_type[error_kinds.DUPLICATE_ZONE_NAME] = DuplicateZoneNameError


class DuplicateIdentityNameError(BaseAPIError):
    """There was an attempt to create a new identity with the same name as
    another identity.
    """
    def __init__(self, description):
        super().__init__(error_kinds.DUPLICATE_IDENTITY_NAME, description)


kind_to_error_type[error_kinds.DUPLICATE_IDENTITY_NAME] = \
    DuplicateIdentityNameError


class NotDetectableError(BaseAPIError):
    """There was an attempt to use a class name that is not detectable."""
    def __init__(self, description):
        super().__init__(error_kinds.NOT_DETECTABLE, description)


kind_to_error_type[error_kinds.NOT_DETECTABLE] = NotDetectableError


class NoEncoderForClassError(BaseAPIError):
    """There was an attempt to create an identity for a class that is not
    encodable.
    """
    def __init__(self, description):
        super().__init__(error_kinds.NO_ENCODER_FOR_CLASS, description)


kind_to_error_type[error_kinds.NO_ENCODER_FOR_CLASS] = NoEncoderForClassError


class IdentityNotFoundError(BaseAPIError):
    """An identity specified by the client could not be found."""
    def __init__(self, description):
        super().__init__(error_kinds.IDENTITY_NOT_FOUND, description)


kind_to_error_type[error_kinds.IDENTITY_NOT_FOUND] = IdentityNotFoundError


class ImageNotFoundForIdentityError(BaseAPIError):
    """An image specified by the client could not be found for the specified
    identity.
    """
    def __init__(self, description):
        super().__init__(error_kinds.IMAGE_NOT_FOUND_FOR_IDENTITY, description)


kind_to_error_type[error_kinds.IMAGE_NOT_FOUND_FOR_IDENTITY] = \
    ImageNotFoundForIdentityError


class InvalidImageTypeError(BaseAPIError):
    """An image could not be decoded by OpenCV"""
    def __init__(self, description):
        super().__init__(error_kinds.INVALID_IMAGE_TYPE, description)


kind_to_error_type[error_kinds.INVALID_IMAGE_TYPE] = InvalidImageTypeError


class AnalysisLimitExceededError(BaseAPIError):
    """There was an attempt to start analysis on a stream, but the maximum
    amount of streams that may have analysis run on them at once has already
    been reached.
    """
    def __init__(self, description):
        super().__init__(error_kinds.ANALYSIS_LIMIT_EXCEEDED, description)


kind_to_error_type[error_kinds.ANALYSIS_LIMIT_EXCEEDED] = \
    AnalysisLimitExceededError


class NoDetectionsInImageError(BaseAPIError):
    """There was an attempt to encode an image with no objects of the given
    class in the frame.
    """
    def __init__(self, description):
        super().__init__(error_kinds.NO_DETECTIONS_IN_IMAGE, description)


kind_to_error_type[error_kinds.NO_DETECTIONS_IN_IMAGE] = \
    NoDetectionsInImageError


class TooManyDetectionsInImageError(BaseAPIError):
    """There was an attempt to encode an image with more than one object of the
    given class in the frame, causing ambiguity on which one to encode.
    """
    def __init__(self, description):
        super().__init__(error_kinds.TOO_MANY_DETECTIONS_IN_IMAGE, description)


kind_to_error_type[error_kinds.TOO_MANY_DETECTIONS_IN_IMAGE] = \
    TooManyDetectionsInImageError


class ImageAlreadyEncodedError(BaseAPIError):
    """There was an attempt to encode an image that has already been encoded for
    a given identity and a given class.
    """
    def __init__(self, description):
        super().__init__(error_kinds.IMAGE_ALREADY_ENCODED, description)


kind_to_error_type[error_kinds.IMAGE_ALREADY_ENCODED] = ImageAlreadyEncodedError


class DuplicateVectorError(BaseAPIError):
    """There was an attempt to add a vector that already exists for the given
    identity and class.
    """
    def __init__(self, description):
        super().__init__(error_kinds.DUPLICATE_VECTOR, description)


kind_to_error_type[error_kinds.DUPLICATE_VECTOR] = DuplicateVectorError


class FrameNotFoundForAlertError(BaseAPIError):
    """There was an attempt to get a frame for an alert that has no frame."""
    def __init__(self, description):
        super().__init__(error_kinds.FRAME_NOT_FOUND_FOR_ALERT, description)


kind_to_error_type[error_kinds.FRAME_NOT_FOUND_FOR_ALERT] = \
    FrameNotFoundForAlertError
