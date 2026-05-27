from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QTableWidget, QTableWidgetItem, QHBoxLayout
from database.db import get_connection
import sqlite3

class Clientes(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout_h = QHBoxLayout()
        layout.addWidget(QLabel("Cadastrar novos clientes!"))
        label_nome = QLabel("Nome: ")
        self.campo_nome = QLineEdit()
        label_cpf = QLabel("CPF: ")
        self.campo_cpf = QLineEdit()
        self.campo_cpf.setPlaceholderText("Digite apenas os números")
        label_numero = QLabel("Número: ")
        self.campo_numero = QLineEdit()
        self.campo_numero.setPlaceholderText("Digite apenas os números")
        label_email = QLabel("Email: ")
        self.campo_email = QLineEdit()
        label_endereco = QLabel("Endereço: (Bairro, Rua, Número)")
        self.campo_endereco = QLineEdit()
        self.salvar = QPushButton("Salvar")
        self.limpar = QPushButton("Limpar")
        self.excluir = QPushButton("Excluir")
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(6)
        self.tabela.setHorizontalHeaderLabels(["ID", "Nome", "CPF", "Número", "Email", "Endereço"])
        self.tabela.setColumnHidden(0, True)
        self.id_editando = None
        self.tabela.cellClicked.connect(self.selecionar_cliente)

        self.salvar.clicked.connect(self.salvar_cliente)
        self.limpar.clicked.connect(self.limpar_campos)
        self.excluir.clicked.connect(self.excluir_cliente)
        self.campo_cpf.textChanged.connect(self.formatar_cpf)
        self.campo_numero.textChanged.connect(self.formatar_numero)

        layout.addWidget(label_nome)
        layout.addWidget(self.campo_nome)
        layout.addWidget(label_cpf)
        layout.addWidget(self.campo_cpf)
        layout.addWidget(label_numero)
        layout.addWidget(self.campo_numero)
        layout.addWidget(label_email)
        layout.addWidget(self.campo_email)
        layout.addWidget(label_endereco)
        layout.addWidget(self.campo_endereco)
        layout_h.addWidget(self.salvar)
        layout_h.addWidget(self.limpar)
        layout_h.addWidget(self.excluir)
        layout.addLayout(layout_h)
        layout.addWidget(self.tabela)
        self.carregar_clientes()
        self.setLayout(layout)


    def salvar_cliente(self):
        nome = self.campo_nome.text().upper()
        cpf = self.campo_cpf.text()
        numero = self.campo_numero.text()
        email = self.campo_email.text()
        endereco = self.campo_endereco.text().upper()
        if not nome or not cpf or not numero or not email or not endereco:
            QMessageBox.warning(self,"Atenção", "Por favor, preencha todos os campos!")
            return

        if len(cpf.replace(".", "").replace("-", "")) != 11:
            QMessageBox.warning(self, "Atenção", "CPF inválido!")
            return

        conn = get_connection()
        cursor = conn.cursor()
        try:
            if self.id_editando is None:
                cursor.execute("""
                    INSERT INTO clientes (nome, cpf, numero, email, endereco)
                    VALUES (?, ?, ?, ?, ?)
                """, (nome, cpf, numero, email, endereco))
            else:
                cursor.execute("""
                    UPDATE clientes SET nome=?, cpf=?, numero=?, email=?, endereco=?
                    WHERE id=?
                """, (nome, cpf, numero, email, endereco, self.id_editando))
            conn.commit()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Atenção", "CPF já cadastrado!")
            conn.close()
            return
        conn.close()
        self.limpar_campos()
        QMessageBox.information(self,"Cadastro realizado!", "Cliente cadastrado com sucesso!")
        self.id_editando = None
        self.carregar_clientes()

    def limpar_campos(self):
        self.campo_nome.clear()
        self.campo_cpf.clear()
        self.campo_numero.clear()
        self.campo_email.clear()
        self.campo_endereco.clear()
        self.id_editando = None

    def carregar_clientes(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, cpf, numero, email, endereco FROM clientes")
        clientes = cursor.fetchall()
        self.tabela.setRowCount(len(clientes))

        for i, cliente in enumerate(clientes):
            self.tabela.setItem(i, 0, QTableWidgetItem(str(cliente["id"])))
            self.tabela.setItem(i, 1, QTableWidgetItem(cliente["nome"]))
            self.tabela.setItem(i, 2, QTableWidgetItem(cliente["cpf"]))
            self.tabela.setItem(i, 3, QTableWidgetItem(cliente["numero"]))
            self.tabela.setItem(i, 4, QTableWidgetItem(cliente["email"]))
            self.tabela.setItem(i, 5, QTableWidgetItem(cliente["endereco"]))

    def excluir_cliente(self):
        linha = self.tabela.currentRow()
        if linha == -1:
            QMessageBox.warning(self, "Atenção", "Selecione um cliente para excluir!")
            return
        
        id_cliente = self.tabela.item(linha, 0).text()  # pega o id primeiro
        conn = get_connection()                        # abre conexão
        cursor = conn.cursor()                         # cria cursor
        
        cursor.execute("SELECT COUNT(*) as total FROM vendas WHERE cliente_id = ?", (id_cliente,))
        resultado = cursor.fetchone()
        if resultado["total"] > 0:
            QMessageBox.warning(self, "Atenção", 
                f"Esse cliente possui {resultado['total']} venda(s) registrada(s) e não pode ser excluído!")
            conn.close()
            return

        msg = QMessageBox()
        msg.setWindowTitle("Confirmar exclusão")
        msg.setText("Tem certeza que deseja excluir o cliente selecionado?")
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg.button(QMessageBox.StandardButton.Yes).setText("Sim")
        msg.button(QMessageBox.StandardButton.No).setText("Não")
        resposta = msg.exec()

        if resposta == QMessageBox.StandardButton.No:
            return
        cursor.execute("DELETE FROM clientes WHERE id = ?", (id_cliente,))
        QMessageBox.information(self, "Atenção", "Cliente deletado com sucesso!")
        conn.commit()
        conn.close()
        self.carregar_clientes()
        self.limpar_campos()
        
    def selecionar_cliente(self, linha, coluna):
        self.campo_nome.setText(self.tabela.item(linha, 1).text())
        self.campo_cpf.setText(self.tabela.item(linha, 2).text())
        self.campo_numero.setText(self.tabela.item(linha, 3).text())
        self.campo_email.setText(self.tabela.item(linha, 4).text())
        self.campo_endereco.setText(self.tabela.item(linha, 5).text())
        self.id_editando = self.tabela.item(linha, 0).text()

    def formatar_cpf(self, texto):
        numeros = ''.join(filter(str.isdigit, texto))
        
        # limita a 11 dígitos
        if len(numeros) > 11:
            numeros = numeros[:11]
        
        # formata conforme vai digitando
        if len(numeros) <= 3:
            formatado = numeros
        elif len(numeros) <= 6:
            formatado = f"{numeros[:3]}.{numeros[3:]}"
        elif len(numeros) <= 9:
            formatado = f"{numeros[:3]}.{numeros[3:6]}.{numeros[6:]}"
        else:
            formatado = f"{numeros[:3]}.{numeros[3:6]}.{numeros[6:9]}-{numeros[9:]}"
        
        self.campo_cpf.blockSignals(True)
        self.campo_cpf.setText(formatado)
        self.campo_cpf.blockSignals(False)

    def formatar_numero(self, texto):
        numeros = ''.join(filter(str.isdigit, texto))
        
        # limita a 11 dígitos
        if len(numeros) > 11:
            numeros = numeros[:11]
        
        # formata conforme vai digitando
        if len(numeros) <= 2:
            formatado = f"{numeros}"
        elif len(numeros) <= 7:
            formatado = f"({numeros[:2]}) {numeros[2:]}"
        elif len(numeros) <= 11:
            formatado = f"({numeros[:2]}) {numeros[2:7]}-{numeros[7:]}"
        
        self.campo_numero.blockSignals(True)
        self.campo_numero.setText(formatado)
        self.campo_numero.blockSignals(False)