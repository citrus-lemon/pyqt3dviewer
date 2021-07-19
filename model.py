from PySide2.QtCore import QObject, Qt, QUrl
from PySide2.Qt3DCore import Qt3DCore
from PySide2.Qt3DExtras import Qt3DExtras
from PySide2.Qt3DRender import (Qt3DRender)
from PySide2.QtGui import QMatrix4x4, QQuaternion, QVector3D, QColor
import os
import json
import pprint
pp = pprint.PrettyPrinter(indent=2).pprint

def inject_generic_repr(cls):
    """ Injects a generic repr function """
    def generic_repr(that):
        class_items = [f'{k}={v}' for k, v in that.__dict__.items()
            if k not in ['entity', 'transform', 'mesh', 'meterial']]
        return f'<{that.__class__.__name__} ' + ', '.join(class_items) + '>'

    cls.__repr__ = generic_repr
    return cls

class BindingEntity(Qt3DCore.QEntity):
    def __init__(self, *args):
        super().__init__(*args)
        self.idnum = 0
        self._callback = None
    
    def setCallback(self, fn):
        self._callback = fn
    
    def onClicked(self, ev):
        print("clicked", self.idnum)

@inject_generic_repr
class DataObject():
    def __init__(self):
        self.name = None
        self.type = None
        self.idnum = 0
        self.parent = 0
        self.entity = None
    
    def setName(self, _name):
        self.name = _name

    def destroy(self):
        pass

    def assignID(self, _id):
        self.idnum = _id

@inject_generic_repr
class RootObject(DataObject):
    def __init__(self):
        super().__init__()
        self.name = "root"
        self.type = "root"
        self.children = []
        self.parent = None
        self.entity = Qt3DCore.QEntity()
    
    def destroy(self):
        raise RuntimeError("Root cannot be destroyed")

@inject_generic_repr
class EntityObject(DataObject):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.type = "entity"
        self.shape = None
        self.entity = BindingEntity()
        self.transform = Qt3DCore.QTransform()
        self.meterial = Qt3DExtras.QPhongMaterial(self.entity)
        self.dx = 0
        self.dy = 0
        self.dz = 0
        self.rx = 0
        self.ry = 0
        self.rz = 0
        self.color = (0, 0, 0)

        self.meterial.setDiffuse(QColor(*self.color, 255))

        self.entity.addComponent(self.transform)
        self.entity.addComponent(self.meterial)
    
    def assignID(self, _id):
        super().assignID(_id)
        self.entity.idnum = _id
    
    def setCallback(self, fn):
        self.entity.setCallback(fn)
    
    def applyTransform(self):
        t = Qt3DCore.QTransform()
        t.rotate(self.rx, axis=Qt.XAxis)
        t.rotate(self.ry, axis=Qt.YAxis)
        t.rotate(self.rz, axis=Qt.ZAxis)
        self.transform.setMatrix(t.m11(), t.m12(), t.m13(), t.m21(), t.m22(), t.m23(), t.m31(), t.m32(), t.m33())
    
    def setTrans(self, dx=None, dy=None, dz=None):
        if dx is not None:
            self.dx = dx
        if dy is not None:
            self.dy = dy
        if dz is not None:
            self.dz = dz
        self.transform.setTranslation(QVector3D(self.dx, self.dy, self.dz))
    
    def setRotate(self, rx=None, ry=None, rz=None):
        if rx is not None:
            self.rx = rx
        if ry is not None:
            self.ry = ry
        if rz is not None:
            self.rz = rz
        # self.applyTransform()
        self.transform.setRotationX(self.rx)
        self.transform.setRotationY(self.ry)
        self.transform.setRotationZ(self.rz)
    
    def setColor(self, r, g, b):
        self.color = (r, g, b)
        self.meterial.setDiffuse(QColor(*self.color, 255))
    
    def setParent(self, _id, par):
        self.parent = _id
        self.entity.setParent(par.entity)
        par.children.append(self.idnum)
    
    def destroy(self, data=None):
        self.entity.setParent(None)
        if self.parent is not None:
            data[self.parent].children.remove(self.idnum)

@inject_generic_repr
class BoxObject(EntityObject):
    def __init__(self, name):
        super().__init__(name)
        self.shape = "box"
        self.length = 5
        self.width  = 5
        self.height = 5
        self.mesh = Qt3DExtras.QCuboidMesh()
        self.mesh.setXExtent(self.length)
        self.mesh.setYExtent(self.width)
        self.mesh.setZExtent(self.height)
        self.entity.addComponent(self.mesh)
    
    def setSize(self, l=None, w=None, h=None):
        if l is not None:
            self.length = l
        if w is not None:
            self.width = w
        if h is not None:
            self.height = h
        self.mesh.setXExtent(self.length)
        self.mesh.setYExtent(self.width)
        self.mesh.setZExtent(self.height)

@inject_generic_repr
class SphereObject(EntityObject):
    def __init__(self, name):
        super().__init__(name)
        self.shape = "sphere"
        self.radius = 5
        self.mesh = Qt3DExtras.QSphereMesh()
        self.mesh.setRadius(self.radius)
        self.entity.addComponent(self.mesh)
    
    def setRadius(self, r):
        self.radius = r
        self.mesh.setRadius(self.radius)

@inject_generic_repr
class STLObject(EntityObject):
    def __init__(self, name):
        super().__init__(name)
        self.shape = "stl"
        self.url = None
        self.mesh = None
        self.scale = 1
    
    def setURL(self, _url):
        if _url is None:
            return
        self.mesh = Qt3DRender.QMesh()
        self.mesh.setSource(QUrl.fromLocalFile(_url))
        self.entity.addComponent(self.mesh)
        self.url = _url
    
    def setScale(self, s):
        self.scale = s
        self.transform.setScale(s)

@inject_generic_repr
class GroupObject(DataObject):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.type = "group"
        self.entity = None
        raise NotImplementedError("GroupObject")

class DataModel(QObject):
    def __init__(self):
        self._data = {}
        self._sel = 0
        self._no = 0

        self._update_tree_callback = None
        self._update_detail_callback = None

        self.initData()

        self._stack = []
    
    def assignCallback(self, s, fn):
        if s == "tree":
            self._update_tree_callback = fn
            self.updateTree()
        elif s == "detail":
            self._update_detail_callback = fn
            self.updateDetail()
    
    def initData(self):
        self._data[0] = RootObject()
        if os.path.exists(os.path.expanduser("~/.pyqt3dviewer/data.json")):
            print("load from file")
            data = json.load(open(os.path.expanduser("~/.pyqt3dviewer/data.json")))
            for entry in data:
                self.loadData(entry, 0)
    
    def loadData(self, data, parent):
        if data["type"] == "entity":
            self._no += 1
            if data["shape"] == "box":
                el = BoxObject(data["name"])
                self._data[self._no] = el
                el.assignID(self._no)
                el.setParent(parent, self._data[parent])
                el.setTrans(*data["pos"][:3])
                el.setRotate(*data["pos"][3:])
                el.setColor(*data["color"])
                el.setSize(*data["size"])
            elif data["shape"] == "sphere":
                el = SphereObject(data["name"])
                self._data[self._no] = el
                el.assignID(self._no)
                el.setParent(parent, self._data[parent])
                el.setTrans(*data["pos"][:3])
                el.setRotate(*data["pos"][3:])
                el.setColor(*data["color"])
                el.setRadius(*data["size"])
            elif data["shape"] == "stl":
                el = STLObject(data["name"])
                self._data[self._no] = el
                el.assignID(self._no)
                el.setParent(parent, self._data[parent])
                el.setTrans(*data["pos"][:3])
                el.setRotate(*data["pos"][3:])
                el.setColor(*data["color"])
                el.setScale(data["scale"])
                el.setURL(data["url"])
        elif data["type"] == "group":
            raise NotImplementedError("Group load")
    
    def dumpData(self, i):
        if i == 0:
            return [self.dumpData(j) for j in self._data[0].children]
        rst = {}
        el = self._data[i]
        rst["name"] = el.name
        if el.type == "entity":
            rst["type"] = "entity"
            rst["pos"] = [el.dx, el.dy, el.dz, el.rx, el.ry, el.rz]
            rst["color"] = list(el.color)
            if el.shape == "box":
                rst["shape"] = "box"
                rst["size"] = [el.length, el.width, el.height]
            elif el.shape == "sphere":
                rst["shape"] = "sphere"
                rst["size"] = [el.radius]
            elif el.shape == "stl":
                rst["shape"] = "stl"
                rst["scale"] = el.scale
                rst["url"] = el.url
            else:
                rst["shape"] = el.shape
        elif el.type == "group":
            raise NotImplementedError("Group dump")
        return rst
    
    def dumpToFile(self):
        os.makedirs(os.path.expanduser("~/.pyqt3dviewer"), exist_ok=True)
        fp = open(os.path.expanduser("~/.pyqt3dviewer/data.json"), "w")
        json.dump(self.dumpData(0), fp)
        fp.close()
    
    def addShape(self, shape):
        self._no += 1
        name = "{} {}".format(shape, self._no)
        if shape == 'sphere':
            self._data[self._no] = SphereObject(name)
        elif shape == 'box':
            self._data[self._no] = BoxObject(name)
        elif shape == 'stl':
            self._data[self._no] = STLObject(name)
        self._data[self._no].assignID(self._no)
        self._data[self._no].setParent(0, self._data[0])
        pp(self._data)
        self.updateTree()
        self.dumpToFile()
    
    def delShape(self, _id=None):
        if _id is None:
            _id = self._sel
        if _id != 0:
            el = self._data[_id]
            el.destroy(self._data)
            del self._data[_id]
            self._sel = 0
            self.updateDetail()
            self.updateTree()
            self.dumpToFile()

    def selectElement(self, _id):
        self._sel = int(_id)
        self.updateDetail()

    def setValue(self, _id, **vargs):
        if _id != 0:
            if "name" in vargs:
                self._data[_id].setName(vargs["name"])
                self.updateTree()
            
            if self._data[_id].type == 'entity':
                do_translate = False
                dx, dy, dz = None, None, None
                if "dx" in vargs:
                    do_translate = True
                    dx = vargs["dx"]
                if "dy" in vargs:
                    do_translate = True
                    dy = vargs["dy"]
                if "dz" in vargs:
                    do_translate = True
                    dz = vargs["dz"]
                if do_translate:
                    self._data[_id].setTrans(dx, dy, dz)
                
                do_rotate = False
                rx, ry, rz = None, None, None
                if "rx" in vargs:
                    do_rotate = True
                    rx = vargs["rx"]
                if "ry" in vargs:
                    do_rotate = True
                    ry = vargs["ry"]
                if "rz" in vargs:
                    do_rotate = True
                    rz = vargs["rz"]
                if do_rotate:
                    self._data[_id].setRotate(rx, ry, rz)
                
                if "color" in vargs:
                    self._data[_id].setColor(*vargs["color"])

                if self._data[_id].shape == "box":
                    do_change = False
                    l, w, h = None, None, None
                    if "length" in vargs:
                        do_change = True
                        l = vargs["length"]
                    if "width" in vargs:
                        do_change = True
                        w = vargs["width"]
                    if "height" in vargs:
                        do_change = True
                        h = vargs["height"]
                    if do_change:
                        self._data[_id].setSize(l, w, h)
                
                if self._data[_id].shape == "sphere" and "radius" in vargs:
                    self._data[_id].setRadius(vargs["radius"])
                
                if self._data[_id].shape == "stl":
                    if "url" in vargs:
                        self._data[_id].setURL(vargs["url"])
                    if "scale" in vargs:
                        self._data[_id].setScale(vargs["scale"])

            self.dumpToFile()
            self.updateDetail()

    def updateDetail(self):
        if self._update_detail_callback is not None:
            self._update_detail_callback(self._sel, self._data[self._sel])
    
    def updateTree(self):
        if self._update_tree_callback is not None:
            self._update_tree_callback(self._data, self._sel)

    def getRootEntity(self):
        return self._data[0].entity
    
    def incUpdate(self, **vargs):
        if self._sel != 0 and self._data[self._sel].type == "entity":
            el = self._data[self._sel]

            do_translate = False
            dx, dy, dz = None, None, None
            if "dx" in vargs:
                do_translate = True
                dx = vargs["dx"] + el.dx
            if "dy" in vargs:
                do_translate = True
                dy = vargs["dy"] + el.dy
            if "dz" in vargs:
                do_translate = True
                dz = vargs["dz"] + el.dz
            if do_translate:
                el.setTrans(dx, dy, dz)
            
            do_rotate = False
            rx, ry, rz = None, None, None
            if "rx" in vargs:
                do_rotate = True
                rx = (vargs["rx"] + el.rx + 180) % 360 - 180
            if "ry" in vargs:
                do_rotate = True
                ry = (vargs["ry"] + el.ry + 180) % 360 - 180
            if "rz" in vargs:
                do_rotate = True
                rz = (vargs["rz"] + el.rz + 180) % 360 - 180
            if do_rotate:
                el.setRotate(rx, ry, rz)
            
            if "update" in vargs:
                self.updateDetail()
                self.dumpToFile()
    
    def recordChange(self):
        pass

    def undoChange(self):
        pass

    def redoChange(self):
        pass