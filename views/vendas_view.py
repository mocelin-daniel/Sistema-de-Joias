# Importações dos widgets PyQt6 necessários para a tela de vendas
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton, QMessageBox
from database.db import get_connection
import qrcode
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
import io
from PyQt6.QtWidgets import QHeaderView

# ===== FUNÇÕES PARA GERAÇÃO DO QR CODE PIX =====

def crc16(payload):
    """Calcula o CRC16 do payload Pix — necessário para validar o QR Code"""
    polinomio = 0x1021
    resultado = 0xFFFF
    for byte in payload.encode('utf-8'):
        resultado ^= byte << 8
        for _ in range(8):
            if resultado & 0x8000:
                resultado = (resultado << 1) ^ polinomio
            else:
                resultado <<= 1
        resultado &= 0xFFFF
    return resultado

def gerar_payload_pix(chave, nome, cidade, valor):
    """Gera o payload no formato Pix Copia e Cola do Banco Central"""
    valor_str = f"{float(valor):.2f}"
    
    # monta o bloco de identificação da chave pix
    merchant_account = f"0014br.gov.bcb.pix01{len(chave):02d}{chave}"
    merchant_account = f"26{len(merchant_account):02d}{merchant_account}"
    
    # limita nome e cidade ao tamanho máximo permitido pelo padrão Pix
    nome = nome[:25]
    cidade = cidade[:15]
    
    # monta o payload seguindo o padrão EMV do Banco Central
    payload = (
        f"000201"           # versão do payload
        f"010212"           # ponto de iniciação
        f"{merchant_account}"
        f"52040000"         # código de categoria
        f"5303986"          # código da moeda (986 = BRL)
        f"54{len(valor_str):02d}{valor_str}"  # valor da transação
        f"5802BR"           # código do país
        f"59{len(nome):02d}{nome}"            # nome do recebedor
        f"60{len(cidade):02d}{cidade}"        # cidade do recebedor
        f"6207050300062"    # campo adicional obrigatório
        f"6304"             # prefixo do CRC
    )
    
    # calcula e adiciona o CRC16 ao final
    crc = crc16(payload)
    return payload + f"{crc:04X}"


class Vendas(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Registrar Vendas"))

        # === CAMPOS DA TELA ===
        label_cliente = QLabel("Cliente:")
        self.combo_cliente = QComboBox()  # lista de clientes do banco

        label_cpf = QLabel("CPF:")
        self.campo_cpf = QLineEdit()
        self.campo_cpf.setReadOnly(True)  # preenchido automaticamente

        label_numero = QLabel("Número:")
        self.campo_numero = QLineEdit()
        self.campo_numero.setReadOnly(True)  # preenchido automaticamente

        label_joia = QLabel("Produto:")
        self.combo_joia = QComboBox()  # lista de joias com estoque

        label_valor = QLabel("Valor:")
        self.campo_valor = QLineEdit()
        self.campo_valor.setReadOnly(True)  # preenchido automaticamente ao selecionar joia

        label_quantidade = QLabel("Quantidade: ")
        self.campo_quantidade = QLineEdit()

        label_desc = QLabel("Desconto: %")
        self.campo_desc = QLineEdit()

        label_total = QLabel("Total")
        self.campo_total = QLineEdit()
        self.campo_total.setReadOnly(True)  # calculado automaticamente

        label_pagamento = QLabel("Forma de Pagamento: ")
        self.combo_pagamento = QComboBox()
        self.combo_pagamento.addItems(["Débito", "Crédito", "Pix", "Dinheiro"])

        self.qpush_registrar_venda = QPushButton("Registrar Venda!")

        # === CONEXÕES DE SINAIS ===
        self.combo_cliente.currentIndexChanged.connect(self.preencher_cliente)
        self.combo_joia.currentIndexChanged.connect(self.preencher_joia)
        self.campo_quantidade.textChanged.connect(self.calcular_total)
        self.campo_desc.textChanged.connect(self.calcular_total)
        self.qpush_registrar_venda.clicked.connect(self.registrar_venda)

        # === ADIÇÃO DOS WIDGETS AO LAYOUT ===
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
        layout.addWidget(label_desc)
        layout.addWidget(self.campo_desc)
        layout.addWidget(label_total)
        layout.addWidget(self.campo_total)
        layout.addWidget(label_pagamento)
        layout.addWidget(self.combo_pagamento)
        layout.addWidget(self.qpush_registrar_venda)
        self.setLayout(layout)

        # carrega clientes e joias ao iniciar a tela
        self.carregar_clientes()
        self.carregar_joias()

    def carregar_clientes(self):
        """Busca todos os clientes do banco e popula o ComboBox"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome FROM clientes")
        clientes = cursor.fetchall()
        conn.close()
        for cliente in clientes:
            self.combo_cliente.addItem(cliente["nome"], cliente["id"])

    def carregar_joias(self):
        """Busca joias com estoque disponível e popula o ComboBox"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, valor, material FROM joias WHERE quantidade > 0")
        joias = cursor.fetchall()
        conn.close()
        for joia in joias:
            # exibe nome e material para diferenciar joias com mesmo nome
            self.combo_joia.addItem(f"{joia['nome']} - {joia['material']}", joia['id'])

    def preencher_cliente(self):
        """Preenche CPF e telefone automaticamente ao selecionar um cliente"""
        id_cliente = self.combo_cliente.currentData()
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
        """Preenche o valor automaticamente ao selecionar uma joia"""
        id_joia = self.combo_joia.currentData()
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
        """Calcula o total da venda aplicando desconto se houver"""
        try:
            valor = float(self.campo_valor.text())
            quantidade = int(self.campo_quantidade.text())
            desconto = float(self.campo_desc.text() or 0)
            subtotal = valor * quantidade
            total = subtotal - (subtotal * desconto / 100)
            self.campo_total.setText(f"{total:.2f}")
        except ValueError:
            self.campo_total.setText("")

    def registrar_venda(self):
        """Registra a venda no banco, atualiza o estoque e gera QR Code Pix se necessário"""
        id_cliente = self.combo_cliente.currentData()
        id_joia = self.combo_joia.currentData()
        valor_joias = self.campo_valor.text()
        quantidade = self.campo_quantidade.text()
        valor_total = self.campo_total.text()
        pagamento = self.combo_pagamento.currentText()

        # validação dos campos obrigatórios
        if not quantidade or not id_cliente or not id_joia:
            QMessageBox.warning(self, "Atenção", "Preencha todos os campos!")
            return

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT quantidade FROM joias WHERE id = ?", (id_joia,))
        joia = cursor.fetchone()

        # valida quantidade
        if int(quantidade) <= 0:
            QMessageBox.warning(self, "Atenção", "Quantidade deve ser maior que zero!")
            return

        # verifica estoque disponível
        if int(quantidade) > joia["quantidade"]:
            QMessageBox.warning(self, "Atenção", f"Estoque insuficiente! \nQuantidade disponível: {joia['quantidade']}")
            conn.close()
            return

        # insere a venda no banco
        cursor.execute("""
            INSERT INTO vendas (cliente_id, joia_id, valor_joia, quantidade, valor_total, pagamento)
            VALUES (?, ?, ?, ?, ?, ?)""",
            (id_cliente, id_joia, valor_joias, quantidade, valor_total, pagamento))

        # atualiza o estoque da joia
        cursor.execute("UPDATE joias SET quantidade = quantidade - ? WHERE id = ?", (quantidade, id_joia))
        conn.commit()
        conn.close()

        # se o pagamento for Pix, oferece geração do QR Code
        if pagamento == "Pix":
            conn_cfg = get_connection()
            cursor_cfg = conn_cfg.cursor()
            cursor_cfg.execute("SELECT chave_pix, nome, cidade FROM configs WHERE id = 1")
            config = cursor_cfg.fetchone()
            conn_cfg.close()

            if config:
                chave_pix = config["chave_pix"]
                nome_pix = config["nome"]
                cidade_pix = config["cidade"]
            else:
                QMessageBox.warning(self, "Atenção", "Configure a chave Pix nas Configurações!")
                return

            # pergunta se deseja gerar o QR Code
            msg_confirmacao = QMessageBox()
            msg_confirmacao.setWindowTitle("Pagamento via Pix")
            msg_confirmacao.setText(f"Total a pagar: R$ {valor_total}\n\nDeseja gerar o QR Code para pagamento?")
            msg_confirmacao.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            msg_confirmacao.button(QMessageBox.StandardButton.Yes).setText("Sim")
            msg_confirmacao.button(QMessageBox.StandardButton.No).setText("Não")
            resposta = msg_confirmacao.exec()

            if resposta == QMessageBox.StandardButton.Yes:
                msg = QMessageBox()
                msg.setWindowTitle("Pagamento via Pix")
                msg.setText(f"Total a pagar: R$ {valor_total}")

                # gera o payload e o QR Code
                payload = gerar_payload_pix(chave_pix, nome_pix, cidade_pix, valor_total)
                qr = qrcode.make(payload)

                # converte a imagem para QPixmap e exibe no QMessageBox
                buffer = io.BytesIO()
                qr.save(buffer, format="PNG")
                buffer.seek(0)
                pixmap = QPixmap()
                pixmap.loadFromData(buffer.read())
                label_qr = QLabel()
                label_qr.setPixmap(pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio))
                msg.layout().addWidget(label_qr, 1, 0, 1, msg.layout().columnCount())
                msg.exec()

        QMessageBox.information(self, "Atenção!", "Venda registrada com sucesso!")
        self.atualizar()
        self.campo_quantidade.clear()

    def atualizar(self):
        """Recarrega clientes, joias e limpa o campo de desconto"""
        self.combo_cliente.clear()
        self.combo_joia.clear()
        self.carregar_clientes()
        self.carregar_joias()
        self.campo_desc.clear()