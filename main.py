import sys
from PyQt6.QtWidgets import QApplication
from views.main_window import MainWindow
from database.db import criar_tabelas

criar_tabelas()

app = QApplication(sys.argv)
janela = MainWindow()
janela.setWindowTitle("Carmem Jóias")
janela.show()
sys.exit(app.exec())