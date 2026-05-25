from PyQt6.QtWidgets import QVBoxLayout, QWidget, QLabel, QMainWindow, QHBoxLayout, QPushButton, QStackedWidget
from views.dashboard_view import Dashboard
from views.clientes_view import Clientes
from views.joias_view import Joias
from views.relatorio_view import Relatorio
from views.vendas_view import Vendas

class MainWindow(QMainWindow): #cria a classe da janela principal, com todos seus botões e layout
    def __init__(self):
        super().__init__()
        self.setFixedSize(800,600)
        self.label_sidebar = QLabel("Menu")
        self.pushbutton_clientes = QPushButton("Cadastrar Clientes") 
        self.pushbutton_joias = QPushButton("Cadastrar Joias")
        self.pushbutton_vendas = QPushButton("Registrar Vendas")
        self.pushbutton_relatorio = QPushButton("Visualizar Vendas")
        self.label_conteudo = QLabel("Conteúdo")
        layout_principal = QHBoxLayout()
        widget_principal = QWidget()
        widget_sidebar = QWidget()
        layout_sidebar = QVBoxLayout()
        layout_sidebar.addWidget(self.label_sidebar)
        layout_sidebar.addWidget(self.pushbutton_clientes)
        layout_sidebar.addWidget(self.pushbutton_joias)
        layout_sidebar.addWidget(self.pushbutton_vendas)
        layout_sidebar.addWidget(self.pushbutton_relatorio)
        widget_sidebar.setLayout(layout_sidebar)
     
        self.stack = QStackedWidget()
        self.stack.addWidget(Clientes())
        self.stack.addWidget(Joias())
        self.stack.addWidget(Vendas())
        self.stack.addWidget(Relatorio())

        layout_principal.addWidget(widget_sidebar)
        layout_principal.addWidget(self.stack)
        widget_principal.setLayout(layout_principal)
        self.setCentralWidget(widget_principal)

        #conecta todos os botões
        self.pushbutton_clientes.clicked.connect(lambda: self.abrir_pagina(0))
        self.pushbutton_joias.clicked.connect(lambda: self.abrir_pagina(1))
        self.pushbutton_vendas.clicked.connect(lambda: self.abrir_pagina(2))
        self.pushbutton_relatorio.clicked.connect(lambda: self.abrir_pagina(3))

    def abrir_pagina(self, indice):
        self.stack.setCurrentIndex(indice)
        pagina_atual = self.stack.currentWidget()
        if hasattr(pagina_atual, "atualizar"):
            pagina_atual.atualizar()