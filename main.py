import sys
import mysql.connector
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QBrush, QColor
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QHeaderView, QDateEdit, QLineEdit, QComboBox, QVBoxLayout, QWidget, QTableWidget, QTableWidgetItem, QPushButton, QMessageBox, QDialog, QHBoxLayout, QHeaderView
from main_functions import *
from table_functions import *

connect_to_database()  

# Główne okno aplikacji
class MainWindow(QMainWindow):

    def load_children(self):
        load_children(self)
    def show_absence_history(self, child_id):
        show_absence_history(self, child_id)
    def show_absence_dialog(self, child_id):
        show_absence_dialog(self, child_id)
    def add_absence(self, child_id, absence_date):
        add_absence(self, child_id, absence_date)
    def show_payment_history(self, child_id):
        show_payment_history(self, child_id)
    def show_payment_dialog(self, child_id):
        show_payment_dialog(self, child_id)
    def add_payment(self, child_id, payment_date, amount):
        add_payment(self, child_id, payment_date, amount)
    def show_edit_child_dialog(self, child_id):
        show_edit_child_dialog(self, child_id)
    def save_child_changes(self, child_id, first_name, last_name, group_id):
        save_child_changes(self, child_id, first_name, last_name, group_id)
    def handle_save_changes(self, child_id, first_name, last_name, group_id):
        self.save_child_changes(child_id, first_name, last_name, group_id)
    def show_add_group_dialog(self):
        show_add_group_dialog(self)
    def add_group(self, group_name):
        add_group(self, group_name)
    def show_add_child_dialog(self):
        show_add_child_dialog(self)
    
    def __init__(self):
        super().__init__()

        self.setWindowTitle("System rozliczeniowy dla Przedszkoli ver. 0.02")
        self.resize(800, 500)

        self.group_label = QLabel("Wybierz grupę:")
        self.group_combo_box = QComboBox()

        self.add_group_button = QPushButton("Dodaj grupę")
        self.add_group_button.clicked.connect(self.show_add_group_dialog)

        self.add_child_button = QPushButton("Dodaj dziecko")
        self.add_child_button.clicked.connect(self.show_add_child_dialog)

        self.group_combo_box.setFixedWidth(150)
        self.add_group_button.setFixedWidth(150)
        self.add_child_button.setFixedWidth(150)    

        self.child_table = QTableWidget(self)
        self.child_table.resizeColumnsToContents()




        
        load_groups(self)

        self.group_combo_box.currentIndexChanged.connect(self.load_children)

        #default_group_index = 1
        #self.group_combo_box.setCurrentIndex(default_group_index)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.group_combo_box)
        button_layout.addWidget(self.add_group_button)
        button_layout.addWidget(self.add_child_button)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignLeft) 

        layout = QVBoxLayout()
        layout.addWidget(self.group_label)
        layout.addLayout(button_layout)
        layout.addWidget(self.child_table)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        

    

    

# Uruchamianie aplikacji
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
