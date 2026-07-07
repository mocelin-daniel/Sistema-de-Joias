from PyQt6.QtWidgets import QVBoxLayout, QWidget, QLabel, QMainWindow, QHBoxLayout, QPushButton, QStackedWidget
from views.dashboard_view import Dashboard
from views.clientes_view import Clientes
from views.joias_view import Joias
from views.relatorio_view import Relatorio
from views.cadastros_view import Cadastros
from views.vendas_view import Vendas
from views.config_view import Config
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
import os

class MainWindow(QMainWindow): #cria a classe da janela principal, com todos seus botões e layout
    def __init__(self):
        super().__init__()
        layout_sidebar = QVBoxLayout()
        self.setFixedSize(800,600)
        logo = QLabel()
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logo_path = os.path.join(BASE_DIR, "images", "logo.png")
        pixmap = QPixmap(logo_path)
        logo.setPixmap(pixmap.scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_sidebar = QLabel("Menu")
        self.label_sidebar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pushbutton_clientes = QPushButton("Clientes") 
        self.pushbutton_joias = QPushButton("Joias")
        self.pushbutton_vendas = QPushButton("Vendas")
        self.pushbutton_cadastros = QPushButton("Cadastros")
        self.pushbutton_relatorio = QPushButton("Relatórios")
        self.pushbutton_cfg = QPushButton("Configurações")
        self.label_conteudo = QLabel("Conteúdo")
        layout_principal = QHBoxLayout()
        widget_principal = QWidget()
        widget_sidebar = QWidget()
        layout_sidebar.addWidget(self.label_sidebar)
        layout_sidebar.addWidget(self.pushbutton_clientes)
        layout_sidebar.addWidget(self.pushbutton_joias)
        layout_sidebar.addWidget(self.pushbutton_vendas)
        layout_sidebar.addWidget(self.pushbutton_cadastros)
        layout_sidebar.addWidget(self.pushbutton_relatorio)
        layout_sidebar.addWidget(self.pushbutton_cfg)
        layout_sidebar.addStretch()
        layout_sidebar.addWidget(logo)
        widget_sidebar.setLayout(layout_sidebar)
     
        self.stack = QStackedWidget()
        self.stack.addWidget(Clientes())
        self.stack.addWidget(Joias())
        self.stack.addWidget(Vendas())
        self.stack.addWidget(Cadastros())
        self.stack.addWidget(Relatorio())
        self.stack.addWidget(Config())

        layout_principal.addWidget(widget_sidebar)
        layout_principal.addWidget(self.stack)
        widget_principal.setLayout(layout_principal)
        self.setCentralWidget(widget_principal)

        #conecta todos os botões
        self.pushbutton_clientes.clicked.connect(lambda: self.abrir_pagina(0))
        self.pushbutton_joias.clicked.connect(lambda: self.abrir_pagina(1))
        self.pushbutton_vendas.clicked.connect(lambda: self.abrir_pagina(2))
        self.pushbutton_cadastros.clicked.connect(lambda: self.abrir_pagina(3))
        self.pushbutton_relatorio.clicked.connect(lambda: self.abrir_pagina(4))
        self.pushbutton_cfg.clicked.connect(lambda: self.abrir_pagina(5))

    def abrir_pagina(self, indice):
        self.stack.setCurrentIndex(indice)
        pagina_atual = self.stack.currentWidget()
        if hasattr(pagina_atual, "atualizar"):
            pagina_atual.atualizar()