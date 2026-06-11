import requests
import urllib.parse
import re
import os
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
GENIUS_TOKEN = os.environ.get("GENIUS_API_TOKEN")
if not GENIUS_TOKEN:
    raise ValueError("GENIUS_API_TOKEN environment variable not set")


# 🔥 normalizar
def normalizar(txt):
    return re.sub(r'\s+', ' ', txt.lower()).strip()


# 🔥 gerar variações
def gerar_buscas(artista, musica):
    base = f"{artista} {musica}".strip()

    return [
        base,
        base + " lyrics",
        base + " song",
        base + " official lyrics",
        base + " romaji lyrics",
    ]


# =========================
# 🎵 GENIUS
# =========================

def buscar_varios_genius(query, tipo="normal"):
    query = query.strip()

    if tipo == "trecho" and len(query.split()) >= 4:
        query += " lyrics"

    url = f"https://api.genius.com/search?q={urllib.parse.quote(query)}"

    headers = {
        "Authorization": f"Bearer {GENIUS_TOKEN}"
    }

    try:
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            return []

        data = response.json()
        hits = data.get("response", {}).get("hits", [])

        resultados = []

        query_norm = normalizar(query)
        palavras = query_norm.split()

        for idx, hit in enumerate(hits):
            result = hit.get("result", {})

            titulo = result.get("title", "")
            artista = result.get("primary_artist", {}).get("name", "")
            link = result.get("url", "")
            imagem = result.get("song_art_image_url", "")

            titulo_norm = normalizar(titulo)
            artista_norm = normalizar(artista)

            score = 0

            score += sum(1 for p in palavras if p in titulo_norm)
            score += sum(1 for p in palavras if p in artista_norm)

            if score > 0:
                resultados.append({
                    "titulo": titulo,
                    "artista": artista,
                    "url": link,
                    "imagem": imagem,
                    "score": score,
                    "fonte": "Genius"
                })

        resultados.sort(key=lambda x: x["score"], reverse=True)

        for r in resultados:
            del r["score"]

        return resultados[:8]

    except Exception:
        return []


def pegar_letra_genius(url):
    try:
        html = requests.get(url).text
        soup = BeautifulSoup(html, "html.parser")

        divs = soup.find_all("div", {"data-lyrics-container": "true"})

        if not divs:
            return None

        letra = ""

        for d in divs:
            texto = d.get_text(separator="\n")
            letra += texto + "\n\n"

        return letra.strip()

    except Exception as e:
        print("ERRO:", e)
        return None


def buscar_lrclib(artista, musica):
    return [{
        "titulo": musica,
        "artista": artista,
        "url": f"{artista}|{musica}",
        "imagem": None,
        "fonte": "LRCLIB"
    }]

def pegar_letra_lrclib(artista, musica):
    try:
        url = (
            "https://lrclib.net/api/get"
            f"?artist_name={urllib.parse.quote(artista)}"
            f"&track_name={urllib.parse.quote(musica)}"
        )

        headers = {
            "User-Agent": "LyricsApp/1.0"
        }

        r = requests.get(
            url,
            headers=headers,
            timeout=10
        )

        if r.status_code != 200:
            return None

        data = r.json()

        return (
            data.get("plainLyrics")
            or data.get("syncedLyrics")
        )

    except Exception as e:
        print("ERRO:", e)
        return None
    
    
    



# =========================
# 🔥 MULTI-FONTE (LISTA)
# =========================

def buscar_todas_fontes(artista, musica, tipo="completo"):
    resultados = []

    # Genius
    try:
        resultados.extend(buscar_varios_genius(f"{artista} {musica}", tipo))
    except Exception:
        pass

    # LRCLIB
    try:
        resultados.extend(buscar_lrclib(artista, musica))
    except Exception:
        pass

    return resultados


# =========================
# 🔥 PEGAR LETRA POR FONTE
# =========================

def pegar_letra_por_fonte(url, fonte):
    if fonte == "Genius":
        return pegar_letra_genius(url)
    
    elif fonte == "LRCLIB":
        try:
            artista, musica = url.split("|")
            return pegar_letra_lrclib(artista, musica)
        except ValueError:
            return None
    
    elif fonte == "Manual":
        return url
    
    return None

