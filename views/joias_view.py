from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QTableWidget, QTableWidgetItem, QComboBox
from database.db import get_connection

class Joias(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Cadastrar novas joias!"))
        label_nome = QLabel("Nome: ")
        self.campo_nome = QLineEdit()
        label_tipo = QLabel("Tipo: ")
        self.campo_tipo = QLineEdit()
        label_material = QLabel("Material: ")
        self.campo_material = QComboBox()
        self.campo_material.addItems(["Ouro", "Prata", "Aço", "Bronze", "Platina", "Outro"])
        label_quantidade = QLabel("Quantidade: ")
        self.campo_quantidade = QLineEdit()
        label_valor = QLabel("Preço: R$")
        self.campo_valor = QLineEdit()
        label_descricao = QLabel("Descrição: ")
        self.campo_descricao = QLineEdit()
        self.salvar = QPushButton("Salvar")
        self.limpar = QPushButton("Limpar")
        self.excluir = QPushButton("Excluir")
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(6)
        self.tabela.setHorizontalHeaderLabels(["ID", "Nome", "Tipo", "Material", "Quantidade", "Valor"])
        self.id_editando = None
        self.tabela.cellClicked.connect(self.selecionar_joia)

        self.salvar.clicked.connect(self.salvar_joia)
        self.limpar.clicked.connect(self.limpar_campos)
        self.excluir.clicked.connect(self.excluir_joia)

        layout.addWidget(label_nome)
        layout.addWidget(self.campo_nome)
        layout.addWidget(label_tipo)
        layout.addWidget(self.campo_tipo)
        layout.addWidget(label_material)
        layout.addWidget(self.campo_material)
        layout.addWidget(label_quantidade)
        layout.addWidget(self.campo_quantidade)
        layout.addWidget(label_valor)
        layout.addWidget(self.campo_valor)
        layout.addWidget(label_descricao)
        layout.addWidget(self.campo_descricao)
        layout.addWidget(self.salvar)
        layout.addWidget(self.limpar)
        layout.addWidget(self.excluir)
        layout.addWidget(self.tabela)
        self.carregar_joias()
        self.setLayout(layout)

    def salvar_joia(self):
        nome = self.campo_nome.text()
        tipo = self.campo_tipo.text()
        material = self.campo_material.currentText()
        quantidade = self.campo_quantidade.text()
        valor = self.campo_valor.text()
        descricao = self.campo_descricao.text()
        
        if not nome or not tipo or not material or not quantidade or not valor:
            QMessageBox.warning(self, "Atenção", "Preencha todos os campos obrigatórios!")
            return
        
        try:
            valor_float = float(valor)
            quantidade_int = int(quantidade)
        except ValueError:
            QMessageBox.warning(self, "Atenção", "O campo Valor/Quantidade devem ser números!")
            return

        conn = get_connection()
        cursor = conn.cursor()
        if self.id_editando is None:
            cursor.execute("""
            INSERT INTO joias (nome, tipo, material, quantidade, valor, descricao)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (nome, tipo, material, quantidade_int, valor_float, descricao))
        else:
            cursor.execute("""
            UPDATE joias SET nome=?, tipo=?, material=?, quantidade=?, valor=?, descricao=?
            WHERE id=?
        """, (nome, tipo, material, quantidade_int, valor_float, descricao, self.id_editando))
        conn.commit()
        conn.close()
        self.limpar_campos()
        QMessageBox.information(self,"Cadastro realizado!", "Joia cadastrada com sucesso!")
        self.id_editando = None
        self.carregar_joias()

    def limpar_campos(self):
        self.campo_nome.clear()
        self.campo_tipo.clear()
        self.campo_material.setCurrentIndex(0)
        self.campo_quantidade.clear()
        self.campo_valor.clear()
        self.campo_descricao.clear()
        self.id_editando = None

    def carregar_joias(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, tipo, material, quantidade, valor FROM joias")
        joias = cursor.fetchall()
        self.tabela.setRowCount(len(joias))

        for i, joia in enumerate(joias):
            self.tabela.setItem(i, 0, QTableWidgetItem(str(joia["id"])))
            self.tabela.setItem(i, 1, QTableWidgetItem(joia["nome"]))
            self.tabela.setItem(i, 2, QTableWidgetItem(joia["tipo"]))
            self.tabela.setItem(i, 3, QTableWidgetItem(joia["material"]))
            self.tabela.setItem(i, 4, QTableWidgetItem(str(joia["quantidade"])))
            self.tabela.setItem(i, 5, QTableWidgetItem(str(joia["valor"])))

    def excluir_joia(self):
        linha = self.tabela.currentRow()
        id_joia = self.tabela.item(linha, 0).text()
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM joias WHERE id = ?", (id_joia,))
        QMessageBox.information(self, "Atenção", "Joia deletada com sucesso!")
        conn.commit()
        conn.close()
        self.carregar_joias()

    def selecionar_joia(self, linha, coluna):
        self.campo_nome.setText(self.tabela.item(linha, 1).text())
        self.campo_tipo.setText(self.tabela.item(linha, 2).text())
        self.campo_material.setCurrentText(self.tabela.item(linha, 3).text())
        self.campo_quantidade.setText(self.tabela.item(linha, 4).text())
        self.campo_valor.setText(self.tabela.item(linha, 5).text())
        self.id_editando = self.tabela.item(linha, 0).text()