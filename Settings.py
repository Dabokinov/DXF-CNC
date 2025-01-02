# -*- coding: utf-8 -*-
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QCheckBox, QPushButton
from PySide6.QtGui import QDoubleValidator

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройки")
        self.setGeometry(300, 300, 400, 400)
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Загибатель
        layout.addWidget(QLabel("Загибатель"))
        self.angle_start_input = self.create_validated_lineedit("Угол от начальной точки до профиля")
        layout.addWidget(self.angle_start_input)

        self.safe_angle_input = self.create_validated_lineedit("Безопасный угол")
        layout.addWidget(self.safe_angle_input)

        self.step_angle_input = self.create_validated_lineedit("Угол на 1 шаг загибателя")
        layout.addWidget(self.step_angle_input)

        self.delay_input = self.create_validated_lineedit("Задержка после команды выдвижения штока")
        layout.addWidget(self.delay_input)

        self.bender_checkbox = QCheckBox("Активировать загибатель")
        layout.addWidget(self.bender_checkbox)

        # Перемещение
        layout.addWidget(QLabel("Перемещение"))
        self.joint_length_input = self.create_validated_lineedit("Длина стыковой части")
        layout.addWidget(self.joint_length_input)

        self.joint_check = QCheckBox("Делать стыковую часть")
        layout.addWidget(self.joint_check)

        self.gap_distance_input = self.create_validated_lineedit("Расстояние от канавки до точки сгиба")
        layout.addWidget(self.gap_distance_input)

        self.step_length_input = self.create_validated_lineedit("Длина 1 шага для перемещения")
        layout.addWidget(self.step_length_input)

        # Канавка
        layout.addWidget(QLabel("Канавка"))
        self.groove_length_input = self.create_validated_lineedit("Длина канавки (размер профиля)")
        layout.addWidget(self.groove_length_input)

        self.step_z_input = self.create_validated_lineedit("Длина 1 шага перемещения Z")
        layout.addWidget(self.step_z_input)

        self.tool_step_input = self.create_validated_lineedit("Длина 1 шага резца")
        layout.addWidget(self.tool_step_input)

        self.tool_depth_input = self.create_validated_lineedit("Расстояние заглубления резца, чтобы сделать канавку")
        layout.addWidget(self.tool_depth_input)

        self.groove_checkbox = QCheckBox("Активировать канавку")
        layout.addWidget(self.groove_checkbox)

        self.save_button = QPushButton("Сохранить настройки")
        self.save_button.clicked.connect(self.save_settings)
        layout.addWidget(self.save_button)

    def create_validated_lineedit(self, placeholder):
        lineedit = QLineEdit()
        lineedit.setPlaceholderText(placeholder)
        validator = QDoubleValidator(0, 9999, 2)  # Действительные числа от 0 до 9999 с 2 знаками после точки
        lineedit.setValidator(validator)
        return lineedit

    def save_settings(self):
        # Валидация перед сохранением
        if not self.angle_start_input.text() or not self.safe_angle_input.text():
            self.parent().status_bar.showMessage("Ошибка: заполните все обязательные поля!")
            return

        #Вместо примера будет добавлена логика сохранения настроек
        self.parent().status_bar.showMessage("Настройки сохранены!")
        self.accept()
