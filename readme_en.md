# QR code Recognizer on Windows

English | [中文](readme.md)

This is a QR code Recognizer running on Windows systems. Its results are saved in the system clipboard.

- Recognize the string content from the QR code.
- The QR code recognition function is realized by [pyzbar](https://github.com/NaturalHistoryMuseum/pyzbar).
- The GUI is built by [Qt](https://wiki.qt.io/Qt_for_Python).
- The `.exe` program is built by [PyInstaller](https://pyinstaller.org/).

## Disclaimer

### **This project is an OPEN-SOURCE, OFFLINE endeavor! All developers & maintainers of this project CANNOT control its use, and they CANNOT collect or get the input of users, either. Therefore, any issues or consequences arising from their use are the SOLE RESPONSIBILITY of the users, COMPLETELY UNRELATED to the developers & maintainers!!!**

## Presentation

![presentation](presentation.gif)

## Use of Source Code

Require `python>=3.8`, require dependency libraries `pyzbar, opencv-python, PySide6`.

After, run `python main.py`. Please pay attention to `sys_icon_dark.png`. It should be in the save directory of `main.py`, otherwise there will be no system tray icon.

## Acknowledgement

- [pyzbar](https://github.com/NaturalHistoryMuseum/pyzbar)
- [Qt](https://qt.io)
- [opencv-python](https://github.com/opencv/opencv-python)
- [Python基于pyzbar、opencv、pyqt5库，实现二维码识别 gui 应用程序开发_唤醒手腕的博客-CSDN博客](https://blog.csdn.net/qq_47452807/article/details/124233469)
- [Qt项目中，实现屏幕截图功能的模块详细实现（可通用）_可吉拉多的专栏-知乎](https://zhuanlan.zhihu.com/p/212230990)