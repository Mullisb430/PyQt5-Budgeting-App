from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from operator import itemgetter

class BudgetItemModel(QtCore.QAbstractTableModel):
    def __init__(self, items):
        super().__init__()
        self.items = items
        
        self.income = ""

    def data(self, index, role):
        try:
            if role == Qt.DisplayRole:
                    return self.items[index.row()][index.column()]
        except Exception:
            return []

    def rowCount(self, index):
        try:
            return len(self.items)
        except:
            return 0

    def columnCount(self, index):
        try:
            return len(self.items[0])
        except:
            return 0

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        header = ['Name', 'Price']
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return f'{header[section]}'
        return super().headerData(section, orientation, role)