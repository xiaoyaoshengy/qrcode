import cv2
import pyzbar.pyzbar as pyzbar
from tempfile import TemporaryDirectory
from copy import copy
from enum import Enum
from typing import Optional
from typing_extensions import Self
from PySide6.QtCore import QSize, QPoint, Slot, QDateTime, Qt
from PySide6.QtWidgets import QWidget, QMenu, QSystemTrayIcon
from PySide6.QtGui import QGuiApplication, QPixmap, QPainter, QPen, QScreen, QColor, QMouseEvent, QKeySequence, QClipboard, QIcon


class Screen:
    class STATUS(Enum):
        SELECT = 1      # 选择区域
        MOV = 2         # 移动区域
        SET_W_H = 3     # 设置 width height
    
    def __init__(self, size: QSize) -> None:
        self.max_width: int = size.width()                  # 屏幕最大宽度
        self.max_height: int = size.height()                # 屏幕最大高度
        self.start_pos: QPoint = QPoint(-1, -1)             # 开始坐标
        self.end_pos: QPoint = self.start_pos               # 结束坐标
        self.left_up_pos: QPoint = self.start_pos           # 截图区域左上角坐标
        self.right_down_pos: QPoint = self.start_pos        # 截图区域右下角坐标
        self.status: Screen.STATUS = Screen.STATUS.SELECT   # 鼠标状态

    def width(self) -> int:
        return self.max_width

    def height(self) -> int:
        return self.max_height

    def get_status(self) -> STATUS:
        return self.status

    def set_status(self, status: STATUS) -> None:
        self.status = status

    def compare_point(self, left_up: QPoint, right_down: QPoint) -> None:
        l: QPoint = copy(left_up)
        r: QPoint = copy(right_down)

        if l.x() <= r.x():
            if l.y() > r.y():
                left_up.setY(r.y())
                right_down.setY(l.y())
        else:
            if l.y() < r.y():
                left_up.setX(r.x())
                right_down.setX(l.x())
            else:
                tmp: QPoint = left_up
                left_up = right_down
                right_down = tmp

    def set_end(self, pos: QPoint) -> None:
        self.end_pos = pos
        self.left_up_pos = self.start_pos
        self.right_down_pos = self.end_pos
        self.compare_point(self.left_up_pos, self.right_down_pos)

    def set_start(self, pos: QPoint) -> None:
        self.start_pos = pos

    def get_end(self) -> QPoint:
        return self.end_pos

    def get_start(self) -> QPoint:
        return self.start_pos

    def get_left_up(self) -> QPoint:
        return self.left_up_pos

    def get_right_down(self) -> QPoint:
        return self.right_down_pos

    def is_in_area(self, pos: QPoint) -> bool:
        if self.left_up_pos.x() < pos.x() < self.right_down_pos.x() and self.left_up_pos.y() < pos.y() < self.right_down_pos.y():
            return True
        return False

    def move(self, p: QPoint) -> None:
        lx: int = self.left_up_pos.x() + p.x()
        ly: int = self.left_up_pos.y() + p.y()
        rx: int = self.right_down_pos.x() + p.x()
        ry: int = self.right_down_pos.y() + p.y()

        if lx < 0:
            lx = 0
            rx -= p.x()

        if ly < 0:
            ly = 0
            ry -= p.y()

        if rx > self.max_width:
            rx = self.max_width
            lx -= p.x()

        if ry > self.max_height:
            ry = self.max_height
            ly -= p.y()

        self.left_up_pos = QPoint(lx, ly)
        self.right_down_pos = QPoint(rx, ry)
        self.start_pos = self.left_up_pos
        self.end_pos = self.right_down_pos


class ScreenWidget(QWidget):
    def __init__(self, parent: Optional[QWidget] = ...) -> None:
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.X11BypassWindowManagerHint | Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.screen: Screen = Screen(QGuiApplication.primaryScreen().size())  # 取得屏幕大小
        self.full_screen: QPixmap = QPixmap()  # 保存全屏图像
        self.bg_screen: QPixmap = QPixmap()  # 模糊背景图
        self.mov_pos: QPoint = QPoint()  # 坐标
        self.menu: QMenu = QMenu(self)  # 右键菜单
        self.menu.addAction("识别二维码", self.recognize_qrcode)
        self.menu.addAction("退出截图", self.hide, QKeySequence.StandardKey.Cancel)
        self.sys_tray_icon: QSystemTrayIcon = QSystemTrayIcon(QIcon("sys_icon_dark.png"))
        self.sys_tray_menu: QMenu = QMenu()
        self.sys_tray_menu.addAction("识别", self.showFullScreen)
        self.sys_tray_menu.addAction("退出", QGuiApplication.quit)
        self.sys_tray_icon.setContextMenu(self.sys_tray_menu)
        self.sys_tray_icon.show()

    def __new__(cls, parent: Optional[QWidget] = ...) -> Self:
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls, parent)
        return cls._instance

    @Slot()
    def recognize_qrcode(self) -> None:
        x: int = self.screen.get_left_up().x()
        y: int = self.screen.get_left_up().y()
        w: int = self.screen.get_right_down().x() - x
        h: int = self.screen.get_right_down().y() - y

        with TemporaryDirectory() as tmp_dir:
            filename: str = f"{tmp_dir}/screen_{QDateTime.currentDateTime().toString('yyyy-MM-dd-HH-mm-ss')}.png"
            self.full_screen.copy(x, y, w, h).save(filename, "png")
            img = cv2.imread(filename)
            img = cv2.resize(img, (0, 0), fx=0.5, fy=0.5)
            barcodes = pyzbar.decode(img)
            for barcode in barcodes:
                barcode_data = barcode.data.decode("utf-8")
                clipboard = QGuiApplication.clipboard()
                clipboard.setText(barcode_data)
        self.hide()

    def paintEvent(self, _) -> None:
        x: int = self.screen.get_left_up().x()
        y: int = self.screen.get_left_up().y()
        w: int = self.screen.get_right_down().x() - x
        h: int = self.screen.get_right_down().y() - y

        painter: QPainter = QPainter(self)

        pen: QPen = QPen()
        pen.setColor(Qt.GlobalColor.green)
        pen.setWidth(2)
        pen.setStyle(Qt.PenStyle.DotLine)
        painter.setPen(pen)
        painter.drawPixmap(0, 0, self.bg_screen)

        if w != 0 and h != 0:
            painter.drawPixmap(x, y, self.full_screen.copy(x, y, w, h))

        painter.drawRect(x, y, w, h)

        pen.setColor(Qt.GlobalColor.yellow)
        painter.setPen(pen)
        painter.drawText(x + 2, y - 8, f"截图范围：( {x} x {y} ) - ( {x + w} x {y + h} ) 图片大小：( {w} x {h} )")

    def showEvent(self, _) -> None:
        point: QPoint = QPoint(-1, -1)
        self.screen.set_start(point)
        self.screen.set_end(point)

        pscreen: QScreen = QGuiApplication.primaryScreen()
        self.full_screen = pscreen.grabWindow()

        # 设置透明度实现模糊背景
        pix: QPixmap = QPixmap(self.screen.width(), self.screen.height())
        pix.fill(QColor(160, 160, 160, 200))
        self.bg_screen = QPixmap(self.full_screen)
        p: QPainter = QPainter(self.bg_screen)
        p.drawPixmap(0, 0, pix)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self.screen.get_status() is Screen.STATUS.SELECT:
            self.screen.set_end(event.pos())
        elif self.screen.get_status() is Screen.STATUS.MOV:
            p: QPoint = QPoint(event.x() - self.mov_pos.x(), event.y() - self.mov_pos.y())
            self.screen.move(p)
            self.mov_pos = event.pos()

        self.update()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        status: Screen.STATUS = self.screen.get_status()
        if status is Screen.STATUS.SELECT:
            self.screen.set_start(event.pos())
        elif status is Screen.STATUS.MOV:
            if self.screen.is_in_area(event.pos()) is False:
                self.screen.set_start(event.pos())
                self.screen.set_status(Screen.STATUS.SELECT)
            else:
                self.mov_pos = event.pos()
                self.setCursor(Qt.CursorShape.SizeAllCursor)

        self.update()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if self.screen.get_status() is Screen.STATUS.SELECT:
            self.screen.set_status(Screen.STATUS.MOV)
        elif self.screen.get_status() is Screen.STATUS.MOV:
            self.setCursor(Qt.CursorShape.ArrowCursor)

    def contextMenuEvent(self, _) -> None:
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.menu.exec(self.cursor().pos())