from sqlite3 import SQLITE_ANALYZE
import sys, json, random
from PyQt5.QtWidgets import QApplication, QMainWindow, QGridLayout, QWidget, QLineEdit, QLabel, QPushButton, QTableView, QMessageBox
from PyQt5 import QtGui
from PyQt5.QtGui import QColor
from PyQt5.QtChart import QChart, QChartView, QPieSeries, QPieSlice

from BudgetItemModel import BudgetItemModel
from operator import itemgetter



class Window(QMainWindow,):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My Budget")
        self.setGeometry(100, 100, 1200, 900)

        # Data list that is used to populate the Pie Chart
        self.data = []

        #Creating Window's Central Widget's layout
        self.layout = QGridLayout()

        # Creating Window's central widget and adding self.layout as it's layout
        widget = QWidget()
        widget.setLayout(self.layout)
        self.setCentralWidget(widget)

# ----- Add Item Form ------------------------------------------------------------------------------------------------- #
        # Monthly income label
        monthlyIncomeLabel = QLabel("Monthly Income: ")
        self.layout.addWidget(monthlyIncomeLabel, 0, 0, 1, 1)

        # Monthly income line edit
        self.monthlyIncomeField = QLineEdit()
        self.monthlyIncomeField.setMaximumSize(150, 30)
        self.layout.addWidget(self.monthlyIncomeField, 0, 1, 1, 1)

        self.monthlyIncomeField.textChanged.connect(self.setIncome)




        # Label for the line edit which tells the user to type an item to add to the pie chart
        budgetItemNameLabel = QLabel("Budget Item's Name: ")
        self.layout.addWidget(budgetItemNameLabel, 2, 0, 1, 1)

        # Line Edit in which the user can add a budget item to the pie chart
        self.budgetItemName = QLineEdit()
        self.budgetItemName.setMaximumSize(150, 30)
        self.layout.addWidget(self.budgetItemName, 2, 1, 1, 1)

        # Label for line edit which tell the user to type the items value that you want to add to pie chart
        budgetItemValueLabel = QLabel("Budget Item's Value: ")
        self.layout.addWidget(budgetItemValueLabel, 3, 0, 1, 1)

        # Line Edit in which the user can add a budget item value to the pie chart
        self.budgetItemValue = QLineEdit()
        self.budgetItemValue.setMaximumSize(150, 30)
        self.layout.addWidget(self.budgetItemValue, 3, 1, 1, 1)

        # Button to add the item that was typed in, into the pie chart
        self.addBudgetItemButton = QPushButton("Add Item")
        self.layout.addWidget(self.addBudgetItemButton, 4, 1, 1, 1)

        self.addBudgetItemButton.pressed.connect(self.addItem)
        self.budgetItemName.returnPressed.connect(self.addItem)
        self.budgetItemValue.returnPressed.connect(self.addItem)


# ----- Budget Item's Table View ----------------------------------------------------------------------------------------- #
        self.itemView = QTableView()
        self.model = BudgetItemModel(self.data)
        self.itemView.resizeColumnsToContents()
        self.itemView.setModel(self.model)
        self.layout.addWidget(self.itemView, 6, 0, 2, 2)
        self.sort()

        # Buttons for Item's Table View
        deleteButton = QPushButton("Delete")
        self.layout.addWidget(deleteButton, 8, 0, 1, 1)

        editButton = QPushButton("Edit")
        self.layout.addWidget(editButton, 8, 1, 1, 1)

        deleteButton.pressed.connect(self.deleteItem)
        editButton.pressed.connect(self.editItem)


# ----- Budget Item's labels, fields, buttons ---------------------------------------------------------------------------- #
        #Total line edit for budget item view
        totalLabel = QLabel("Budget Total: ")
        self.layout.addWidget(totalLabel, 9, 0, 1, 1)

        self.totalField = QLineEdit()
        self.totalField.setMaximumSize(150, 30)
        self.totalField.setReadOnly(True)
        self.layout.addWidget(self.totalField, 9, 1, 1, 1)

        # Income total label for comparison to budget total
        incomeLabel = QLabel("Monthly Income: ")
        self.layout.addWidget(incomeLabel, 10, 0, 1, 1)

        self.incomeField = QLineEdit()
        self.incomeField.setMaximumSize(150, 30)
        self.incomeField.setReadOnly(True)
        self.layout.addWidget(self.incomeField, 10, 1, 1, 1)

        # Income total minus the budget total to diplay money left over after expenses
        moneyLeftOverLabel = QLabel("Difference: ")
        self.layout.addWidget(moneyLeftOverLabel, 11, 0, 1, 1)

        self.differenceField = QLineEdit()
        self.differenceField.setMaximumSize(150, 30)
        self.differenceField.setReadOnly(True)
        self.layout.addWidget(self.differenceField, 11, 1, 1, 1)



# ----- Clear Budget Button and event method ---------------------------------------------------------------------------- #
        clearBudget = QPushButton("Clear Budget")
        clearBudget.setMinimumSize(120, 40)
        self.layout.addWidget(clearBudget, 13, 1, 1, 1)
        clearBudget.pressed.connect(self.clearBudget)

        # Populate the view and piechart with previously entered values
        self.load()
        self.getTotal()
        self.monthlyIncomeField.textChanged.connect(self.getTotal)

        # Populating and displaying pie chart
        self.createPieChart()



# ----- Creating The Pie Chart ----------------------------------------------------------------------------------------- #
    def createPieChart(self):
        series = QPieSeries()

        # Getting a font to set for each label on each slice in the pie chart
        sliceFont = QtGui.QFont()
        sliceFont.setPointSize(5)
        sliceFont.bold()

        # Getting a color for the label on each slice in the pie chart
        labelColor = QColor()
        labelColor.setNamedColor('White')
        
        # Iterating through self.data list and adding each tuple inside of it to the QPieSeries object
        if len(self.model.items) != 0:
            for dataPair in self.model.items:
                series.append(dataPair[0], float(dataPair[1][1::].replace(',', ''))).setBrush(QtGui.QColor(f"#{self.returnRandomHashColor()}"))
        else:
            series.append('', 100)

        # Getting each individual slice from the pie chart and placing in list
        slice = QPieSlice()
        slice.setLabelPosition(slice.LabelPosition.LabelInsideHorizontal)
        slices = series.slices()


        for slice_ in slices: 
            slice_.setLabelVisible(True)
            slice_.setLabelPosition(QPieSlice.LabelPosition.LabelInsideNormal)
            slice_.setLabelColor(labelColor)

        chart = QChart()
        chart.addSeries(series)
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.setTitle("Budget")

        chartView = QChartView(chart)

        self.layout.addWidget(chartView, 0, 2, 13, 13)
        self.getTotal()


# ----- Adding Item to Pie Chart ----------------------------------------------------------------------------------------- #
    def addItem(self):
        self.budgetItemName.setPlaceholderText("")
        self.budgetItemValue.setPlaceholderText("")
        if self.everythingIsValidated():
            newEntry = [self.budgetItemName.text(), "$" + "{:,.2f}".format(round(float(self.budgetItemValue.text().replace(',', '').replace('$', '')), 2))]
            self.model.items.append(newEntry)
            self.model.layoutChanged.emit()

            self.clear()
            self.createPieChart()
            self.getTotal()
            self.save()
        
            self.itemView.resizeColumnsToContents()

            self.budgetItemName.setFocus()
        else:
            self.invalidEntry()
            self.clear()



# ----- Deleting Item From Pie Chart ------------------------------------------------------------------------------------- #
    def deleteItem(self):
        indexes = self.itemView.selectedIndexes()

        if indexes:
            index = indexes[0]

            del self.model.items[index.row()]
            self.model.layoutChanged.emit()
            self.itemView.clearSelection()

            self.createPieChart()
            self.getTotal()
            self.save()


# ----- Edit Item From Pie Chart ---------------------------------------------------------------------------------------- #
    def editItem(self):
        indexes = self.itemView.selectedIndexes()

        if indexes:
            index = indexes[0]

            # Grabbing selected item from the view and putting them back in the add items form for the user to edit
            self.budgetItemName.setText(self.model.items[index.row()][0])
            self.budgetItemValue.setText(self.model.items[index.row()][1])

            # Deletes the patient from the view.
            del self.model.items[index.row()]
            self.model.layoutChanged.emit()
            self.itemView.clearSelection()

            self.createPieChart()
            self.getTotal()
            self.save()


# ----- Load Items From JSON ---------------------------------------------------------------------------------------- #
    def load(self):
        try:
            with open('budgetItems.json', 'r') as f:
                self.model.items = json.load(f)
                self.sort()
                self.getTotal()
                f.close()
            with open('monthlyIncome.json', 'r') as f:
                self.model.income = json.load(f)
                self.getTotal()
                f.close()
        except Exception:
            pass
        


# ----- Save Items Into JSON ---------------------------------------------------------------------------------------- #
    def save(self):
        with open('budgetItems.json', 'w') as f:
            items = json.dump(self.model.items, f)
            f.close()
        with open('monthlyIncome.json', 'w') as f:
            income = json.dump(self.model.income, f)
            f.close()
        


# ----- Validating Items ---------------------------------------------------------------------------------------- #
    def everythingIsValidated(self):
        try:
            if len(self.budgetItemName.text()) > 0:
                if self.budgetItemName.text()[0].isalnum() and float(self.budgetItemValue.text().replace('$', '').replace(',', '')) and float(self.monthlyIncomeField.text().replace('$', '').replace(',', '')):
                    return True
                else:
                    return False
            else:
                return False
        except:
            self.clear()
            self.invalidEntry()
            return False
        


# ----- Populated Total ---------------------------------------------------------------------------------------- #  
    def getTotal(self):
        total = 0
        for number in self.model.items:
            total += float(number[1][1:].replace(',', ''))
        
        self.totalField.setText("$" + "{:,.2f}".format(total))
        self.monthlyIncomeField.setText(self.model.income)


        # This try-except block will test if the monthly income field can be converted into a float. If not it will set the difference and income field below the table view to $0.00
        try:
            self.incomeField.setText("$" + "{:,.2f}".format(float(self.monthlyIncomeField.text())))
            self.differenceField.setText("$" + "{:,.2f}".format(
                (float(self.incomeField.text().replace('$', '').replace(',', '')) - 
                (float(self.totalField.text().replace('$', '').replace(',', ''))
                ))))

            if '-' in self.differenceField.text():
                self.differenceField.setStyleSheet("color: red;")
            else:
                self.differenceField.setStyleSheet("color: green;")

        except:
            self.differenceField.setText("$0.00")
            self.incomeField.setText("$0.00")
        


# ----- Clear Forms ---------------------------------------------------------------------------------------- #
    def clear(self):
        self.budgetItemName.setText("")
        self.budgetItemValue.setText("")
        


# ----- Invalid Entry ---------------------------------------------------------------------------------------- #
    def invalidEntry(self):
        self.addBudgetItemButton.setFocus()
        self.budgetItemName.setPlaceholderText("Letters or Numbers")
        self.budgetItemValue.setPlaceholderText("Must be Numbers")
        


# ----- Random Hash Color ---------------------------------------------------------------------------------------- #
    def returnRandomHashColor(self):
        return f"{random.randint(100000, 999999)}".replace(f'{random.randint(0, 9)}', 'a')
        


# ----- Clear Budget ---------------------------------------------------------------------------------------- #
    def clearBudget(self):
        qm = QMessageBox()
        ret = qm.question(self, '', 'Are you sure you want to clear the budget?', qm.Yes | qm.No)

        if ret == qm.Yes:
            with open('budgetItems.json', 'w') as f:
                items = json.dump([], f)
            self.model.items = []
            self.itemView.setModel(self.model)
            self.model.layoutChanged.emit()
            self.createPieChart()


# ----- Clear Budget ---------------------------------------------------------------------------------------- #
    def setIncome(self):
        self.model.income = self.monthlyIncomeField.text()
        self.save()


# ----- Sorting Budget Items by value descending  ----------------------------------------------------------------------- #
    def sort(self):
        # Makes the budget items list's first index value a float, so that the list is sortable by a float value
        self.model.items = [[i[0], float(i[1][1::])] for i in self.model.items]

        # Sorts the list based on the list's first index value which is a float
        self.model.items = sorted(self.model.items, key=itemgetter(1))

        # Now that the list is sorted based on the first index's value, the below statement makes the first index value a string again. Also the below statement reverses the sorted list so that the list is sorted by the first index's value in descending order.
        self.model.items = [[i[0], str("$" + "{:,.2f}".format(round(i[1], 2)))] for i in self.model.items[::-1]]

        

    

app = QApplication(sys.argv)
window = Window()
window.show()
sys.exit(app.exec())