# PyCAM ® 📷

**PyCAM** is a lightweight, standalone desktop application built with Python and PySide6 (Qt6) designed for efficient camera hardware inventory tracking, quick serial number (SN) queries, and local database log management.

---

## ✨ Features

- **Multi-Parameter Search:** Perform targeted lookups or cross-reference assets via "Full Search" combining Serial Number, Name, Year, Country, Brand, and Optics Manufacturer.
- **Local SQLite Database:** A self-contained, high-performance daily logging system—filter and view records created specifically *for today*.
- **Smart Dialog Workflows:** Custom modal dialogs (`QDialog`) for execution confirmations, multi-field validations, and warning alerts.
- **Independent Standalone App:** Compiled resources (`.qrc`) ensure that all interface iconography and layouts are bundled natively inside the build.

---

## 📸 Interface Preview

| Search & Analytics | Database Management                               |
|---|---------------------------------------------------|
| *Clean search panel featuring dynamic brand/optics dropdown selections.* | *Add or remove local hardware records instantly.* |

---

## 🛠️ Tech Stack & Architecture

- **Language:** Python 3.11+
- **GUI Engine:** PySide6 (Official Qt6 for Python)
- **Database:** SQLite3 (Embedded, zero-configuration)
- **Design Core:** Qt Designer (`.ui` structured forms compiled directly to native Python objects via `pyside6-uic`)
- **Asset Pipeline:** Compiled `.qrc` files mapping system icons seamlessly without external path dependencies.

---

## 🚀 Quick Start

### Prerequisites
Make sure you have Python 3.11 or higher installed on your macOS, Windows, or Linux system.

### 1. Clone the repository
```bash
git clone https://github.com
cd PyCAM
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Compile UI and Resources (Development stage)
If you modify the UI layouts in Qt Designer, regenerate the Python asset bindings:
```bash
# Compile UI layout
pyside6-uic PyCAM.ui -o ui_PyCAM.py

# Compile icons & resources
pyside6-rcc resources.qrc -o resources_rc.py
```

### 4. Run the application
```bash
PyCAM.exe
```

---

## 📝 License

Distributed under the MIT License. See `LICENSE` in GitHub for more information.

---
*PyCAM © 2026. Built with absolute precision for high-performance camera logging and search.*
