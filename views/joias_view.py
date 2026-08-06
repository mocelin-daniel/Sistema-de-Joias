# Importações dos widgets PyQt6 e bibliotecas necessárias
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QTableWidget, QTableWidgetItem, QComboBox, QHBoxLayout
from database.db import get_connection
from PyQt6.QtWidgets import QHeaderView
from PyQt6.QtWidgets import QAbstractItemView

class Joias(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout_h = QHBoxLayout()  # layout horizontal para os botões
        layout.addWidget(QLabel("Cadastrar Joias"))

        # campos do formulário
        label_nome = QLabel("Código: ")
        self.campo_nome = QLineEdit()
        label_tipo = QLabel("Tipo: ")
        self.combo_tipo = QComboBox()  # populado dinamicamente do banco
        label_material = QLabel("Material: ")
        self.combo_material = QComboBox()  # populado dinamicamente do banco
        label_quantidade = QLabel("Quantidade: ")
        self.campo_quantidade = QLineEdit()
        label_valor = QLabel("Preço: R$")
        self.campo_valor = QLineEdit()
        label_descricao = QLabel("Descrição: ")
        self.campo_descricao = QLineEdit()

        # botões de ação
        self.salvar = QPushButton("Salvar")
        self.limpar = QPushButton("Limpar")
        self.excluir = QPushButton("Excluir")
        
        # tabela de listagem das joias cadastradas
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(6)
        self.tabela.setHorizontalHeaderLabels(["ID", "Código", "Tipo", "Material", "Quantidade", "Valor"])
        self.tabela.setColumnHidden(0, True)  # oculta coluna ID
        self.id_editando = None  # guarda o id da joia sendo editada (None = novo cadastro)
        
        # conexões dos sinais aos métodos
        self.tabela.cellClicked.connect(self.selecionar_joia)
        self.salvar.clicked.connect(self.salvar_joia)
        self.limpar.clicked.connect(self.limpar_campos)
        self.excluir.clicked.connect(self.excluir_joia)

        # adição dos widgets ao layout
        layout.addWidget(label_nome)
        layout.addWidget(self.campo_nome)
        layout.addWidget(label_tipo)
        layout.addWidget(self.combo_tipo)
        layout.addWidget(label_material)
        layout.addWidget(self.combo_material)
        layout.addWidget(label_quantidade)
        layout.addWidget(self.campo_quantidade)
        layout.addWidget(label_valor)
        layout.addWidget(self.campo_valor)
        layout.addWidget(label_descricao)
        layout.addWidget(self.campo_descricao)
        layout_h.addWidget(self.salvar)
        layout_h.addWidget(self.limpar)
        layout_h.addWidget(self.excluir)
        layout.addLayout(layout_h)
        layout.addWidget(self.tabela)
        self.tabela.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)  # impede edição direta na tabela
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)  # colunas preenchem a largura
        self.carregar_joias()
        self.setLayout(layout)

        # carrega tipos e materiais nos ComboBoxes
        self.carregar_tipo()
        self.carregar_material()

    def carregar_tipo(self):
        """Busca todas as categorias do banco e popula o ComboBox de tipo"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, tipo FROM tipos")
        tipos = cursor.fetchall()
        conn.close()
        for tipos in tipos:
            self.combo_tipo.addItem(tipos["tipo"], tipos["id"])

    def carregar_material(self):
        """Busca todos os materiais do banco e popula o ComboBox de material"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, material FROM material")
        material = cursor.fetchall()
        conn.close()
        for material in material:
            self.combo_material.addItem(material["material"], material["id"])

    def salvar_joia(self):
        """Salva ou atualiza uma joia no banco de dados"""
        nome = self.campo_nome.text().title()
        tipo = self.combo_tipo.currentText()
        material = self.combo_material.currentText()
        quantidade = self.campo_quantidade.text()
        valor = self.campo_valor.text().replace(",", ".")  # aceita vírgula como separador decimal
        descricao = self.campo_descricao.text()
        
        # valida campos obrigatórios
        if not nome or not tipo or not material or not quantidade or not valor:
            QMessageBox.warning(self, "Atenção", "Preencha todos os campos obrigatórios!")
            return
        
        # valida se quantidade e valor são números válidos
        try:
            valor_float = float(valor)
            quantidade_int = int(quantidade)
        except ValueError:
            QMessageBox.warning(self, "Atenção", "O campo Valor/Quantidade devem ser números!")
            return

        conn = get_connection()
        cursor = conn.cursor()

        if self.id_editando is None:
            # verifica nome duplicado apenas no cadastro novo
            cursor.execute("SELECT id FROM joias WHERE nome = ?", (nome,))
            if cursor.fetchone():
                msg = QMessageBox()
                msg.setWindowTitle("Atenção")
                msg.setText("Já existe uma joia com esse nome. Deseja cadastrar mesmo assim?")
                msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                msg.button(QMessageBox.StandardButton.Yes).setText("Sim")
                msg.button(QMessageBox.StandardButton.No).setText("Não")
                resposta = msg.exec()

                if resposta == QMessageBox.StandardButton.No:
                    conn.close()
                    return

            # novo cadastro
            cursor.execute("""
                INSERT INTO joias (nome, tipo, material, quantidade, valor, descricao)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (nome, tipo, material, quantidade_int, valor_float, descricao))
        else:
            # atualiza cadastro existente
            cursor.execute("""
                UPDATE joias SET nome=?, tipo=?, material=?, quantidade=?, valor=?, descricao=?
                WHERE id=?
            """, (nome, tipo, material, quantidade_int, valor_float, descricao, self.id_editando))

        conn.commit()
        conn.close()
        self.limpar_campos()
        QMessageBox.information(self, "Cadastro realizado!", "Joia cadastrada com sucesso!")
        self.id_editando = None
        self.carregar_joias()

    def limpar_campos(self):
        """Limpa os campos do formulário e desfaz a seleção da tabela"""
        self.campo_nome.clear()
        self.combo_tipo.setCurrentIndex(0)
        self.combo_material.setCurrentIndex(0)
        self.campo_quantidade.clear()
        self.campo_valor.clear()
        self.campo_descricao.clear()
        self.id_editando = None
        self.tabela.setCurrentCell(-1, -1)  # desfaz seleção da tabela
        
    def carregar_joias(self):
        """Busca todas as joias do banco e preenche a tabela"""
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
            self.tabela.setItem(i, 5, QTableWidgetItem(f"R$ {joia['valor']:.2f}"))  # formata valor em reais

    def excluir_joia(self):
        """Exclui a joia selecionada após validações e confirmação"""
        linha = self.tabela.currentRow()
        if linha == -1:
            QMessageBox.warning(self, "Atenção", "Selecione uma joia para excluir!")
            return
        
        id_joia = self.tabela.item(linha, 0).text()
        conn = get_connection()
        cursor = conn.cursor()
        
        # bloqueia exclusão se a joia tiver vendas registradas
        cursor.execute("SELECT COUNT(*) as total FROM vendas WHERE joia_id = ?", (id_joia,))
        resultado = cursor.fetchone()
        if resultado["total"] > 0:
            QMessageBox.warning(self, "Atenção", 
                f"Essa joia possui {resultado['total']} venda(s) registrada(s) e não pode ser excluída!")
            conn.close()
            return
        
        # confirmação antes de excluir
        msg = QMessageBox()
        msg.setWindowTitle("Confirmar exclusão")
        msg.setText("Tem certeza que deseja excluir a joia selecionada?")
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg.button(QMessageBox.StandardButton.Yes).setText("Sim")
        msg.button(QMessageBox.StandardButton.No).setText("Não")
        resposta = msg.exec()

        if resposta == QMessageBox.StandardButton.No:
            return

        cursor.execute("DELETE FROM joias WHERE id = ?", (id_joia,))
        QMessageBox.information(self, "Atenção", "Joia deletada com sucesso!")
        conn.commit()
        conn.close()
        self.carregar_joias()
        self.limpar_campos()
        self.id_editando = None

    def selecionar_joia(self, linha, coluna):
        """Preenche o formulário com os dados da linha clicada na tabela"""
        self.campo_nome.setText(self.tabela.item(linha, 1).text())
        self.combo_tipo.setCurrentText(self.tabela.item(linha, 2).text())
        self.combo_material.setCurrentText(self.tabela.item(linha, 3).text())
        self.campo_quantidade.setText(self.tabela.item(linha, 4).text())
        valor = self.tabela.item(linha, 5).text().replace("R$ ", "")  # remove formatação antes de editar
        self.campo_valor.setText(valor)
        self.id_editando = self.tabela.item(linha, 0).text()
    
    def atualizar(self):
        """Recarrega os ComboBoxes e a tabela de joias"""
        self.combo_tipo.clear()
        self.combo_material.clear()
        self.carregar_tipo()
        self.carregar_material()
        self.carregar_joias()