import sys
import os

def resource_path(arquivo):
    """Retorna o caminho correto tanto em desenvolvimento quanto no executável"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, arquivo)
    return os.path.join(os.path.abspath("."), arquivo)