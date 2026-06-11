import json
import os
import sys


def caminho_arquivo(nome):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, nome)
    return os.path.join(os.path.abspath("."), nome)

Arquivo = caminho_arquivo("favoritos.json")
ArquivoManuais = caminho_arquivo("manuais.json")

def carregar():
    if not os.path.exists(Arquivo):
        return []
    
    with open(Arquivo, "r", encoding="utf-8") as f:
        return json.load(f)
    
def salvar(dados):
    with open(Arquivo, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

def remover(indice):
    dados = carregar()
    if 0 <= indice < len(dados):
        del dados[indice]
        salvar(dados)
        return True
    return False

def atualizar(indice, artista, musica, letra):
    dados = carregar()
    if 0 <= indice < len(dados):
        dados[indice]["artista"] = artista
        dados[indice]["musica"] = musica
        dados[indice]["letra"] = letra
        salvar(dados)
        return True
    return False

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

def carregar_manuais():
    if not os.path.exists(ArquivoManuais):
        return []
    
    with open(ArquivoManuais, "r", encoding="utf-8") as f:
        return json.load(f)
    
def salvar_manuais(dados):
    with open(ArquivoManuais, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

def adicionar_manual(artista, musica, letra):
    dados = carregar_manuais()

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

    salvar_manuais(dados)
    return True

def remover_manual(indice):
    dados = carregar_manuais()
    if 0 <= indice < len(dados):
        del dados[indice]
        salvar_manuais(dados)
        return True
    return False

def buscar_manuais(artista, musica):
    manuais = carregar_manuais()
    resultados = []
    
    artista_lower = artista.lower()
    musica_lower = musica.lower()
    
    for m in manuais:
        if (artista_lower in m["artista"].lower() and musica_lower in m["musica"].lower()):
            resultados.append({
                "titulo": m["musica"],
                "artista": m["artista"],
                "url": m["letra"],
                "imagem": None,
                "fonte": "Manual"
            })
    
    return resultados