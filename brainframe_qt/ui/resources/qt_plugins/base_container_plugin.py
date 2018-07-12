import sip

from PyQt5.QtDesigner import QExtensionFactory, \
    QPyDesignerContainerExtension, QDesignerFormWindowInterface, \
    QPyDesignerPropertySheetExtension

from brainframe.client.ui.resources import BasePlugin

Q_TYPEID = {
    'QDesignerContainerExtension': 'org.qt-project.Qt.Designer.Container',
    'QDesignerPropertySheetExtension': 'org.qt-project.Qt.Designer.PropertySheet'
}
"""No idea what this is used for"""


class BaseContainerPlugin(BasePlugin):

    def __init__(self, cls=None, qt_designer_folder=None, name=None, path=None):

        if cls is not None:
            cls.container_plugin = True
            """Used in factory as a hack to be able to detect if a widget is a
            a contianer plugin"""

        super().__init__(cls, qt_designer_folder, name, path)

        self.factory = None

    def initialize(self, form_editor):
        if self._initialized:
            return
        manager = form_editor.extensionManager()
        if manager:
            self.factory = BaseContainerExtensionFactory(manager)
            manager.registerExtensions(
                self.factory,
                Q_TYPEID['QDesignerContainerExtension'])
        self._initialized = True

    def domXml(self):
        return (f'<widget class="{self.widget_name}" name="{self.widget_name}">'
                f'  <widget class="QWidget" name="container" />'
                f'</widget>')

    def currentIndexChanged(self, index):
        widget = self.sender()
        if widget and isinstance(widget, self.widget_class):
            form = QDesignerFormWindowInterface.findFormWindow(widget)
            if form:
                form.emitSelectionChanged()

    def pageTitleChanged(self, title):
        widget = self.sender()
        if widget and isinstance(widget, self.widget_class):
            page = widget.widget(widget.getCurrentIndex())
            form = QDesignerFormWindowInterface.findFormWindow(widget)
            if form:
                editor = form.core()
                manager = editor.extensionManager()
                sheet = manager.extension(page, Q_TYPEID[
                    'QDesignerPropertySheetExtension'])
                # This explicit cast is necessary here
                sheet = sip.cast(sheet, QPyDesignerPropertySheetExtension)
                propertyIndex = sheet.indexOf('windowTitle')
                sheet.setChanged(propertyIndex, True)


class BaseContainerExtensionFactory(QExtensionFactory):

    def __init__(self, parent=None):
        super().__init__(parent)

    def createExtension(self, obj, iid, parent):
        if iid != Q_TYPEID['QDesignerContainerExtension']:
            return None
        # This check is a hack. This attribute is forced in during
        # BaseContainerPlugin initialization
        if hasattr(obj, "container_plugin"):
            return BaseContainerExtension(obj, parent)
        return None


class BaseContainerExtension(QPyDesignerContainerExtension):

    def __init__(self, widget, parent=None):
        super().__init__(parent)

        self._widget = widget

    def addWidget(self, widget):
        self._widget.addPage(widget)

    def count(self):
        return self._widget.count()

    def currentIndex(self):
        return self._widget.getCurrentIndex()

    def insertWidget(self, index, widget):
        self._widget.insertPage(index, widget)

    def remove(self, index):
        self._widget.removePage(index)

    def setCurrentIndex(self, index):
        self._widget.setCurrentIndex(index)

    def widget(self, index):
        return self._widget.widget(index)
