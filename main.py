import sys
import os
import json
import shutil
import traceback
from datetime import datetime
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QLineEdit, QLabel,
    QInputDialog, QMessageBox
)
from PyQt6.QtCore import Qt, QUrl, QLockFile
from PyQt6.QtGui import QGuiApplication, QIcon, QDesktopServices

from app_info import (
    APP_NAME, APP_ID, VERSION, PUBLISHER, AUTHOR, DESCRIPTION, WEBSITE, REPO
)


# ---------------- PATHS ----------------
def resource_path(relative):
    """Files shipped WITH the app (icon, default commands).

    From source: next to main.py.
    Built with PyInstaller: inside the bundle (sys._MEIPASS).
    """
    base = getattr(sys, "_MEIPASS", Path(__file__).resolve().parent)
    return Path(base) / relative


def data_dir():
    """Where the USER's data lives - always writable, survives updates.

    Windows: %APPDATA%\\EFury Labs\\Command Hub
    macOS:   ~/Library/Application Support/EFury Labs/Command Hub
    Linux:   ~/.config/EFury Labs/Command Hub

    (An installed app must never write next to its .exe: C:\\Program Files
    is read-only for normal programs.)
    """
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    folder = base / PUBLISHER / APP_NAME
    folder.mkdir(parents=True, exist_ok=True)
    return folder


DATA_DIR = data_dir()
DATA_FILE = DATA_DIR / "commands.json"
LOG_FILE = DATA_DIR / "error.log"
ICON_FILE = resource_path("assets/app.ico")


def first_run_setup():
    """First start: copy the sample commands into the user's data folder."""
    if DATA_FILE.exists():
        return
    for sample in (resource_path("defaults/commands.json"), resource_path("commands.json")):
        if sample.exists():
            shutil.copyfile(sample, DATA_FILE)
            return


# ---------------- SINGLE INSTANCE ----------------
_instance_lock = None


def already_running():
    """True if another Command Hub is open.

    Windows: a named mutex. The installer checks the same name (AppMutex)
    so it can ask you to close the app before updating or uninstalling.
    """
    global _instance_lock
    if sys.platform == "win32":
        import ctypes
        _instance_lock = ctypes.windll.kernel32.CreateMutexW(None, False, APP_ID)
        ERROR_ALREADY_EXISTS = 183
        return ctypes.windll.kernel32.GetLastError() == ERROR_ALREADY_EXISTS
    _instance_lock = QLockFile(str(DATA_DIR / "app.lock"))
    _instance_lock.setStaleLockTime(0)
    return not _instance_lock.tryLock(100)


# ---------------- ERRORS ----------------
def show_unexpected_error(exc_type, exc, tb):
    """Any crash: write it to error.log and show a message instead of vanishing."""
    details = "".join(traceback.format_exception(exc_type, exc, tb))
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n[{datetime.now():%Y-%m-%d %H:%M:%S}] {APP_NAME} {VERSION}\n{details}")
    except OSError:
        pass
    if QApplication.instance():
        box = QMessageBox(QMessageBox.Icon.Critical, f"{APP_NAME} - unexpected error",
                          f"Something went wrong:\n\n{exc}\n\n"
                          f"Details were saved to:\n{LOG_FILE}")
        box.setDetailedText(details)
        box.exec()


class CommandHub(QWidget):
    def __init__(self):
        super().__init__()

        # 🔥 Remove window border
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setWindowOpacity(0.97)
        self.setWindowTitle(APP_NAME)          # taskbar / Alt+Tab name
        self.setWindowIcon(QIcon(str(ICON_FILE)))

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

        self.title = QLabel(APP_NAME)
        self.title.setStyleSheet("font-size: 16px;")

        self.about_btn = QPushButton("i")
        self.about_btn.setFixedSize(30, 30)
        self.about_btn.setToolTip("About")
        self.about_btn.clicked.connect(self.show_about)

        self.min_btn = QPushButton("—")
        self.min_btn.setFixedSize(30, 30)
        self.min_btn.clicked.connect(self.showMinimized)

        self.close_btn = QPushButton("✕")
        self.close_btn.setFixedSize(30, 30)
        self.close_btn.clicked.connect(self.close)

        top_bar.addWidget(self.title)
        top_bar.addStretch()
        top_bar.addWidget(self.about_btn)
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

    # ---------------- ABOUT ----------------
    def show_about(self):
        box = QMessageBox(self)
        box.setWindowTitle(f"About {APP_NAME}")
        box.setIconPixmap(QIcon(str(ICON_FILE)).pixmap(64, 64))
        box.setTextFormat(Qt.TextFormat.RichText)
        box.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        box.setText(
            f"<b>{APP_NAME}</b> &nbsp;version {VERSION}<br>"
            f"{DESCRIPTION}<br><br>"
            f"By {AUTHOR} · {PUBLISHER}<br>"
            f"<a href='{WEBSITE}' style='color:#00ffff'>Project page</a> · "
            f"<a href='{REPO}' style='color:#00ffff'>Source code (MIT)</a><br><br>"
            f"Your commands are saved in:<br><code>{DATA_DIR}</code>"
        )
        open_btn = box.addButton("Open data folder", QMessageBox.ButtonRole.ActionRole)
        box.addButton(QMessageBox.StandardButton.Close)
        box.exec()
        if box.clickedButton() is open_btn:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(DATA_DIR)))

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
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        except FileNotFoundError:
            self.data = {}
        except (json.JSONDecodeError, UnicodeDecodeError):
            # Keep the damaged file for the user, start with an empty list.
            backup = DATA_FILE.with_name(f"commands.broken-{datetime.now():%Y%m%d-%H%M%S}.json")
            shutil.copyfile(DATA_FILE, backup)
            self.data = {}
            QMessageBox.warning(
                self, APP_NAME,
                f"commands.json could not be read, so Command Hub started empty.\n\n"
                f"A copy of the damaged file was saved as:\n{backup}"
            )

        self.category_list.clear()
        for cat in self.data.keys():
            self.category_list.addItem(cat)

    def save_data(self):
        # Write to a temporary file first, then swap it in: a crash or
        # power cut can never leave a half-written commands.json.
        tmp = DATA_FILE.with_suffix(".tmp")
        try:
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            os.replace(tmp, DATA_FILE)
        except OSError as e:
            QMessageBox.critical(
                self, APP_NAME,
                f"Your change could not be saved.\n\n{e}\n\nFile: {DATA_FILE}"
            )

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
    # Own taskbar icon/group on Windows (otherwise it groups under python.exe)
    if sys.platform == "win32":
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_ID)

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(VERSION)
    app.setOrganizationName(PUBLISHER)
    app.setWindowIcon(QIcon(str(ICON_FILE)))
    apply_style(app)

    sys.excepthook = show_unexpected_error

    if already_running():
        QMessageBox.information(None, APP_NAME, f"{APP_NAME} is already running.")
        sys.exit(0)

    first_run_setup()

    window = CommandHub()
    window.show()

    sys.exit(app.exec())
