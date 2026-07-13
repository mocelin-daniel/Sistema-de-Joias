# Importações dos widgets PyQt6 e bibliotecas necessárias
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QTableWidget, QTableWidgetItem, QComboBox, QHBoxLayout
from database.db import get_connection
import sqlite3
from PyQt6.QtWidgets import QHeaderView

class Cadastros(QWidget):
    def __init__(self):
        super().__init__()
        
        # layout principal divide a tela em dois lados (categorias | materiais)
        layout_principal = QHBoxLayout()

        # LADO ESQUERDO — CADASTRO DE CATEGORIAS
        layout_categorias = QVBoxLayout()
        layout_categorias.addWidget(QLabel("Categoria da Joia:"))
        self.campo_categoria = QLineEdit()
        layout_categorias.addWidget(self.campo_categoria)
        
        # botões de ação para categorias
        layout_btns_categoria = QHBoxLayout()
        self.salvar_c = QPushButton("Salvar")
        self.limpar_c = QPushButton("Limpar")
        self.excluir_c = QPushButton("Excluir")
        layout_btns_categoria.addWidget(self.salvar_c)
        layout_btns_categoria.addWidget(self.limpar_c)
        layout_btns_categoria.addWidget(self.excluir_c)
        layout_categorias.addLayout(layout_btns_categoria)
        
        # tabela de listagem das categorias cadastradas
        self.tabela_categorias = QTableWidget()
        self.tabela_categorias.setColumnCount(2)
        self.tabela_categorias.setHorizontalHeaderLabels(["ID", "Categoria"])
        self.tabela_categorias.setColumnHidden(0, True)  # oculta coluna ID
        layout_categorias.addWidget(self.tabela_categorias)
        self.tabela_categorias.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # LADO DIREITO — CADASTRO DE MATERIAIS
        layout_materiais = QVBoxLayout()
        layout_materiais.addWidget(QLabel("Material:"))
        self.campo_material = QLineEdit()
        layout_materiais.addWidget(self.campo_material)
        
        # botões de ação para materiais
        layout_btns_material = QHBoxLayout()
        self.salvar_m = QPushButton("Salvar")
        self.limpar_m = QPushButton("Limpar")
        self.excluir_m = QPushButton("Excluir")
        layout_btns_material.addWidget(self.salvar_m)
        layout_btns_material.addWidget(self.limpar_m)
        layout_btns_material.addWidget(self.excluir_m)
        layout_materiais.addLayout(layout_btns_material)
        
        # tabela de listagem dos materiais cadastrados
        self.tabela_materiais = QTableWidget()
        self.tabela_materiais.setColumnCount(2)
        self.tabela_materiais.setHorizontalHeaderLabels(["ID", "Material"])
        self.tabela_materiais.setColumnHidden(0, True)  # oculta coluna ID
        layout_materiais.addWidget(self.tabela_materiais)
        self.tabela_materiais.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # junta os dois lados no layout principal
        layout_principal.addLayout(layout_categorias)
        layout_principal.addLayout(layout_materiais)
        self.setLayout(layout_principal)

        # === CONEXÕES DOS SINAIS AOS MÉTODOS ===
        self.salvar_c.clicked.connect(self.salvar_categoria)
        self.limpar_c.clicked.connect(self.limpar_campo_c)
        self.tabela_categorias.cellClicked.connect(self.selecionar_categorias)
        self.excluir_c.clicked.connect(self.excluir_categoria)
        
        self.salvar_m.clicked.connect(self.salvar_material)
        self.limpar_m.clicked.connect(self.limpar_campo_m)
        self.tabela_materiais.cellClicked.connect(self.selecionar_material)
        self.excluir_m.clicked.connect(self.excluir_material)
        
        # carrega os dados do banco ao iniciar a tela
        self.carregar_categorias()
        self.carregar_materiais()

    def salvar_categoria(self):
        """Salva uma nova categoria no banco de dados"""
        categoria = self.campo_categoria.text().strip().title()

        if not categoria:
            QMessageBox.warning(self, "Atenção", "Preencha pelo menos um dos campos!")
            return
        
        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO tipos (tipo) VALUES (?)", (categoria,))
        except sqlite3.IntegrityError:
            # impede cadastro de categoria duplicada
            QMessageBox.warning(self, "Atenção", "Já existe uma categoria com esse nome!")
            conn.close()
            return
        conn.commit()
        conn.close()
        self.limpar_campo_c()
        self.atualizar()

    def limpar_campo_c(self):
        """Limpa o campo de categoria e desfaz a seleção da tabela"""
        self.campo_categoria.clear()
        self.tabela_categorias.setCurrentCell(-1, -1)  # desfaz seleção
        self.id_editando = None

    def carregar_categorias(self):
        """Busca todas as categorias do banco e preenche a tabela"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, tipo FROM tipos")
        categoria = cursor.fetchall()
        self.tabela_categorias.setRowCount(len(categoria))

        for i, categoria in enumerate(categoria):
            self.tabela_categorias.setItem(i, 0, QTableWidgetItem(str(categoria["id"])))
            self.tabela_categorias.setItem(i, 1, QTableWidgetItem(categoria["tipo"]))

    def salvar_material(self):
        """Salva um novo material no banco de dados"""
        material = self.campo_material.text().strip().title()

        if not material:
            QMessageBox.warning(self, "Atenção", "Preencha pelo menos um dos campos!")
            return
        
        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO material (material) VALUES (?)", (material,))
        except sqlite3.IntegrityError:
            # impede cadastro de material duplicado
            QMessageBox.warning(self, "Atenção", "Já existe um material com esse nome!")
            conn.close()
            return
        conn.commit()
        conn.close()
        self.limpar_campo_m()
        self.atualizar()

    def limpar_campo_m(self):
        """Limpa o campo de material e desfaz a seleção da tabela"""
        self.campo_material.clear()
        self.tabela_materiais.setCurrentCell(-1, -1)  # desfaz seleção
        self.id_editando = None

    def carregar_materiais(self):
        """Busca todos os materiais do banco e preenche a tabela"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, material FROM material")
        materiais = cursor.fetchall()
        self.tabela_materiais.setRowCount(len(materiais))

        for i, material in enumerate(materiais):
            self.tabela_materiais.setItem(i, 0, QTableWidgetItem(str(material["id"])))
            self.tabela_materiais.setItem(i, 1, QTableWidgetItem(material["material"]))

    def selecionar_categorias(self, linha, coluna):
        """Preenche o campo com os dados da linha clicada na tabela de categorias"""
        self.campo_categoria.setText(self.tabela_categorias.item(linha, 1).text())
        self.id_editando = self.tabela_categorias.item(linha, 0).text()

    def selecionar_material(self, linha, coluna):
        """Preenche o campo com os dados da linha clicada na tabela de materiais"""
        self.campo_material.setText(self.tabela_materiais.item(linha, 1).text())
        self.id_editando = self.tabela_materiais.item(linha, 0).text()

    def excluir_categoria(self):
        """Exclui a categoria selecionada após validações e confirmação"""
        linha = self.tabela_categorias.currentRow()
        if linha == -1:
            QMessageBox.warning(self, "Atenção", "Selecione uma categoria para excluir!")
            return
        
        id_categoria = self.tabela_categorias.item(linha, 0).text()
        conn = get_connection()
        cursor = conn.cursor()
        
        # verifica se alguma joia usa essa categoria antes de excluir
        cursor.execute("SELECT COUNT(*) as total FROM joias WHERE tipo = ?", (self.tabela_categorias.item(linha, 1).text(),))
        resultado = cursor.fetchone()
        if resultado["total"] > 0:
            QMessageBox.warning(self, "Atenção", 
                f"Essa categoria possui {resultado['total']} venda(s) registrada(s) e não pode ser excluída!")
            conn.close()
            return
        
        # confirmação antes de excluir
        msg = QMessageBox()
        msg.setWindowTitle("Confirmar exclusão")
        msg.setText("Tem certeza que deseja excluir a categoria selecionada?")
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg.button(QMessageBox.StandardButton.Yes).setText("Sim")
        msg.button(QMessageBox.StandardButton.No).setText("Não")
        resposta = msg.exec()

        if resposta == QMessageBox.StandardButton.No:
            return

        cursor.execute("DELETE FROM tipos WHERE id = ?", (id_categoria,))
        QMessageBox.information(self, "Atenção", "Categoria deletada com sucesso!")
        conn.commit()
        conn.close()
        self.carregar_categorias()
        self.limpar_campo_c()

    def excluir_material(self):
        """Exclui o material selecionado após validações e confirmação"""
        linha = self.tabela_materiais.currentRow()
        if linha == -1:
            QMessageBox.warning(self, "Atenção", "Selecione um material para excluir!")
            return
        
        id_material = self.tabela_materiais.item(linha, 0).text()
        conn = get_connection()
        cursor = conn.cursor()
        
        # verifica se alguma joia usa esse material antes de excluir
        cursor.execute("SELECT COUNT(*) as total FROM joias WHERE material = ?", (self.tabela_materiais.item(linha, 1).text(),))
        resultado = cursor.fetchone()
        if resultado["total"] > 0:
            QMessageBox.warning(self, "Atenção", 
                f"Esse material possui {resultado['total']} venda(s) registrada(s) e não pode ser excluído!")
            conn.close()
            return
        
        # confirmação antes de excluir
        msg = QMessageBox()
        msg.setWindowTitle("Confirmar exclusão")
        msg.setText("Tem certeza que deseja excluir o material selecionado?")
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg.button(QMessageBox.StandardButton.Yes).setText("Sim")
        msg.button(QMessageBox.StandardButton.No).setText("Não")
        resposta = msg.exec()

        if resposta == QMessageBox.StandardButton.No:
            return

        cursor.execute("DELETE FROM material WHERE id = ?", (id_material,))
        QMessageBox.information(self, "Atenção", "Material deletado com sucesso!")
        conn.commit()
        conn.close()
        self.carregar_materiais()
        self.limpar_campo_m()

    def atualizar(self):
        """Recarrega as tabelas de categorias e materiais"""
        self.carregar_categorias()
        self.carregar_materiais()