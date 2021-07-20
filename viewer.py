from PySide2.QtCore import(Property, QObject, QPropertyAnimation, Signal, Qt)
from PySide2.QtGui import (QGuiApplication, QMatrix4x4, QQuaternion, QVector3D, QColor)
from PySide2.Qt3DCore import (Qt3DCore)
from PySide2.Qt3DExtras import (Qt3DExtras)
from PySide2.Qt3DRender import (Qt3DRender)
from PySide2.QtWidgets import *
import math
from model import BindingEntity

class Viewer(Qt3DExtras.Qt3DWindow):
    def __init__(self, root):
        super(Viewer, self).__init__()

        self.camera().lens().setPerspectiveProjection(45, 16 / 9, 0.1, 1000)
        self.camera().setPosition(QVector3D(0, 0, 40))
        self.camera().setViewCenter(QVector3D(0, 0, 0))

        self.rootEntity = root
        self.setRootEntity(self.rootEntity)

        self.transform = Qt3DCore.QTransform()
        self.rootEntity.addComponent(self.transform)

        self.light = Qt3DRender.QDirectionalLight(self.rootEntity)
        self.light.setWorldDirection(QVector3D(100,-100,-100))
        self.rootEntity.addComponent(self.light)

        self.picker = Qt3DRender.QObjectPicker(self.rootEntity)
        self.rootEntity.addComponent(self.picker)
        self.picker.clicked.connect(self.pickerTouch)

        self.press = None
        self.last_x = 0
        self.last_y = 0

        self.dx = 0
        self.dy = 0
        self.dz = 0
        self.scale = float(0)
        
        self.rxy = 0
        self.rz = 280

        self.updateMatrix()

        self._callback = None
    
    def pickerTouch(self, ev):
        e = ev.entity()
        if isinstance(e, BindingEntity):
            e.onClicked(ev)
    
    def updateMatrix(self):
        m = QMatrix4x4()
        m.scale(QVector3D(math.exp(self.scale), math.exp(self.scale), math.exp(self.scale)))
        m.rotate(self.rz, QVector3D(1,0,0))
        m.rotate(self.rxy, QVector3D(0,0,1))
        m.translate(self.dx, self.dy, self.dz)
        self.transform.setMatrix(m)
    
    def mousePressEvent(self, ev):
        if ev.button() == Qt.LeftButton:
            self.press = 'left'
        elif ev.button() == Qt.MiddleButton:
            self.press = 'middle'
        elif ev.button() == Qt.RightButton:
            self.press = 'right'
        else:
            self.press = None
        self.last_x = ev.x()
        self.last_y = ev.y()
        # print("press", self.last_x, self.last_y)
    
    def mouseReleaseEvent(self, ev):
        self.incUpdate(update=True)
        self.press = None

    def mouseMoveEvent(self, ev):
        if self.press is not None:
            if self.press == 'left':
                if ev.modifiers() & Qt.ControlModifier == 0:
                    self.rxy = (self.rxy + ev.x() - self.last_x) % 360
                    self.rz = (self.rz + ev.y() - self.last_y) % 360
                else:
                    xx = ev.x() - self.last_x
                    yy = ev.y() - self.last_y
                    if ev.modifiers() & Qt.AltModifier == 0:
                        self.incUpdate(rz=xx, rx=yy)
                    else:
                        self.incUpdate(ry=xx, rx=yy)
                # print(self.rxy, self.rz)
            elif self.press == 'middle':
                rr = self.rxy/360*2*math.pi
                xx = (ev.x() - self.last_x) * 0.5 * math.cos(rr) + \
                    (ev.y() - self.last_y) * 0.5 * (-math.sin(rr))
                yy = (ev.x() - self.last_x) * 0.5 * (-math.sin(rr)) + \
                    (ev.y() - self.last_y) * 0.5 * (-math.cos(rr))
                if ev.modifiers() & Qt.ControlModifier == 0:
                    self.dx += xx
                    self.dy += yy
                else:
                    self.incUpdate(dx=xx*0.5, dy=yy*0.5)
                # print(self.dx, self.dy)
            elif self.press == 'right':
                if ev.modifiers() & Qt.ControlModifier == 0:
                    self.dz -= (ev.y() - self.last_y) * 0.5
                else:
                    self.incUpdate(dz=(-(ev.y() - self.last_y) * 0.25))
            self.last_x = ev.x()
            self.last_y = ev.y()
            self.updateMatrix()
    
    def wheelEvent(self, ev):
        self.scale += ev.angleDelta().y() * 0.001
        # print(self.scale)
        self.updateMatrix()
    
    def incUpdate(self, **vargs):
        if self._callback is not None:
            self._callback(**vargs)
    
    def setCallback(self, fn):
        self._callback = fn