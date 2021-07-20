#!python3

import sys
from PySide2.QtCore import(Property, QObject, QPropertyAnimation, Signal)
from PySide2.QtGui import (QGuiApplication, QMatrix4x4, QQuaternion, QVector3D, QColor)
from PySide2.Qt3DCore import (Qt3DCore)
from PySide2.Qt3DExtras import (Qt3DExtras)
from PySide2.Qt3DRender import (Qt3DRender)
from PySide2.QtWidgets import *

from detail import ObjectDetail
from treeview import TreeView
from model import DataModel
from viewer import Viewer

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self._model = DataModel()
        self._3dview = Viewer(self._model.getRootEntity())

        layout = QHBoxLayout()
        viewer = QWidget.createWindowContainer(self._3dview)
        panel = QVBoxLayout()
        
        layout.addWidget(viewer, 4)
        layout.addLayout(panel, 1)

        self._tree = TreeView()
        panel.addWidget(self._tree)

        buttonLayout = QHBoxLayout()
        bBox = QPushButton("+Box")
        bBox.clicked.connect(lambda: self._model.addShape("box"))
        bSphere = QPushButton("+Sphere")
        bSphere.clicked.connect(lambda: self._model.addShape("sphere"))
        bStl = QPushButton("+STL")
        bStl.clicked.connect(lambda: self._model.addShape("stl"))
        bMinus = QPushButton("-")
        bMinus.clicked.connect(lambda: self._model.delShape())
        bUndo = QPushButton("U")
        bRedo = QPushButton("R")

        buttonLayout.addWidget(bBox)
        buttonLayout.addWidget(bSphere)
        buttonLayout.addWidget(bStl)
        buttonLayout.addWidget(bMinus)
        # buttonLayout.addWidget(bUndo)
        # buttonLayout.addWidget(bRedo)

        panel.addLayout(buttonLayout)

        self._detail = ObjectDetail()
        panel.addLayout(self._detail)

        self.setLayout(layout)

        self._model.assignCallback("tree", self._tree.updateData)
        self._tree.setCallback(self._model.selectElement)

        self._model.assignCallback("detail", self._detail.updateValue)
        self._detail.setCallback(self._model.setValue)

        self._3dview.setCallback(self._model.incUpdate)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    view = MainWindow()
    view.resize(1024,768)
    view.show()
    sys.exit(app.exec_())