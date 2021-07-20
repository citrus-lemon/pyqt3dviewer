from PySide2.QtCore import(Property, QObject, QPropertyAnimation, Signal, Qt)
from PySide2.QtWidgets import *

class TreeView(QTreeWidget):
    def __init__(self):
        super().__init__()
        self.setHeaderHidden(True)
        self.itemPressed.connect(self.itemChange)
        self._sel_element_callback = None
    
    def setCallback(self, fn):
        self._sel_element_callback = fn
    
    def itemChange(self, it):
        if self._sel_element_callback is not None:
            self._sel_element_callback(int(it.text(1)))
    
    def updateData(self, data, sel=0):
        self.clear()
        def item(i):
            it = QTreeWidgetItem([data[i].name, str(i)])
            if i == sel:
                it.setSelected(True)
            if data[i].type == "group":
                for c in data[i].children:
                    it.addChild(item(c))
            return it
        for c in data[0].children:
            self.addTopLevelItem(item(c))
        # self.update()