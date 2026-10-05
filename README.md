<div align="center">

# Command Hub

**A modern command manager built with Python and PyQt6**

Organize your frequently used commands into categories and copy any of them to your clipboard with a single click.

<img src="assets/screenshot.png" alt="Command Hub: categories on the left, search and command buttons on the right" width="900"/>

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![PyQt6](https://img.shields.io/badge/PyQt6-GUI-green)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-orange)

[**Watch the video**](https://youtu.be/sEPDEN9yzwQ) · [**Project page**](https://efurylabs.com/projects/python-command-hub.html) · [**EFury Labs on YouTube**](https://www.youtube.com/@EFuryLabs)

</div>

---

## Features

- **Categories**: group commands as Git, Linux, Docker, Trace32, ADB or anything you use
- **One-click copy**: every command is a button; click it and the command is on your clipboard
- **Instant search**: filter the selected category by command name as you type
- **Hover to preview**: the tooltip shows the full command before you copy it
- **Add and delete** commands and categories, with a confirmation before anything is deleted
- **Local JSON storage**: saved to `commands.json` after every change, with no database and no internet connection
- **Frameless, cyber-themed window** with its own title bar, styled with Qt Style Sheets
- **Lightweight and cross-platform**: one Python file, runs on Windows, Linux and macOS

Commands are only **copied**, never executed. Nothing runs until you paste it yourself.

---

## Demo

<img src="assets/demo.gif" alt="Command Hub demo: selecting a category and copying a command" width="900"/>

---

## Video tutorial

[![I Built a Python Command Hub | PyQt6 GUI App for Faster Workflows](https://img.youtube.com/vi/sEPDEN9yzwQ/hqdefault.jpg)](https://youtu.be/sEPDEN9yzwQ)

**[I Built a Python Command Hub | PyQt6 GUI App for Faster Workflows](https://youtu.be/sEPDEN9yzwQ)** on the **[EFury Labs](https://www.youtube.com/@EFuryLabs)** YouTube channel.

The video covers:

- Building the UI with PyQt6
- Creating a frameless desktop application
- Managing categories and commands
- JSON file handling
- Clipboard integration
- Custom styling with Qt Style Sheets (QSS)
- Running and extending the application

The written guide, with a code walkthrough, is on the [EFury Labs project page](https://efurylabs.com/projects/python-command-hub.html).

---

## Project structure

```text
command-hub/
├── assets/
│   ├── screenshot.png
│   └── demo.gif
├── main.py            # the whole application
├── commands.json      # your saved commands (sample data included)
├── requirements.txt
├── LICENSE
├── .gitignore
└── README.md
```

---

## Requirements

- Python 3.10 or newer
- pip
- PyQt6 (installed from `requirements.txt`)

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/EFuryLabs/command-hub.git
cd command-hub
```

Or use **Code → Download ZIP** on GitHub and extract it.

### 2. Create a virtual environment (recommended)

```bash
# Windows
python -m venv venv

# Linux / macOS
python3 -m venv venv
```

### 3. Activate it

```bash
# Windows (Command Prompt)
venv\Scripts\activate

# Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# Linux / macOS
source venv/bin/activate
```

### 4. Install the dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the application

Run it **from inside the `command-hub` folder** (see [Data storage](#data-storage)):

```bash
python main.py
```

The repository includes a sample `commands.json` (Linux, Trace32, Bash, Git and Embedded examples), so the app opens with something to click. Replace those examples with your own.

---

## How to use

| Action | How |
|---|---|
| **Create a category** | Click **+ Category** and enter a name, e.g. `Git`, `Docker`, `ADB` |
| **Select a category** | Click it in the left panel; its commands appear as buttons on the right |
| **Add a command** | With a category selected, click **+ Command**, enter a name (`Git Pull`) and then the command (`git pull origin main`) |
| **Copy a command** | Click its button. The status line shows `Copied: …`; paste with **Ctrl + V** |
| **Preview a command** | Hover over its button |
| **Search** | Type in the search bar to filter the selected category by command name |
| **Delete a command** | Click the command first (this selects it), then **− Command**, and confirm |
| **Delete a category** | Select it, click **Delete Category**, and confirm. This removes all its commands |
| **Move the window** | Drag any empty part of it. **—** minimises, **✕** closes |

---

## Data storage

Everything is stored locally in `commands.json`:

```json
{
  "Git": [
    {
      "name": "Git Status",
      "command": "git status"
    },
    {
      "name": "Push",
      "command": "git push origin main"
    }
  ]
}
```

- The file is read at start-up and rewritten after every add or delete.
- It is opened from the **current working directory**, so start the app from the project folder. Started elsewhere, it opens empty and creates a new `commands.json` there.
- It is plain text: back it up by copying it, or keep it in a private Git repository.
- To edit a command, change it in `commands.json` while the app is closed, or delete it and add it again.

No cloud storage, no account, and no internet connection required.

---

## Technologies used

- Python
- PyQt6 (Qt Widgets, `QGuiApplication.clipboard()`)
- Qt Style Sheets (QSS)
- JSON

---

## Roadmap

- [x] Add and delete categories
- [x] Add and delete commands
- [x] Search, tooltips and one-click copy
- [ ] Edit commands in place
- [ ] Import / export JSON
- [ ] SQLite support
- [ ] Keyboard shortcuts
- [ ] Favorites
- [ ] Multi-line commands
- [ ] Command descriptions
- [ ] Dark / light themes
- [ ] System tray support
- [ ] Global hotkeys

---

## Common issues

**`python` is not recognized**
Install Python and tick **Add Python to PATH** during installation, then open a new terminal. On Linux/macOS use `python3`.

**`No module named PyQt6`**
Activate the virtual environment and install the dependencies:

```bash
pip install -r requirements.txt
```

**My commands are gone / the list is empty**
The app was probably started from a different folder. Run `python main.py` from inside `command-hub`, where your `commands.json` lives.

**Commands are not saved**
Make sure the app can create and modify `commands.json` in the folder it was started from.

---

## Contributing

Contributions are welcome:

1. Fork the repository.
2. Create a feature branch.
3. Commit your changes.
4. Open a Pull Request.

---

## Support

If you found this project helpful:

- ⭐ Star this repository
- 🍴 Fork the project
- 📺 Subscribe to **[EFury Labs](https://www.youtube.com/@EFuryLabs)** for more Python, embedded systems, electronics and automotive software builds
- 🌐 Visit **[efurylabs.com](https://efurylabs.com)** for free tools, datasheets and guides
- 🛠 Share it with fellow developers

---

## License

This project is licensed under the **MIT License**. See [LICENSE](LICENSE) for details.

---

<div align="center">

**EFury Labs** · Think • Build • Solve

Made by **Vijay Bari**

</div>
