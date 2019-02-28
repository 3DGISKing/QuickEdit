# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Quick Editing Attribute
                                 A QGIS plugin
 tool for quick editing attributes in field campaigns
                             -------------------
        begin                : 2019-02-19
        copyright            : (C) 2019 by haris
        email                :
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os
from PyQt5 import QtGui, QtWidgets
from qgis.PyQt.QtCore import QSettings, QLocale, QTranslator, QCoreApplication, Qt
from qgis.core import *
from .IdentifyGeometry import IdentifyGeometry
from .TreeTypeDialog import TreeTypeDialog
from .DiameterDialog import DiameterDialog


class QuickEdit:
    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """

        self.iface = iface

        try:
            self.qgis_version = Qgis.QGIS_VERSION_INT
        except NameError:
            self.qgis_version = QGis.QGIS_VERSION_INT

        # we store geometry type
        self.Point, self.Line, self.Polygon = (
                [QgsWkbTypes.PointGeometry, QgsWkbTypes.LineGeometry, QgsWkbTypes.PolygonGeometry]
                if self.qgis_version >= 29900 else
                [QGis.Point, QGis.Line, QGis.Polygon])

        if QSettings().value('locale/overrideFlag', type=bool):
            locale = QSettings().value('locale/userLocale')
        else:
            locale = QLocale.system().name()

        if locale:
            locale_path = os.path.join(os.path.dirname(__file__), 'i18n', locale)
            self.translator = QTranslator()

            if self.translator.load(locale_path):
                QCoreApplication.installTranslator(self.translator)

        # Save reference to the QGIS interface
        self.iface = iface
        self.mapCanvas = iface.mapCanvas()

        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)

        icon_path = os.path.join(self.plugin_dir, "icons", "quickEdit.png")
        self.mapToolAction = QtWidgets.QAction(QtGui.QIcon(icon_path),"Quick Editing Attribute", self.iface.mainWindow())
        self.mapToolAction.setCheckable(True)
        self.mapToolAction.triggered.connect(self.setMapTool)

        self.mapTool = IdentifyGeometry(self.mapCanvas)

        self.mapTool.geomIdentified.connect(self.onGeometryIdentified)
        self.mapTool.setAction(self.mapToolAction)

    def tr(self, message):
        return QCoreApplication.translate(self.__class__.__name__, message)

    # noinspection PyPep8Naming
    def initGui(self):
        self.iface.addToolBarIcon(self.mapToolAction)
        self.iface.addPluginToMenu("&Quick Editing Attribute", self.mapToolAction)

    def unload(self):
        self.iface.removePluginMenu("&Quick Editing Attribute", self.mapToolAction)
        self.iface.removeToolBarIcon(self.mapToolAction)

    # noinspection PyPep8Naming
    def setMapTool(self):
        self.mapCanvas.setMapTool(self.mapTool)

    def show_tree_type_dialog(self, selected_layer, selected_feature):
        tree_type_dialog = TreeTypeDialog()

        tree_type_dialog.selectedLayer = selected_layer
        tree_type_dialog.selectedFeature = selected_feature

        tree_type_dialog.confirm.connect(self.onTreeTypeDialogConfirmed)

        tree_type_dialog.exec_()

    # noinspection PyPep8Naming
    def onGeometryIdentified(self, selectedLayer, selectedFeature):
        if selectedLayer.geometryType() not in [self.Point]:
            self.iface.messageBar().pushCritical(self.tr('Error'), self.tr('Selected layer is not Tree layer! Geometry type is not point.'))
            return

        tree_type_field_id = selectedLayer.fields().indexFromName('tree_type')

        if tree_type_field_id == -1:
            self.iface.messageBar().pushCritical(self.tr('Error'), self.tr('Selected layer is not Tree layer! Can not find "tree_type" attribute.'))
            return

        diameter_field_id = selectedLayer.fields().indexFromName('diameter')

        if diameter_field_id == -1:
            self.iface.messageBar().pushCritical(self.tr('Error'), self.tr('Selected layer is not Tree layer! Can not find "diameter" attribute.'))
            return

        status_field_id = selectedLayer.fields().indexFromName('status')

        if status_field_id == -1:
            self.iface.messageBar().pushCritical(self.tr('Error'), self.tr('Selected layer is not Tree layer! Can not find "status" attribute.'))
            return

        self.show_tree_type_dialog(selectedLayer, selectedFeature)

    # noinspection PyPep8Naming
    def onTreeTypeDialogConfirmed(self, selectedLayer, selectedFeature):
        diameterDialog = DiameterDialog()

        diameterDialog.selectedLayer = selectedLayer
        diameterDialog.selectedFeature = selectedFeature

        diameterDialog.back.connect(self.onDiameterDialogBacked)

        diameterDialog.exec()

    # noinspection PyPep8Naming
    def onDiameterDialogBacked(self, selectedLayer, selectedFeature):
        self.show_tree_type_dialog(selectedLayer, selectedFeature)


if __name__ == '__main__':
    pass