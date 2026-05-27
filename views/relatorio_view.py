from PyQt6.QtWidgets import QVBoxLayout, QWidget, QLabel, QComboBox, QPushButton, QTableWidget, QHBoxLayout, QLineEdit, QTableWidgetItem
from datetime import datetime
from database.db import get_connection

class Relatorio(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Relatório de vendas!"))
        layout_filtros = QHBoxLayout()
        layout.addLayout(layout_filtros)
        self.label_mes = QLabel("Mês:")
        self.combo_mes = QComboBox()
        self.combo_mes.addItem("Todos", 0)
        self.combo_mes.addItems(["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                                 "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"])
        self.label_ano = QLabel("Ano:")
        self.combo_ano = QComboBox()
        self.label_cliente = QLabel("Cliente:")
        self.combo_cliente = QComboBox()
        self.label_joia = QLabel("Jóia")
        self.combo_joia = QComboBox()
        self.label_pagamento = QLabel("Pagamento:")
        self.combo_pagamento = QComboBox()
        self.combo_pagamento.addItem("Todos", 0)
        self.combo_pagamento.addItems(["Débito", "Crédito", "Pix", "Dinheiro"])
        self.filtrar = QPushButton("Filtrar")
        self.total_vendas = QLabel("Total de Vendas:")
        self.campo_vendas = QLineEdit()
        self.campo_vendas.setReadOnly(True)
        self.faturamento = QLabel("Faturamento:")
        self.campo_faturamento = QLineEdit()
        self.campo_faturamento.setReadOnly(True)
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(6)
        self.tabela.setHorizontalHeaderLabels(["ID","Cliente", "Joia","Quantidade", "Total", "Pagamento"])

        self.filtrar.clicked.connect(self.filtrar_vendas)

        layout_filtros.addWidget(self.label_mes)
        layout_filtros.addWidget(self.combo_mes)
        layout_filtros.addWidget(self.label_ano)
        layout_filtros.addWidget(self.combo_ano)
        layout_filtros.addWidget(self.label_cliente)
        layout_filtros.addWidget(self.combo_cliente)
        layout_filtros.addWidget(self.label_joia)
        layout_filtros.addWidget(self.combo_joia)
        layout_filtros.addWidget(self.label_pagamento)
        layout_filtros.addWidget(self.combo_pagamento)
        
        layout.addWidget(self.filtrar)
        layout.addWidget(self.total_vendas)
        layout.addWidget(self.campo_vendas)
        layout.addWidget(self.faturamento)
        layout.addWidget(self.campo_faturamento)
        layout.addWidget(self.tabela)
        self.setLayout(layout)

        self.carregar_clientes()
        self.carregar_joias()

        ano_atual = datetime.now().year
        self.combo_ano.addItem("Todos", 0)
        for ano in range(ano_atual, ano_atual - 4, -1):
            self.combo_ano.addItem(str(ano), ano)

    def carregar_joias(self):
        self.combo_joia.addItem("Todos", 0)
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome FROM joias")
        joias = cursor.fetchall()
        conn.close()
        for joia in joias:
            self.combo_joia.addItem(joia["nome"], joia["id"])

    def carregar_clientes(self):
        self.combo_cliente.addItem("Todos", 0)
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome FROM clientes")
        clientes = cursor.fetchall()
        conn.close()
        for cliente in clientes:
            self.combo_cliente.addItem(cliente["nome"], cliente["id"])

    def filtrar_vendas(self):
        query = """
        SELECT v.id, c.nome as nome_cliente, j.nome as nome_joia, 
            v.quantidade, v.valor_total, v.pagamento
        FROM vendas v
        JOIN clientes c ON c.id = v.cliente_id
        JOIN joias j ON j.id = v.joia_id
        WHERE 1=1
        """
        parametros = []

        # se cliente não for "Todos"
        id_cliente = self.combo_cliente.currentData()
        if id_cliente != 0:
            query += " AND v.cliente_id = ?"
            parametros.append(id_cliente)

        id_joia = self.combo_joia.currentData()
        if id_joia != 0:
            query += " AND v.joia_id = ?"
            parametros.append(id_joia)

        pagamento = self.combo_pagamento.currentText()
        if pagamento != "Todos":
            query += " AND v.pagamento = ?"
            parametros.append(pagamento)

        mes = self.combo_mes.currentIndex()  # 0 = Todos, 1 = Janeiro, etc
        if mes != 0:
            query += " AND strftime('%m', v.data_venda) = ?"
            parametros.append(f"{mes:02d}")  # formata como "01", "02"...

        ano = self.combo_ano.currentData()
        if ano != 0:
            query += " AND strftime('%Y', v.data_venda) = ?"
            parametros.append(str(ano))

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query, parametros)
        vendas = cursor.fetchall()
        self.tabela.setRowCount(len(vendas))
        total = len(vendas)
        faturamento = sum(venda["valor_total"] for venda in vendas)
        self.campo_vendas.setText(str(total))
        self.campo_faturamento.setText(f"R$ {faturamento:.2f}")

        for i, venda in enumerate(vendas):
            self.tabela.setItem(i, 0, QTableWidgetItem(str(venda["id"])))
            self.tabela.setItem(i, 1, QTableWidgetItem(venda["nome_cliente"]))
            self.tabela.setItem(i, 2, QTableWidgetItem(venda["nome_joia"]))
            self.tabela.setItem(i, 3, QTableWidgetItem(str(venda["quantidade"])))
            self.tabela.setItem(i, 4, QTableWidgetItem(str(venda["valor_total"])))
            self.tabela.setItem(i, 5, QTableWidgetItem(str(venda["pagamento"])))
        
        conn.close()

    def atualizar(self):
        self.combo_cliente.clear()
        self.combo_joia.clear()
        self.carregar_clientes()
        self.carregar_joias()