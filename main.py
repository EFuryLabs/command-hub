import sys
import json
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QLineEdit, QLabel,
    QInputDialog, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QGuiApplication


DATA_FILE = "commands.json"


class CommandHub(QWidget):
    def __init__(self):
        super().__init__()

        # 🔥 Remove window border
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setWindowOpacity(0.97)

        self.setGeometry(100, 100, 1000, 600)

        self.data = {}
        self.current_category = None
        self.current_command = None

        self.old_pos = None

        self.init_ui()
        self.load_data()

    # ---------------- UI ----------------
    def init_ui(self):
        main_layout = QVBoxLayout()

        # 🔷 TOP BAR (custom title bar)
        top_bar = QHBoxLayout()

        self.title = QLabel("Command Hub")
        self.title.setStyleSheet("font-size: 16px;")

        self.min_btn = QPushButton("—")
        self.min_btn.setFixedSize(30, 30)
        self.min_btn.clicked.connect(self.showMinimized)

        self.close_btn = QPushButton("✕")
        self.close_btn.setFixedSize(30, 30)
        self.close_btn.clicked.connect(self.close)

        top_bar.addWidget(self.title)
        top_bar.addStretch()
        top_bar.addWidget(self.min_btn)
        top_bar.addWidget(self.close_btn)

        # 🔷 MAIN CONTENT
        content_layout = QHBoxLayout()

        # LEFT PANEL
        left_layout = QVBoxLayout()

        self.category_list = QListWidget()
        self.category_list.clicked.connect(self.on_category_selected)

        self.add_category_btn = QPushButton("+ Category")
        self.add_category_btn.clicked.connect(self.add_category)

        self.delete_category_btn = QPushButton("Delete Category")
        self.delete_category_btn.clicked.connect(self.delete_category)

        left_layout.addWidget(QLabel("Categories"))
        left_layout.addWidget(self.category_list)
        left_layout.addWidget(self.add_category_btn)
        left_layout.addWidget(self.delete_category_btn)

        # RIGHT PANEL
        right_layout = QVBoxLayout()

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search commands...")
        self.search_bar.textChanged.connect(self.filter_commands)

        self.commands_container = QVBoxLayout()
        self.add_command_btn = QPushButton("+ Command")
        self.add_command_btn.clicked.connect(self.add_command)

        self.delete_command_btn = QPushButton("− Command")
        self.delete_command_btn.clicked.connect(self.delete_command)

        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        right_layout.addWidget(self.search_bar)
        right_layout.addLayout(self.commands_container)
        right_layout.addWidget(self.add_command_btn)
        right_layout.addWidget(self.delete_command_btn)
        right_layout.addWidget(self.status_label)

        content_layout.addLayout(left_layout, 1)
        content_layout.addLayout(right_layout, 3)

        main_layout.addLayout(top_bar)
        main_layout.addLayout(content_layout)

        self.setLayout(main_layout)

    # ---------------- DRAG WINDOW ----------------
    def mousePressEvent(self, event):
        self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()

    # ---------------- DATA ----------------
    def load_data(self):
        try:
            with open(DATA_FILE, "r") as f:
                self.data = json.load(f)
        except:
            self.data = {}

        self.category_list.clear()
        for cat in self.data.keys():
            self.category_list.addItem(cat)

    def save_data(self):
        with open(DATA_FILE, "w") as f:
            json.dump(self.data, f, indent=2)

    # ---------------- CATEGORY ----------------
    def on_category_selected(self):
        self.current_category = self.category_list.currentItem().text()
        self.display_commands()

    def add_category(self):
        text, ok = QInputDialog.getText(self, "New Category", "Enter category name:")
        if ok and text:
            if text not in self.data:
                self.data[text] = []
                self.save_data()
                self.load_data()

    def delete_category(self):
        if not self.current_category:
            QMessageBox.warning(
                self,
                "Error",
                "Select a category first!"
            )
            return

        reply = QMessageBox.question(
            self,
            "Delete Category",
            f"Are you sure you want to delete "
            f"'{self.current_category}' and all its commands?",
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:

            deleted_category = self.current_category

            del self.data[self.current_category]

            self.current_category = None
            self.current_command = None

            self.save_data()
            self.load_data()

            # Clear commands area
            for i in reversed(range(self.commands_container.count())):
                widget = self.commands_container.itemAt(i).widget()
                if widget:
                    widget.deleteLater()

            self.status_label.setText(
                f"Deleted category: {deleted_category}"
            )

    # ---------------- COMMANDS ----------------
    def display_commands(self, filter_text=""):
        for i in reversed(range(self.commands_container.count())):
            widget = self.commands_container.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        if not self.current_category:
            return

        for cmd in self.data[self.current_category]:
            if filter_text.lower() not in cmd["name"].lower():
                continue

            btn = QPushButton(cmd["name"])
            btn.setToolTip(cmd["command"])

            btn.clicked.connect(
                lambda _, c=cmd["command"], n=cmd["name"]:
                self.select_command(c, n)
            )

            self.commands_container.addWidget(btn)

    def select_command(self, command, name):
        self.current_command = {
            "name": name,
            "command": command
        }

        QGuiApplication.clipboard().setText(command)
        self.status_label.setText(f"Copied: {command}")

    def filter_commands(self):
        self.display_commands(self.search_bar.text())

    def copy_command(self, command):
        QGuiApplication.clipboard().setText(command)
        self.status_label.setText(f"Copied: {command}")

    def delete_command(self):
        if not self.current_category:
            QMessageBox.warning(
                self,
                "Error",
                "Select a category first!"
            )
            return

        if not self.current_command:
            QMessageBox.warning(
                self,
                "Error",
                "Select a command first!"
            )
            return

        reply = QMessageBox.question(
            self,
            "Delete Command",
            f"Are you sure you want to delete "
            f"'{self.current_command['name']}'?",
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:

            self.data[self.current_category].remove(
                self.current_command
            )

            self.save_data()

            deleted_name = self.current_command["name"]
            self.current_command = None

            self.display_commands(self.search_bar.text())

            self.status_label.setText(
                f"Deleted: {deleted_name}"
            )

    def add_command(self):
        if not self.current_category:
            QMessageBox.warning(self, "Error", "Select a category first!")
            return

        name, ok1 = QInputDialog.getText(self, "Command Name", "Enter name:")
        if not ok1 or not name:
            return

        command, ok2 = QInputDialog.getText(self, "Command", "Enter command:")
        if not ok2 or not command:
            return

        self.data[self.current_category].append({
            "name": name,
            "command": command
        })

        self.save_data()
        self.display_commands()


# ---------------- STYLE ----------------
def apply_style(app):
    app.setStyleSheet("""
    QWidget {
        background-color: #0b0f14;
        color: #00ffff;
        font-family: Consolas;
        font-size: 13px;
        border-radius: 10px;
    }

    QListWidget {
        border: 1px solid #ff00ff;
        background-color: #111;
        padding: 5px;
    }

    QPushButton {
        background-color: #111;
        border: 1px solid #00ffff;
        padding: 8px;
        border-radius: 6px;
    }

    QPushButton:hover {
        background-color: #00ffff;
        color: black;
    }

    QLineEdit {
        background-color: #111;
        border: 1px solid #00ffff;
        padding: 6px;
        border-radius: 6px;
    }

    QLabel {
        color: #ff00ff;
    }
    """)


# ---------------- MAIN ----------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    apply_style(app)

    window = CommandHub()
    window.show()

    sys.exit(app.exec())