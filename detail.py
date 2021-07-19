from PySide2.QtCore import(Property, QObject, QPropertyAnimation, Signal)
from PySide2.QtWidgets import *

class ObjectDetail(QVBoxLayout):
    def __init__(self):
        super().__init__()
        self._name_detail = QWidget()
        self._prop = QFormLayout()
        self._name_detail.setLayout(self._prop)
        self._name = QLineEdit()
        self._name.textChanged.connect(self.callback("name"))
        self._prop.addRow(self.tr("Name:"), self._name)
        self.addWidget(self._name_detail)

        self._co_detail = QGroupBox()
        self._co_detail.setTitle("Coordiante")
        self._co_layout = QHBoxLayout()
        self._co_detail.setLayout(self._co_layout)
        self._translate_layout = QFormLayout()
        self._rotate_layout = QFormLayout()
        self._co_layout.addLayout(self._translate_layout)
        self._co_layout.addLayout(self._rotate_layout)
        self.addWidget(self._co_detail)

        self._translate_control = {}
        for d in "xyz":
            w = QDoubleSpinBox()
            w.setRange(-1000, 1000)
            w.valueChanged.connect(self.callback("d" + d))
            self._translate_layout.addRow(self.tr("d" + d + ":"), w)
            self._translate_control[d] = w
        
        self._rotate_control = {}
        for d in "xyz":
            w = QDoubleSpinBox()
            w.setRange(-180, 180)
            w.setSingleStep(5)
            w.valueChanged.connect(self.callback("r" + d))
            self._rotate_layout.addRow(self.tr("r" + d + ":"), w)
            self._rotate_control[d] = w

        self._color_detail = QGroupBox()
        self._color_detail.setTitle("Color")
        self._color_layout = QHBoxLayout()
        self._color_detail.setLayout(self._color_layout)
        self._color_control = {}
        for c in "rgb":
            f = QFormLayout()
            w = QSpinBox()
            w.setRange(0, 255)
            f.addRow(self.tr(c + ":"), w)
            w.valueChanged.connect(
                lambda: self.callback("color")((*[
                    self._color_control[cc][1].value() for cc in "rgb" ],)))
            self._color_control[c] = (f, w)
            self._color_layout.addLayout(f)
        self.addWidget(self._color_detail)

        self._box_detail = QGroupBox()
        self._box_detail.setTitle("Box")
        self._box_form = QFormLayout()
        self._box_detail.setLayout(self._box_form)
        self._box_control = {}
        for l in ["length", "width", "height"]:
            w = QDoubleSpinBox()
            w.setRange(0.1, 100)
            w.setValue(5)
            w.valueChanged.connect(self.callback(l))
            self._box_form.addRow(self.tr(l + ":"), w)
            self._box_control[l] = w
        self.addWidget(self._box_detail)
        
        self._sphere_detail = QGroupBox()
        self._sphere_detail.setTitle("Sphere")
        self._sphere_form = QFormLayout()
        self._sphere_detail.setLayout(self._sphere_form)
        self._sphere_radius = QDoubleSpinBox()
        self._sphere_radius.setRange(0.1, 100)
        self._sphere_radius.setValue(5)
        self._sphere_radius.valueChanged.connect(self.callback("radius"))
        self._sphere_form.addRow(self.tr("radius:"), self._sphere_radius)
        self.addWidget(self._sphere_detail)

        self._stl_detail = QGroupBox()
        self._stl_detail.setTitle("STL")
        self._stl_layout = QVBoxLayout()
        self._stl_detail.setLayout(self._stl_layout)
        self._stl_button = QPushButton("Open STL File")
        self._stl_button.clicked.connect(self.stlOpenFile)
        self._stl_layout.addWidget(self._stl_button)
        self.addWidget(self._stl_detail)

        self._name_detail.hide()
        self._co_detail.hide()
        self._color_detail.hide()
        self._box_detail.hide()
        self._sphere_detail.hide()
        self._stl_detail.hide()

        self._sel = 0
        self._callback = None
    
    def setCallback(self, fn):
        self._callback = fn
        
    def updateValue(self, sel, data):
        self._sel = 0
        if data.type == "entity":
            self._name_detail.show()
            self._co_detail.show()
            self._color_detail.show()

            self._name.setText(data.name)
            self._translate_control["x"].setValue(data.dx)
            self._translate_control["y"].setValue(data.dy)
            self._translate_control["z"].setValue(data.dz)
            self._rotate_control["x"].setValue(data.rx)
            self._rotate_control["y"].setValue(data.ry)
            self._rotate_control["z"].setValue(data.rz)
            r, g, b = data.color
            self._color_control["r"][1].setValue(r)
            self._color_control["g"][1].setValue(g)
            self._color_control["b"][1].setValue(b)
            
            if data.shape == "box":
                self._box_detail.show()
                self._sphere_detail.hide()
                self._stl_detail.hide()
                self._box_control["length"].setValue(data.length)
                self._box_control["width" ].setValue(data.width)
                self._box_control["height"].setValue(data.height)
            elif data.shape == 'sphere':
                self._box_detail.hide()
                self._sphere_detail.show()
                self._stl_detail.hide()
                self._sphere_radius.setValue(data.radius)
            elif data.shape == 'stl':
                self._box_detail.hide()
                self._sphere_detail.hide()
                self._stl_detail.show()
            else:
                self._box_detail.hide()
                self._sphere_detail.hide()

        else:
            self._name_detail.hide()
            self._co_detail.hide()
            self._color_detail.hide()
            self._box_detail.hide()
            self._sphere_detail.hide()
        self._sel = sel

    def callback(self, field):
        def fn(value):
            if self._sel != 0:
                if self._callback is not None:
                    self._callback(self._sel, **{ field: value })
        return fn
    
    def stlOpenFile(self):
        print("stl open file")
        fname = QFileDialog.getOpenFileName(None, "Open file", "", "STL (*.stl)")
        print(fname)
        if fname[0] != '':
            self.callback("url")(fname[0])