#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Input validator

Description:
    Validation logic for GUI to CLI input.

Copyright:
    (c) 2025 AICONs Lab. All rights reserved.

Author:
    Jonas Osmann
    j.osmann@mail.utoronto.ca

License:
    GPL-3.0
"""

from miracl.flow import miracl_workflow_ace_parser


def validate_ace_workflow_input(args):
    parser = miracl_workflow_ace_parser.ACEWorkflowParser()
    print(parser.parse_args(args))


import subprocess
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget


class CommandRunner(QThread):
    finished = pyqtSignal(bool, str)

    def __init__(self, command):
        super().__init__()
        self.command = command

    def run(self):
        try:
            result = subprocess.run(
                self.command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True,
            )
            self.finished.emit(True, result.stdout)
        except subprocess.CalledProcessError as e:
            self.finished.emit(False, e.stderr)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Command Line Runner")

        self.run_button = QPushButton("Run Command")
        self.run_button.clicked.connect(self.run_command)

        layout = QVBoxLayout()
        layout.addWidget(self.run_button)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.command_runner = None

    def run_command(self):
        self.run_button.setEnabled(False)
        self.command_runner = CommandRunner(["python", "script.py"])
        self.command_runner.finished.connect(self.handle_command_result)
        self.command_runner.start()

    def handle_command_result(self, success, output):
        if success:
            print("Command executed successfully!")
            print(output)
        else:
            print("Command failed:")
            print(output)
        self.run_button.setEnabled(True)


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
