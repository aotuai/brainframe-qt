from abc import ABCMeta

from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QLayout, QWidget


# Hack to allow class to inherit from both QObject (type=sip.wrappertype) and
# abc.ABC (type=type)
class ABCObject(type(QObject), ABCMeta):
    pass


class BaseQMixin(metaclass=ABCObject):
    pass


class BaseWidgetMixin(QWidget, metaclass=ABCObject):
    pass
