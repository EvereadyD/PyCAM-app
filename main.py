import os
import sqlite3
import sys

from PySide6.QtCore import QUrl
from PySide6.QtGui import QStandardItemModel, QStandardItem, QDesktopServices, QKeySequence
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox, QDialog, QVBoxLayout, \
    QFormLayout, QLineEdit, QDialogButtonBox, QLabel
from ui_PyCAM import Ui_MainWindow
import resources_rc


os.environ["QT_TLS_BACKEND"] = "certstore"


class AddCameraDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add new camera")
        self.setModal(True)

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.inputs = {}
        fields = [
            ("Serial Number", "Serial Number"),
            ("Name", "Name"),
            ("Year", "Year"),
            ("Country", "Country"),
            ("Brand", "Brand"),
            ("Optics", "Optics"),
            ("Date of creation", "Date_of_creation"),
            ("Recording Type", "Recording Type"),
            ("User Type", "User Type")
        ]

        for label_text, field_name in fields:
            line_edit = QLineEdit(self)
            form_layout.addRow(f"{label_text}:", line_edit)
            self.inputs[field_name] = line_edit

        layout.addLayout(form_layout)

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
                                           self)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

    def get_data(self):
        return {field_name: widget.text().strip() for field_name, widget in self.inputs.items()}


class WarningDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Warning")
        self.setModal(True)

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.label = QLabel("Are you sure you want to imply changes?", self)
        form_layout.addWidget(self.label)

        layout.addLayout(form_layout)

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Yes | QDialogButtonBox.StandardButton.No,
                                           self)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)


class DeleteWarningDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Warning")
        self.setModal(True)

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.label = QLabel("Are you sure you want to delete field?", self)
        form_layout.addWidget(self.label)

        layout.addLayout(form_layout)

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Yes | QDialogButtonBox.StandardButton.No,
                                           self)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)


class Hotkeys_Dialog(QDialog):
    def __init__(self, current_hotkeys=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Hotkeys")
        self.setModal(True)

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.label = QLabel("Change Hotkeys as you like:", self)
        self.inputs = {}
        fields = [
            ("SN search hotkey:", "sn_search", "1"),
            ("Name search hotkey:", "name_search", "2"),
            ("Year search hotkey:", "year_search", "3"),
            ("Country search hotkey:", "country_search", "4"),
            ("Full search hotkey:", "full_search", "<Return>"),
            ("Send me Email hotkey", "email", "E"),
            ("My GitHub hotkey", "github", "G"),
            ("Site hotkey", "site", "S"),
        ]

        current_hotkeys = current_hotkeys or {}
        for label_text, field_name, default_val in fields:
            line_edit = QLineEdit(self)
            line_edit.setText(current_hotkeys.get(field_name, default_val))
            form_layout.addRow(f"{label_text}:", line_edit)
            self.inputs[field_name] = line_edit

        form_layout.addWidget(self.label)

        layout.addLayout(form_layout)

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
                                           self)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

    def get_hotkeys(self):
        return {field_name: widget.text().strip() for field_name, widget in self.inputs.items()}


class MyWidget(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setFixedSize(1131, 750)
        self.setWindowTitle("PyCAM")

        self.con = None
        self.cur = None

        self.site_btn.clicked.connect(self.open_website)
        self.GitHub_btn.clicked.connect(self.open_github)
        self.email_btn.clicked.connect(self.open_email)
        self.add_btn.clicked.connect(self.add_data_btn)
        self.del_btn.clicked.connect(self.delete_data_btn)
        self.day_radio.clicked.connect(self.win_radio)
        self.color_radio.clicked.connect(self.mac_radio)
        self.night_radio.clicked.connect(self.fusion_radio)
        self.hotkeys_btn.clicked.connect(self.open_hotkeys)
        self.style_sp.currentTextChanged.connect(self.get_style_text)
        self.size_spin.valueChanged.connect(self.get_size_text)
        self.search_sn.clicked.connect(lambda: self.search_by_column("SN", self.edit_sn.toPlainText()))
        self.search_name.clicked.connect(lambda: self.search_by_column("Name", self.edit_name.toPlainText()))
        self.search_year.clicked.connect(lambda: self.search_by_column("year", self.edit_year.toPlainText()))
        self.search_country.clicked.connect(lambda: self.search_by_column("Country", self.edit_country.toPlainText()))
        self.full_search_btn.clicked.connect(self.full_search)
        self.hotkeys = {
            "sn_search": "1",
            "name_search": "2",
            "year_search": "3",
            "country_search": "4",
            "full_search": "Return",
            "email": "E",
            "github": "G",
            "site": "S",
        }
        self.apply_hotkeys()

        for line in open("instructions.txt", encoding="utf-16"):
            self.README_sp.addItem(line.strip())

        self.db_dialog()

        self.load_preview_all()

    def connect_db(self):
        try:
            self.con = sqlite3.connect("PyCAM.db")
            self.cur = self.con.cursor()
            return True
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error", f"Cannot connect to db:\n{e}")
            return False

    def db_dialog(self):
        if not self.connect_db():
            return

        headers = [
            "ID", "Serial Number", "Name", "year",
            "Country", "Brand", "Optics", "Date_of_creation", "Recording Type", "User Type"
        ]

        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(headers)

        try:
            self.cur.execute("SELECT * FROM Cameras")
            rows = self.cur.fetchall()

            for row_data in rows:
                row_items = []
                for cell in row_data:
                    value = str(cell) if cell is not None else ""
                    item = QStandardItem(value)
                    row_items.append(item)
                model.appendRow(row_items)

            self.db_show.setModel(model)
            self.db_show.setColumnHidden(0, False)
            self.db_show.resizeColumnsToContents()

        except sqlite3.Error as e:
            QMessageBox.critical(self, "DataBase failure!", f"Unable to load data:\n{e}")
        finally:
            if self.con:
                self.cur.close()
                self.con.close()

    def add_data_btn(self):
        dialog = AddCameraDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()

            confirm_dialog = WarningDialog(self)
            if confirm_dialog.exec() != QDialog.DialogCode.Accepted:
                return

            if not self.connect_db():
                return

            try:
                sql_query = """
                    INSERT INTO Cameras VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """

                values = (
                    data["Serial Number"],
                    data["Name"],
                    data["Year"],
                    data["Country"],
                    data["Brand"],
                    data["Optics"],
                    data["Date_of_creation"],
                    data["Recording Type"],
                    data["User Type"]
                )

                self.cur.execute(sql_query, values)
                self.con.commit()

                QMessageBox.information(self, "Success!", "Camera added!")

                self.db_dialog()

            except sqlite3.Error as e:
                QMessageBox.critical(self, "Database Error", f"Could not add data:\n{e}")
                if self.con:
                    self.con.rollback()
            finally:
                if self.con:
                    self.cur.close()
                    self.con.close()

    def delete_data_btn(self):
        selected_indexes = self.db_show.selectionModel().selectedRows()

        if not selected_indexes:
            QMessageBox.warning(self, "Warning", "Please select row to delete!")
            return

        row_idx = selected_indexes[0].row()

        model = self.db_show.model()
        item_id = model.item(row_idx, 0).text()

        confirm_dialog = DeleteWarningDialog(self)
        if confirm_dialog.exec() != QDialog.DialogCode.Accepted:
            return

        if not self.connect_db():
            return

        try:
            sql_query = "DELETE FROM Cameras WHERE ID = ?"
            self.cur.execute(sql_query, (item_id,))
            self.con.commit()

            QMessageBox.information(self, "Success!", "Record deleted successfully!")

            self.db_dialog()

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Could not delete data:\n{e}")
            if self.con:
                self.con.rollback()
        finally:
            if self.con:
                self.cur.close()
                self.con.close()

    def open_website(self):
        url = QUrl("https://evereadyd.github.io/PyCAM/")
        QDesktopServices.openUrl(url)

    def open_github(self):
        url = QUrl("https://github.com/EvereadyD")
        QDesktopServices.openUrl(url)

    def open_email(self):
        url = QUrl("mailto:daniel.zasimov@yandex.ru")
        QDesktopServices.openUrl(url)

    def win_radio(self):
        if self.day_radio.isChecked():
            app.setStyle("Windows")

    def mac_radio(self):
        if self.color_radio.isChecked():
            app.setStyle("macOS")

    def fusion_radio(self):
        if self.night_radio.isChecked():
            app.setStyle("Fusion")

    def open_hotkeys(self):
        if not hasattr(self, "hotkeys"):
            self.hotkeys = {
                "sn_search": "1",
                "name_search": "2",
                "year_search": "3",
                "country_search": "4",
                "full_search": "Return",
                "email": "E",
                "github": "G",
                "site": "S",
            }

        dialog = Hotkeys_Dialog(current_hotkeys=self.hotkeys, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.hotkeys = dialog.get_hotkeys()
            self.apply_hotkeys()

    def apply_hotkeys(self):
        button_map = {
            "sn_search": self.search_sn,
            "name_search": self.search_name,
            "year_search": self.search_year,
            "country_search": self.search_country,
            "full_search": self.full_search_btn,
            "email": self.email_btn,
            "github": self.GitHub_btn,
            "site": self.site_btn,
        }

        for key, button in button_map.items():
            hotkey_str = self.hotkeys.get(key, "").strip()
            button.setShortcut(QKeySequence(hotkey_str))

    def get_style_text(self):
        selected_text = self.style_sp.currentText()
        stylesheet = f"""
            QMainWindow, QWidget {{
                font-family: "{selected_text}";
            }}
        """
        self.setStyleSheet(stylesheet)

    def get_size_text(self):
        selected_size = self.size_spin.value()
        stylesheet = f"""
                    QMainWindow, QWidget {{
                        font-size: {selected_size}px;
                    }}
                """
        self.setStyleSheet(stylesheet)

    def show_search_preview(self, rows):
        headers = [
            "ID", "Serial Number", "Name", "year",
            "Country", "Brand", "Optics", "Date_of_creation", "Recording Type", "User Type"
        ]
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(headers)

        for row_data in rows:
            row_items = []
            for cell in row_data:
                val = str(cell) if cell is not None else ""
                row_items.append(QStandardItem(val))
            model.appendRow(row_items)

        self.preview_datab.setModel(model)
        self.preview_datab.setColumnHidden(0, False)
        self.preview_datab.resizeColumnsToContents()

    def load_preview_all(self):
        if not self.connect_db():
            return
        try:
            self.cur.execute("SELECT * FROM Cameras")
            rows = self.cur.fetchall()
            self.show_search_preview(rows)
        except sqlite3.Error as e:
            QMessageBox.critical(self, "DataBase failure!", f"Unable to load preview:\n{e}")
        finally:
            if self.con:
                self.cur.close()
                self.con.close()

    def search_by_column(self, column_name, search_value):
        search_value = search_value.strip()
        if not search_value:
            QMessageBox.warning(self, "Warning", "Enter text to search!")
            return

        if not self.connect_db():
            return

        try:
            if column_name == "Serial Number":
                column_name = "SN"

            query = f'SELECT * FROM Cameras WHERE "{column_name}" LIKE ?'
            self.cur.execute(query, (f"%{search_value}%",))
            rows = self.cur.fetchall()

            if not rows:
                QMessageBox.information(self, "Search", "Nothing found!")

            self.show_search_preview(rows)
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Search failed:\n{e}")
        finally:
            if self.con:
                self.cur.close()
                self.con.close()

    def full_search(self):
        if not self.connect_db():
            return

        try:
            self.cur.execute("PRAGMA table_info(Cameras)")
            db_columns = [row[1] for row in self.cur.fetchall()]

            conditions = []
            params = []

            text_filters = {
                db_columns[1]: self.edit_sn.toPlainText().strip(),
                db_columns[2]: self.edit_name.toPlainText().strip(),
                db_columns[3]: self.edit_year.toPlainText().strip(),
                db_columns[4]: self.edit_country.toPlainText().strip(),
            }

            for col, val in text_filters.items():
                if val:
                    conditions.append(f'"{col}" LIKE ?')
                    params.append(f"%{val}%")

            combo_filters = {
                db_columns[5]: self.brand_sp.currentText().strip(),
                db_columns[6]: self.optics_spi.currentText().strip(),
                db_columns[8]: self.rec_sp.currentText().strip(),
                db_columns[9]: self.type_sp.currentText().strip(),
            }

            for col, val in combo_filters.items():
                if val and val != "All":
                    conditions.append(f'"{col}" LIKE ?')
                    params.append(f"%{val}%")

            query = "SELECT * FROM Cameras"
            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            self.cur.execute(query, params)
            rows = self.cur.fetchall()

            if not rows:
                QMessageBox.information(self, "Full Search", "No matching cameras found.")

            self.show_search_preview(rows)
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Full search failed:\n{e}")
        finally:
            if self.con:
                self.cur.close()
                self.con.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWidget()
    window.show()
    sys.exit(app.exec())
