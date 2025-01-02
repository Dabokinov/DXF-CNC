# -*- coding: utf-8 -*-
import sys
import math
import chardet
import ezdxf
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QGraphicsScene, QDialog, QVBoxLayout, QPushButton, QLineEdit, QTextEdit, QLabel, QHBoxLayout, QSizePolicy,QCheckBox
from PySide6.QtCore import Qt, QTimer, QRectF
from PySide6.QtGui import QPen, QColor, QDoubleValidator
from mainwindow import Ui_QtWidgetsApplication1Class
from Settings import SettingsDialog


class ControllerMonitor(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Монитор контроллера")
        self.setGeometry(200, 200, 400, 300)
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.connection_status = QLabel("Статус: Не подключен")
        layout.addWidget(self.connection_status)

        self.port_input = QLineEdit()
        self.port_input.setPlaceholderText("Введите порт (например, COM3)")
        layout.addWidget(self.port_input)

        self.connect_button = QPushButton("Подключить")
        layout.addWidget(self.connect_button)

        self.output_log = QTextEdit()
        self.output_log.setReadOnly(True)
        layout.addWidget(self.output_log)

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_QtWidgetsApplication1Class()
        self.ui.setupUi(self)

        # Связь сигналов с методами
        self.ui.pushButton.clicked.connect(self.load_dxf_file)  # Загрузить файл
        self.ui.pushButton_2.clicked.connect(self.edit_joint)  # Изменить точки стыка
        self.ui.pushButton_4.clicked.connect(self.start_bend)  # Старт
        self.ui.pushButton_5.clicked.connect(self.stop_bend)  # Стоп
        self.ui.pushButton_8.clicked.connect(self.next_point)  # Следующая точка
        self.ui.pushButton_6.clicked.connect(self.pause_bend)  # Пауза
        self.ui.pushButton_12.clicked.connect(self.open_monitor)  # Монитор контроллера
        self.ui.settings_button.clicked.connect(self.open_settings_dialog) # настройки
        

        # Переменные
        self.entities = []
        self.commands = []
        self.serial_port = None
        self.scene = QGraphicsScene()
        self.ui.graphicsView.setScene(self.scene)
        self.scale_factor = 1.0

        self.current_point_index = 0
        self.bend_in_progress = False
        self.timer = QTimer()
        self.timer.timeout.connect(self.process_next_point)
        

        self.marker = None  # Маркер, который перемещается

        # Настройка QLineEdit для чисел
        self.setup_lineedit_for_numbers()

        # Настройка масштабирования и авторазмера
        self.ui.graphicsView.wheelEvent = self.scale_graphics_view
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
    def open_settings_dialog(self):
        self.settings_window = SettingsDialog(self)
        self.settings_window.exec()

    def setup_lineedit_for_numbers(self):
        validator = QDoubleValidator()
        validator.setBottom(0)  # Минимальное значение - 0
        self.ui.lineEdit.setValidator(validator)
        self.ui.lineEdit_2.setValidator(validator)
        self.ui.lineEdit_3.setValidator(validator)
        self.ui.lineEdit_4.setValidator(validator)
        self.ui.lineEdit_5.setValidator(validator)
        self.ui.lineEdit_6.setValidator(validator)

    def open_monitor(self):
        monitor = ControllerMonitor(self)
        monitor.exec()


    def load_dxf_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Открыть DXF файл", "", "DXF Files (*.dxf)")
        if file_path:
            try:
                with open(file_path, 'rb') as f:
                    raw_data = f.read()
                    encoding = chardet.detect(raw_data)['encoding']
                doc = ezdxf.readfile(file_path)
                self.entities = list(doc.modelspace().query("LINE CIRCLE ARC"))
                self.visualize_dxf()
                self.generate_commands()
                self.ui.plainTextEdit.clear()
                self.ui.plainTextEdit.setPlainText("Команды сгенерированы и файл загружен.")
            except Exception as e:
                self.ui.plainTextEdit.clear()
                self.ui.plainTextEdit.setPlainText(f"Ошибка при загрузке DXF: {e}")

    def visualize_dxf(self):
        self.scene.clear()
        self.points = []
        for entity in self.entities:
            if entity.dxftype() == 'LINE':
                start = entity.dxf.start
                end = entity.dxf.end
                self.scene.addLine(
                    start.x, -start.y, end.x, -end.y,
                    QPen(QColor("blue"), 1)
                )
                self.points.append((start.x, -start.y))
                self.points.append((end.x, -end.y))
            elif entity.dxftype() == 'CIRCLE':
                center = entity.dxf.center
                radius = entity.dxf.radius
                self.scene.addEllipse(
                    center.x - radius, -center.y - radius,
                    radius * 2, radius * 2,
                    QPen(QColor("green"), 1)
                )
            elif entity.dxftype() == 'ARC':
                self.visualize_arc(entity)

        if self.points:
            self.add_marker(self.points[0])

    def visualize_arc(self, entity):
        center = entity.dxf.center
        radius = entity.dxf.radius
        start_angle = entity.dxf.start_angle
        end_angle = entity.dxf.end_angle
        step = 10  # шаг в градусах для сегментации дуги

        points = []
        for angle in range(int(start_angle), int(end_angle) + 1, step):
            x = center.x + radius * math.cos(math.radians(angle))
            y = center.y + radius * math.sin(math.radians(angle))
            points.append((x, -y))

        for i in range(len(points) - 1):
            self.scene.addLine(
                points[i][0], points[i][1], points[i + 1][0], points[i + 1][1],
                QPen(QColor("red"), 1)
            )
        self.points.extend(points)

    def add_marker(self, position):
        if self.marker:
            self.scene.removeItem(self.marker)
        self.marker = self.scene.addRect(
            QRectF(position[0] - 3, position[1] - 3, 6, 6), QPen(QColor("red")), QColor("red")
        )
        
    def edit_joint(self):
        self.ui.plainTextEdit.clear()
        self.ui.plainTextEdit.setPlainText("Изменение точек стыка выполнено.")

    def start_bend(self):
        if not self.bend_in_progress:
            self.ui.plainTextEdit.appendPlainText("Начинаем загиб...")
            self.bend_in_progress = True
            self.current_point_index = 0
            self.timer.start(1000)

    def stop_bend(self):
        self.ui.plainTextEdit.appendPlainText("Загиб остановлен.")
        self.bend_in_progress = False
        self.timer.stop()

    def pause_bend(self):
        if self.bend_in_progress:
            self.ui.plainTextEdit.appendPlainText("Загиб приостановлен.")
            self.bend_in_progress = False
            self.timer.stop()

    def next_point(self):
        self.ui.plainTextEdit.appendPlainText("Следующая точка загиба...")
        self.process_next_point()


    def process_next_point(self):
        if self.current_point_index < len(self.points):
            x, y = self.points[self.current_point_index]
            self.scene.addEllipse(x - 2, y - 2, 4, 4, QPen(QColor("red")))
            command = self.commands[self.current_point_index % len(self.commands)]
            self.send_command(command)
            self.ui.plainTextEdit.appendPlainText(f"Обработана точка: {x}, {y}, команда: {command}")
            self.current_point_index += 1
        else:
            self.stop_bend()


    def scale_graphics_view(self, event):
        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0 and self.scale_factor < 1.5:
                self.scale_factor *= 1.1
            elif delta < 0 and self.scale_factor > 0.5:
                self.scale_factor /= 1.1
            self.ui.graphicsView.resetTransform()
            self.ui.graphicsView.scale(self.scale_factor, self.scale_factor)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_app = MainApp()
    main_app.show()
    sys.exit(app.exec())
