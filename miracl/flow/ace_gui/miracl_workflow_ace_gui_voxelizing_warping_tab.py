# voxelizing_warping_tab.py
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QLabel,
    QComboBox,
    QSpinBox,
)
from PyQt5.QtCore import Qt


class VoxelizingWarpingTab(QWidget):
    def __init__(self):
        super().__init__()
        voxelizing_warping_layout = QFormLayout()
        self.setLayout(voxelizing_warping_layout)

        # Add widgets for the Voxelizing/warping tab here
        # ...

        self.create_section_title(voxelizing_warping_layout, "<b>Voxelization</b>")

        self.create_labels_voxel_size(voxelizing_warping_layout)

    def create_labels_voxel_size(self, layout):
        label = self.create_indented_label("Labels voxel size:")
        combo = self.create_combo(["10", "25", "50"])
        layout.addRow(label, combo)

    def create_indented_label(self, text):
        return QLabel("  " + text)

    def create_section_title(self, layout, text):
        layout.addRow(QLabel(text))

    def create_combo(self, items):
        combo = QComboBox()
        combo.addItems(items)
        return combo
