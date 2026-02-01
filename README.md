# GhostPiP 👻

**GhostPiP** is a premium Python utility designed for gamers and power users who use browser Picture-in-Picture (PiP) mode. It essentially makes your PiP window "hollow" to mouse events, preventing accidental clicks while gaming or working, while allowing you to keep your video overlay visible.

![GitHub last commit](https://img.shields.io/github/last-commit/melihgulbay/GhostPiP?style=flat-square&color=6366f1)
![Python Version](https://img.shields.io/badge/python-3.9+-6366f1?style=flat-square)
![Flet UI](https://img.shields.io/badge/UI-Flet-green?style=flat-square)

## ✨ Features

- 🔒 **Collision Lock**: Deactivates mouse interaction with PiP windows.
- 🎨 **Premium Flet UI**: Modern dark theme with Indigo accents and Material Design 3 components.
- 🎚️ **Opacity Control**: Adjust the transparency of your PiP window in real-time.
- 🌍 **Localized Support**: Works with both English ("Picture-in-Picture") and Turkish ("Resim içinde resim") browser titles.
- ⚡ **Lightweight**: Uses high-performance Win32 API calls and minimal CPU resources.
- 🛡️ **Auto-Restore**: Automatically restores window interaction when the app is closed.

## 🚀 Getting Started

### Prerequisites
- Windows 10 or 11
- Python 3.9 or higher

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/melihgulbay/GhostPiP.git
   cd GhostPiP
   ```
2. Install dependencies:
   ```bash
   pip install flet
   ```

### Usage
- Run the script:
  ```bash
  python main.py
  ```
- Or simply double-click the `run_pip_deactivator.bat` file.

## 🛠️ How it Works
GhostPiP uses the `ctypes` library to interface with the Windows `user32.dll`. It applies the `WS_EX_TRANSPARENT` and `WS_EX_LAYERED` extended window styles to browser PiP windows. This causes Windows to pass mouse events through the PiP window to whatever is behind it (like your game).

## 📄 License
This project is open-source and available under the [MIT License](LICENSE).

---
*Created by [melihgulbay](https://github.com/melihgulbay)*
