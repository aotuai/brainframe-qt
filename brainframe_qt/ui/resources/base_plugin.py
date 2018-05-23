import inspect

from PyQt5.QtDesigner import QPyDesignerCustomWidgetPlugin
from PyQt5.QtGui import QIcon


# TODO(Bryce Beagle): Use a metaclass
class BasePlugin(QPyDesignerCustomWidgetPlugin):
    """Subclass me to create a create a new custom plugin for QtDesigner"""

    # Init instance
    def __init__(self, cls=None,
                 qt_designer_folder=None,
                 name=None,
                 path=None):

        try:
            assert not inspect.ismodule(cls)
        except AssertionError:
            raise AssertionError(f"widget_type for {name} is a module,"
                                 f"not a class. Check your imports")

        if cls is None:
            print("IGNORE THIS ERROR. QT DESIGNER IS DUMB:")
            return

        super().__init__()

        self.widget_class = cls
        self.qt_designer_folder = "Dilili" if not qt_designer_folder \
            else qt_designer_folder

        self.widget_name = cls.__name__ if not name else name
        self.widget_path = cls.__module__ if not path else path

        self._initialized = False

    def initialize(self, form_editor):
        """Initialize the custom widget for use with the specified form_editor

        Not sure why this exists, but I think it was required
        """
        if self._initialized:
            return

        self._initialized = True

    def isInitialized(self):
        """Return if the custom widget has been initialized"""
        return self._initialized

    def createWidget(self, parent):
        """Return a new instance of the custom widget with the given parent"""
        return self.widget_class(parent=parent)

    def name(self):
        """Name of the class that implements the custom widget"""
        return self.widget_name

    def group(self):
        """Name of the group that the custom widget belongs to

        A new group will be created if it doesn't exist
        """
        return self.qt_designer_folder

    def icon(self):
        """Icon that QtDesigner puts next to the widget in the sidebar"""
        # TODO(Bryce Beagle)
        return QIcon()

    def toolTip(self):
        """Short desc. of the custom widget used by QtDesigner in a tooltip"""
        # TODO(Bryce Beagle): Maybe support?
        return self.widget_name

    def whatsThis(self):
        """Full desc. of the custom widget used by QtDesigner in a tooltip"""
        # TODO(Bryce Beagle): Maybe support?
        return self.widget_name

    def isContainer(self):
        """Whether or not the widget is a container-type widget"""
        # TODO(Bryce Beagle): Maybe support?
        return False

    def domXml(self):
        """XML Fragment

        XML fragment that allows the default values of the custom widget's
        properties to be overridden
        """
        return f'<widget class="{self.widget_name}" name="{self.widget_name}">'\
               f'</widget>'

    def includeFile(self):
        """Name of the module containing the class that implements the widget"""
        return self.widget_path
