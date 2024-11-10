import os.path
from pathlib import Path
from typing import Optional

from qgis.core import Qgis, QgsLayerTreeGroup, QgsMessageLog, QgsProject, QgsVectorLayer
from qgis.PyQt.QtCore import QCoreApplication, QSettings, Qt, QTranslator
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QFileDialog

from odrviewer.converter.convert_odr_to_qgis import load_odr_map
from odrviewer.styling.apply_qgis_styles import apply_qgis_styles


class OpenDriveViewer:
    def __init__(self, iface):
        """
        Constructor.
        """
        # Save reference to the QGIS interface
        self.iface = iface

        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)

        self.actions = []
        self.menu = self.tr("&OpenDRIVE Viewer")

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate("OpenDRIVE Viewer", message)

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None,
    ):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """
        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_menu:
            self.iface.addPluginToVectorMenu(self.menu, action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        icon_path = ":/plugins/odrviewer/icon.png"
        self.add_action(
            icon_path,
            text=self.tr("&Open..."),
            callback=self.open_map,
            parent=self.iface.mainWindow(),
        )

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginVectorMenu(self.tr("&OpenDRIVE Viewer"), action)

    def show_file_dialog(self) -> Optional[str]:
        folder_dialog = QFileDialog(self.iface.mainWindow())
        folder_dialog.setWindowTitle("Select an OpenDRIVE file")
        folder_dialog.setFileMode(QFileDialog.ExistingFile)
        folder_dialog.setOption(QFileDialog.ShowDirsOnly, False)
        folder_dialog.setOption(QFileDialog.ReadOnly, False)

        if folder_dialog.exec_() == QFileDialog.Accepted:
            selected_files = folder_dialog.selectedFiles()
            return selected_files[0]
        return None

    def open_map(self):
        """
        Loads an OpenDRIVE map.
        """
        # Open a folder select dialog, and try to read a map.
        odr_filename_str = self.show_file_dialog()
        if odr_filename_str is None:
            print("No file selected")
            return

        odr_filename = Path(odr_filename_str)
        try:
            # Try to load the map.
            qgis_map = load_odr_map(odr_filename)

        except AssertionError as e:
            print(f"failed to load map: {e}")
            return

        # The map was loaded successfully, transfer the ownership of the vector layers to QGIS
        apply_qgis_styles(qgis_map)
        map_name = odr_filename.stem

        current_map_group = QgsProject.instance().layerTreeRoot().addGroup(f"ODR_{map_name}")

        self.load_layer(qgis_map.boundaries, "boundaries", current_map_group)
        self.load_layer(qgis_map.reference_lines, "reference_lines", current_map_group)
        self.load_layer(qgis_map.reference_line_segments, "reference_line_segments", current_map_group, False)
        self.load_layer(qgis_map.reference_frames, "reference_frames", current_map_group, False)
        self.load_layer(qgis_map.lanes, "lanes", current_map_group)

    def load_layer(self, qgis_layer: QgsVectorLayer, name: str, group: QgsLayerTreeGroup, visible=True) -> None:
        """
        Adds a QGIS vector layer into QGIS. It will log an error if loading failed.
        """
        added_layer = QgsProject.instance().addMapLayer(qgis_layer, False)
        group.addLayer(qgis_layer)
        if added_layer is None:
            QgsMessageLog.logMessage(f"failed to add map layer {name}", level=Qgis.Critical)

        if not visible:
            group.findLayer(added_layer).setItemVisibilityChecked(False)
