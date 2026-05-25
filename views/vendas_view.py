from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton, QMessageBox
from database.db import get_connection

class Vendas(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Registrar venda!"))
        label_cliente = QLabel("Cliente:")
        self.combo_cliente = QComboBox()
        label_cpf = QLabel("CPF:")
        self.campo_cpf = QLineEdit()
        self.campo_cpf.setReadOnly(True)
        label_numero = QLabel("Número:")
        self.campo_numero = QLineEdit()
        self.campo_numero.setReadOnly(True)
        label_joia = QLabel("Produto:")
        self.combo_joia = QComboBox()
        label_valor = QLabel("Valor:")
        self.campo_valor = QLineEdit()
        self.campo_valor.setReadOnly(True)
        label_quantidade = QLabel("Quantidade: ")
        self.campo_quantidade = QLineEdit()
        label_total = QLabel("Total")
        self.campo_total = QLineEdit()
        self.campo_total.setReadOnly(True)
        label_pagamento = QLabel("Forma de Pagamento: ")
        self.combo_pagamento = QComboBox()
        self.combo_pagamento.addItems(["Débito", "Crédito", "Pix", "Dinheiro"])
        self.qpush_registrar_venda = QPushButton("Registrar Venda!")

        self.combo_cliente.currentIndexChanged.connect(self.preencher_cliente)
        self.combo_joia.currentIndexChanged.connect(self.preencher_joia)
        self.campo_quantidade.textChanged.connect(self.calcular_total)
        self.qpush_registrar_venda.clicked.connect(self.registrar_venda)

        layout.addWidget(label_cliente)
        layout.addWidget(self.combo_cliente)
        layout.addWidget(label_cpf)
        layout.addWidget(self.campo_cpf)
        layout.addWidget(label_numero)
        layout.addWidget(self.campo_numero)
        layout.addWidget(label_joia)
        layout.addWidget(self.combo_joia)
        layout.addWidget(label_valor)
        layout.addWidget(self.campo_valor)
        layout.addWidget(label_quantidade)
        layout.addWidget(self.campo_quantidade)
        layout.addWidget(label_total)
        layout.addWidget(self.campo_total)
        layout.addWidget(label_pagamento)
        layout.addWidget(self.combo_pagamento)
        layout.addWidget(self.qpush_registrar_venda)
        self.setLayout(layout)
        
        self.carregar_clientes()
        self.carregar_joias()
        
    def carregar_clientes(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome FROM clientes")
        clientes = cursor.fetchall()
        conn.close()
        for cliente in clientes:
            self.combo_cliente.addItem(cliente["nome"], cliente["id"])

    def carregar_joias(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome FROM joias WHERE quantidade > 0")
        joias = cursor.fetchall()
        conn.close()
        for joia in joias:
            self.combo_joia.addItem(joia["nome"], joia["id"])

    def preencher_cliente(self):
        id_cliente = self.combo_cliente.currentData()  # pega o id oculto
        if id_cliente is None:
            return
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT cpf, numero FROM clientes WHERE id=?", (id_cliente,))
        clientes = cursor.fetchone()
        conn.close()
        self.campo_cpf.setText(clientes["cpf"])
        self.campo_numero.setText(clientes["numero"])

    def preencher_joia(self):
        id_joia = self.combo_joia.currentData()  # pega o id oculto
        if id_joia is None:
            return
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT valor FROM joias WHERE id=?", (id_joia,))
        joias = cursor.fetchone()
        conn.close()
        self.campo_valor.setText(str(joias["valor"]))
        self.calcular_total()

    def calcular_total(self):
        try:
            valor = float(self.campo_valor.text())
            quantidade = int(self.campo_quantidade.text())
            total = valor * quantidade
            self.campo_total.setText(str(total))
        except ValueError:
            self.campo_total.setText("")

    def registrar_venda(self):
        id_cliente = self.combo_cliente.currentData()
        id_joia = self.combo_joia.currentData()
        valor_joias = self.campo_valor.text()
        quantidade = self.campo_quantidade.text()
        valor_total = self.campo_total.text()
        pagamento = self.combo_pagamento.currentText()
        if not quantidade or not id_cliente or not id_joia:
            QMessageBox.warning(self, "Atenção", "Preencha todos os campos!")
            return
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT quantidade FROM joias WHERE id = ?", (id_joia,))
        joia = cursor.fetchone()

        if int(quantidade) > joia["quantidade"]:
            QMessageBox.warning(self, "Atenção", "Estoque insuficiente!")
            conn.close()
            return
        cursor.execute("""
                        INSERT INTO vendas (cliente_id, joia_id, valor_joia, quantidade, valor_total, pagamento)
                        VALUES (?, ?, ?, ?, ?, ?)""",
                        (id_cliente, id_joia, valor_joias, quantidade, valor_total, pagamento))
        cursor.execute("""
                        UPDATE joias SET quantidade = quantidade - ? WHERE id = ?
                        """,
                        (quantidade, id_joia))
        conn.commit()
        QMessageBox.information(self, "Atenção!", "Venda registrada com sucesso!")
        self.atualizar()
        self.campo_quantidade.clear()
        conn.close()

    def atualizar(self):
        self.combo_cliente.clear()
        self.combo_joia.clear()
        self.carregar_clientes()
        self.carregar_joias()
