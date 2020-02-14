import abc

from PyQt5.QtWidgets import QWidget


# Hack to allow class to inherit from both QObject (type=sip.wrappertype) and
# abc.ABC (type=type)
class ABCWidget(type(QWidget), type(abc.ABC)):
    pass


class BaseMixin(QWidget, metaclass=ABCWidget):
    pass
