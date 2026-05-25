from PyQt6.QtWidgets import QVBoxLayout, QWidget, QLabel

class Relatorio(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Relatório de vendas!"))
        self.setLayout(layout)