from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel


class Tab1(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("This is the content of Tab 1"))
        self.setLayout(layout)
