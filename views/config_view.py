from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from database.db import get_connection


class Config(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Configurações"))
        
        # campos
        label_chave = QLabel("Chave Pix: (Digite apenas os números)")
        self.campo_chave = QLineEdit()
        self.campo_chave.setEchoMode(QLineEdit.EchoMode.Password)
        label_nome = QLabel("Nome Completo (Pix):")
        self.campo_nome = QLineEdit()
        self.campo_nome.setEchoMode(QLineEdit.EchoMode.Password)
        label_cidade = QLabel("Cidade:")
        self.campo_cidade = QLineEdit()
        self.campo_cidade.setEchoMode(QLineEdit.EchoMode.Password)
        self.alterar = QPushButton("Exibir")
        self.alterar.clicked.connect(self.alterar_visibilidade_senha)
        self.salvar = QPushButton("Salvar")
        self.salvar.clicked.connect(self.salvar_config)

        self.lista_campos = [self.campo_chave, self.campo_cidade, self.campo_nome]
        
        layout.addWidget(label_chave)
        layout.addWidget(self.campo_chave)
        layout.addWidget(label_nome)
        layout.addWidget(self.campo_nome)
        layout.addWidget(label_cidade)
        layout.addWidget(self.campo_cidade)
        layout.addWidget(self.salvar)
        layout.addWidget(self.alterar)
        layout.addStretch()
        self.setLayout(layout)
        self.carregar_config()

    def salvar_config(self):
        chave = self.campo_chave.text().strip()
        nome = self.campo_nome.text().title()
        cidade = self.campo_cidade.text().title()
        
        if not chave or not nome or not cidade:
            QMessageBox.warning(self, "Atenção", "Preencha todos os campos!")
            return
        
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO configs(id, chave_pix, nome, cidade)
            VALUES(1, ?, ?, ?)
        """,(chave, nome, cidade))

        conn.commit()
        conn.close()
        QMessageBox.information(self, "Sucesso", "Dados PIX Salvos.")

    def carregar_config(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT chave_pix, nome, cidade FROM configs WHERE id=1")
        config = cursor.fetchone()
        conn.close()
        if config:
            self.campo_chave.setText(config["chave_pix"])
            self.campo_nome.setText(config["nome"])
            self.campo_cidade.setText(config["cidade"])

    def alterar_visibilidade_senha(self):
        if self.campo_nome.echoMode() == QLineEdit.EchoMode.Password:
            toggle = QLineEdit.EchoMode.Normal
            text_toggle = ("Ocultar")
        else:
            toggle = QLineEdit.EchoMode.Password
            text_toggle = ("Exibir")

        for campo in self.lista_campos:
            campo.setEchoMode(toggle)
            self.alterar.setText(text_toggle)