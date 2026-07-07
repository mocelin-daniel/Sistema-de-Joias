import sys
from PyQt6.QtWidgets import QApplication
from views.main_window import MainWindow
from database.db import criar_tabelas
from PyQt6.QtGui import QIcon
from utils import resource_path

criar_tabelas()

app = QApplication(sys.argv)
janela = MainWindow()
janela.setWindowTitle("Carmem Joias")
icone_path = resource_path("images/crop_icon.ico")
app.setWindowIcon(QIcon(icone_path))
janela.setWindowIcon(QIcon(icone_path)) 
janela.show()
sys.exit(app.exec())