import json
import os
import sys


def caminho_arquivo(nome):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, nome)
    return os.path.join(os.path.abspath("."), nome)

Arquivo = caminho_arquivo("favoritos.json")

def carregar():
    if not os.path.exists(Arquivo):
        return []
    
    with open(Arquivo, "r", encoding="utf-8") as f:
        return json.load(f)
    
def salvar(dados):
    with open(Arquivo, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

def adicionar(artista, musica, letra):
    dados = carregar()

    for item in dados:
        if (
            item["artista"].lower() == artista.lower()
            and item["musica"].lower() == musica.lower()
        ):
            return False

    dados.append({
        "artista": artista,
        "musica": musica,
        "letra": letra
    })

    salvar(dados)
    return True