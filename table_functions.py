from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QHeaderView, QDateEdit, QLineEdit, QComboBox, QVBoxLayout, QWidget, QTableWidget, QTableWidgetItem, QPushButton, QMessageBox, QDialog, QHBoxLayout, QHeaderView
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QBrush, QColor
from functools import partial
from main_functions import *

def load_groups(self):
        groups = get_groups()
        self.group_combo_box.clear()
        for group in groups:
            self.group_combo_box.addItem(group[1], group[0])
        self.update()
def get_groups():
    connection = connect_to_database()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM Groups")
    groups = cursor.fetchall()

    connection.close()
    return groups


def load_children(MainWindow):
    
    group_id = MainWindow.group_combo_box.currentData()
    children = get_children_with_balances(group_id)

    MainWindow.child_table.clear()
    MainWindow.child_table.setColumnCount(8)
    MainWindow.child_table.setHorizontalHeaderLabels(["Imię", "Nazwisko", "Saldo", "Nieobecności", "Dodaj nieobecność", "Historia wpłat", "Wpłaty", "Edycja"])
    header_font = MainWindow.child_table.horizontalHeader().font()
    header_font.setBold(True)
    MainWindow.child_table.horizontalHeader().setFont(header_font)
    #header = self.child_table.horizontalHeader()
    #header.setStyleSheet("QHeaderView::section { background-color: lightgray; }")


    if children:
        MainWindow.child_table.setRowCount(len(children))
        for row, child in enumerate(children):
            child_id = child[0]
            first_name = child[1]
            last_name = child[2]
            balance = child[3]

            item_first_name = QTableWidgetItem(first_name)
            item_last_name = QTableWidgetItem(last_name)
            item_balance = QTableWidgetItem()


            if balance is not None:
                item_balance.setData(Qt.ItemDataRole.DisplayRole, f"{balance:.2f} zł")
                if balance < 0:
                    item_balance.setForeground(QBrush(QColor("red")))
                elif balance > 0:
                    item_balance.setForeground(QBrush(QColor("green")))
                else:
                    item_balance.setForeground(QBrush(QColor("black")))
            else:
                item_balance.setData(Qt.ItemDataRole.DisplayRole, "")

            button_abscence = QPushButton("Nieobecności")
            button_abscence.clicked.connect(partial(MainWindow.show_absence_history, child_id))
            button_abscence.setStyleSheet("border: none;")

            button_add_abscence = QPushButton("Dodaj nieobecność")
            button_add_abscence.clicked.connect(partial(MainWindow.show_absence_dialog, child_id))
            button_add_abscence.setStyleSheet("border: none;")


            button_history = QPushButton("Historia wpłat")
            button_history.clicked.connect(partial(MainWindow.show_payment_history, child_id))
            button_history.setStyleSheet("border: none;")


            button_pay = QPushButton("Wpłać")
            button_pay.clicked.connect(partial(MainWindow.show_payment_dialog, child_id))
            button_pay.setStyleSheet("border: none;")


            button_modify = QPushButton("Edytuj")
            button_modify.clicked.connect(partial(MainWindow.show_edit_child_dialog, child_id))
            button_modify.setStyleSheet("border: none;")


            MainWindow.child_table.setItem(row, 0, item_first_name)
            MainWindow.child_table.setItem(row, 1, item_last_name)
            MainWindow.child_table.setItem(row, 2, item_balance)
            MainWindow.child_table.setCellWidget(row, 3, button_abscence)
            MainWindow.child_table.setCellWidget(row, 4, button_add_abscence)
            MainWindow.child_table.setCellWidget(row, 5, button_history)
            MainWindow.child_table.setCellWidget(row, 6, button_pay)
            MainWindow.child_table.setCellWidget(row, 7, button_modify)

        MainWindow.child_table.resizeColumnsToContents()
    else:
        MainWindow.child_table.setRowCount(0)

def show_payment_history(self, child_id):
    connection = connect_to_database()
    cursor = connection.cursor()

    cursor.execute("SELECT payment_date, amount FROM Payments WHERE child_id = %s ORDER BY payment_date DESC", (child_id,))
    history = cursor.fetchall()

    cursor.execute("SELECT SUM(amount) FROM Payments WHERE child_id = %s", (child_id,))
    total_amount = cursor.fetchone()[0]

    connection.close()

    if history:
        message = "Historia wpłat:\n\n"
        for entry in history:
            payment_date = entry[0].strftime("%Y-%m-%d")
            amount = entry[1]
            message += f"{payment_date}: {amount:.2f} zł\n"

        message += f"\nSUMA: {total_amount:.2f} zł"

        QMessageBox.information(self, "Historia wpłat", message)
    else:
        QMessageBox.information(self, "Historia wpłat", "Brak wpłat dla tego dziecka.")

def show_payment_dialog(self, child_id):
    dialog = QDialog(self)
    dialog.setWindowTitle("Dodaj wpłatę")

    layout = QVBoxLayout()
    dialog.setLayout(layout)

    label_date = QLabel("Data:")
    date_edit = QDateEdit()
    date_edit.setCalendarPopup(True)
    date_edit.setDate(QDate.currentDate())

    label_amount = QLabel("Kwota:")
    amount_edit = QLineEdit()

    button_add_payment = QPushButton("Dodaj")
    button_add_payment.clicked.connect(lambda: self.add_payment(child_id, date_edit.date().toString("yyyy-MM-dd"), amount_edit.text()))

    layout.addWidget(label_date)
    layout.addWidget(date_edit)
    layout.addWidget(label_amount)
    layout.addWidget(amount_edit)
    layout.addWidget(button_add_payment)

    dialog.exec()

def add_payment(self, child_id, payment_date, amount):
    connection = connect_to_database()
    cursor = connection.cursor()

    query = "INSERT INTO Payments (child_id, payment_date, amount) VALUES (%s, %s, %s)"
    values = (child_id, payment_date, amount)

    cursor.execute(query, values)
    connection.commit()

    connection.close()

    QMessageBox.information(self, "Dodawanie wpłaty", "Wpłata została dodana.")

    self.load_children()

def show_edit_child_dialog(MainWindow, child_id):
    dialog = QDialog(MainWindow)
    dialog.setWindowTitle("Edytuj dziecko")

    layout = QVBoxLayout()
    dialog.setLayout(layout)

    # Pobierz dane dziecka na podstawie child_id (np. z bazy danych)
    child_data = get_child_data(MainWindow, child_id)

    # Pola do edycji danych
    label_first_name = QLabel("Imię:")
    first_name_edit = QLineEdit()
    first_name_edit.setText(child_data["first_name"])

    label_last_name = QLabel("Nazwisko:")
    last_name_edit = QLineEdit()
    last_name_edit.setText(child_data["last_name"])

    label_group = QLabel("Grupa:")
    group_combo_box = QComboBox()
    groups = get_groups()
    for group in groups:
        group_combo_box.addItem(group[1], group[0])
    group_combo_box.setCurrentIndex(group_combo_box.findData(child_data["group_id"]))

    button_save_changes = QPushButton("Zapisz zmiany")
    button_save_changes.clicked.connect(lambda: MainWindow.handle_save_changes(child_id, first_name_edit.text(), last_name_edit.text(), group_combo_box.currentData()))

    layout.addWidget(label_first_name)
    layout.addWidget(first_name_edit)
    layout.addWidget(label_last_name)
    layout.addWidget(last_name_edit)
    layout.addWidget(label_group)
    layout.addWidget(group_combo_box)
    layout.addWidget(button_save_changes)

    dialog.exec()


# Funkcja do pobierania danych dziecka na podstawie child_id (może być np. zapytanie do bazy danych)
def get_child_data(self, child_id):
    connection = connect_to_database()
    cursor = connection.cursor()

    query = "SELECT first_name, last_name, group_id FROM Children WHERE child_id = %s"
    cursor.execute(query, (child_id,))
    child_data = cursor.fetchone()

    connection.close()

    return {
        "first_name": child_data[0],
        "last_name": child_data[1],
        "group_id": child_data[2]
    }

def save_child_changes(self, child_id, first_name, last_name, group_id):
    connection = connect_to_database()
    cursor = connection.cursor()
    
    query = "UPDATE Children SET first_name = %s, last_name = %s, group_id = %s WHERE child_id = %s"
    values = (first_name, last_name, group_id, child_id)
    cursor.execute(query, values)

    connection.commit()  # Zatwierdzenie zmian w bazie danych
    connection.close()

    QMessageBox.information(self, "Edycja danych dziecka", "Zmiany dokonane.")

    self.load_children()


# Historia nieobecnosci
def show_absence_history(self, child_id):
    connection = connect_to_database()
    cursor = connection.cursor()

    cursor.execute("SELECT absence_date FROM Absences WHERE child_id = %s ORDER BY absence_date DESC", (child_id,))
    absences = cursor.fetchall()

    cursor.execute("SELECT COUNT(absence_date) FROM Absences WHERE child_id = %s", (child_id,))
    total_days = cursor.fetchone()[0]

    connection.close()

    if absences:
        message = "Nieobecności:\n\n"
        for entry in absences:
            absence_date = entry[0].strftime("%Y-%m-%d")
            message += f"{absence_date}\n"
        message += f"\nSUMA dni nieobecności: {total_days}"

        QMessageBox.information(self, "Nieobecności", message)
    else:
        QMessageBox.information(self, "Nieobecności", "Brak nieobecności dla tego dziecka.")
def show_absence_dialog(self, child_id):
    dialog = QDialog(self)
    dialog.setWindowTitle("Dodaj nieobecność")
    dialog.resize(170, 100)

    layout = QVBoxLayout(dialog)

    label_date = QLabel("Data:")
    date_edit = QDateEdit()
    date_edit.setCalendarPopup(True)
    date_edit.setDate(QDate.currentDate())

    button_add_absence = QPushButton("Dodaj")
    button_add_absence.clicked.connect(lambda: self.add_absence(child_id, date_edit.date().toString("yyyy-MM-dd")))
    
    layout.addWidget(label_date)
    layout.addWidget(date_edit)
    layout.addWidget(button_add_absence)

    dialog.exec()
def add_absence(self, child_id, absence_date):
    connection = connect_to_database()
    cursor = connection.cursor()

    # Sprawdzenie, czy nieobecność już istnieje dla danego dnia
    check_query = "SELECT * FROM Absences WHERE child_id = %s AND absence_date = %s"
    cursor.execute(check_query, (child_id, absence_date))
    existing_absence = cursor.fetchone()

    if existing_absence:
        QMessageBox.warning(self, "Dodawanie nieobecności", "Nieobecność w tym dniu została już dodana.\nPodaj inną datę.")
    else:
        insert_query = "INSERT INTO Absences (child_id, absence_date) VALUES (%s, %s)"
        values = (child_id, absence_date)
        cursor.execute(insert_query, values)
        connection.commit()

        QMessageBox.information(self, "Dodawanie nieobecności", "Nieobecność dodana.")

    connection.close()

    self.load_children()

def show_add_group_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Dodaj grupę")
        dialog.resize(170, 100)

        layout = QVBoxLayout(dialog)

        group_name_edit = QLineEdit()
        layout.addWidget(group_name_edit)
        
        button_add_group = QPushButton("Dodaj")
        #button_add_group.clicked.connect(lambda: MainWindow.add_group(group_name_edit.text(), dialog))
        #button_add_group.clicked.connect(lambda: self.add_group(group_name_edit.text(), dialog))
        #button_add_group.clicked.connect(lambda: add_group(group_name_edit.text(), dialog))
        button_add_group.clicked.connect(lambda: self.add_group(group_name_edit.text(), dialog))

        #button_add_group.clicked.connect(partial(MainWindow.add_group(group_name_edit.text(), dialog)))

        layout.addWidget(button_add_group)

        dialog.exec()

def add_group(self, group_name, dialog):
    connection = connect_to_database()
    cursor = connection.cursor()

    query = "INSERT INTO Groups (group_name) VALUES (%s)"
    values = (group_name,)
    
    cursor.execute(query, values)
    connection.commit()
    connection.close()

    dialog.close()  # Zamykanie okna dialogowego po dodaniu grupy

    QMessageBox.information(self, "Dodawanie grupy", f"Dodano grupę: {group_name}")

    self.load_groups()  # Przeładuj dostępne grupy w interfejsie

def show_add_child_dialog(self):
    dialog = QDialog(self)
    dialog.setWindowTitle("Dodaj dziecko")
    dialog.resize(300, 200)

    layout = QVBoxLayout(dialog)

    label_first_name = QLabel("Imię:")
    first_name_edit = QLineEdit()
    layout.addWidget(label_first_name)
    layout.addWidget(first_name_edit)

    label_last_name = QLabel("Nazwisko:")
    last_name_edit = QLineEdit()
    layout.addWidget(label_last_name)
    layout.addWidget(last_name_edit)

    label_group = QLabel("Grupa:")
    group_combo_box = QComboBox()
    groups = get_groups()
    for group in groups:
        group_combo_box.addItem(group[1], group[0])
    layout.addWidget(label_group)
    layout.addWidget(group_combo_box)

    button_add_child = QPushButton("Dodaj")
    button_add_child.clicked.connect(lambda: self.add_child(first_name_edit.text(), last_name_edit.text(), group_combo_box.currentData(), dialog))

    layout.addWidget(button_add_child)

    dialog.exec()

def add_child(self, first_name, last_name, group_id, dialog):
    connection = connect_to_database()
    cursor = connection.cursor()

    query = "INSERT INTO Children (first_name, last_name, group_id) VALUES (%s, %s, %s)"
    values = (first_name, last_name, group_id)

    cursor.execute(query, values)
    connection.commit()
    connection.close()

    dialog.close()  # Zamykanie okna dialogowego po dodaniu dziecka

    QMessageBox.information(self, "Dodawanie dziecka", f"Dodano dziecko: {first_name} {last_name}")

    self.load_children()  # Przeładuj listę dzieci w interfejsie