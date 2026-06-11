import tkinter as tk
from tkinter import messagebox
from api import buscar_todas_fontes, pegar_letra_por_fonte
from database import adicionar, carregar
from deep_translator import GoogleTranslator # type: ignore
from PIL import Image, ImageTk
import requests
from io import BytesIO


# 🎨 CORES
BG = "#121212"
FG = "#FFFFFF"
ENTRY_BG = "#1E1E1E"
BTN_BG = "#1DB954"
BTN_FG = "#000000"

def buscar():
    artista = entry_artista.get().strip()
    musica = entry_musica.get().strip()

    if not artista and not musica:
        messagebox.showwarning("Erro", "Digite algo!")
        return

    # 🎯 detectar tipo
    if artista and musica:
        tipo = "completo"
        query = f"{artista} {musica}"

    elif musica:
        if len(musica.split()) >= 4:
            tipo = "trecho"
        else:
            tipo = "musica"
        query = musica

    else:
        tipo = "artista"
        query = artista

    resultados = buscar_todas_fontes(artista, musica, tipo)

    if not resultados:
        messagebox.showerror("Erro", "Nada encontrado")
        return

    escolher_resultado(resultados)

def escolher_resultado(resultados):
    janela = tk.Toplevel(root)
    janela.title("Escolha a música")
    janela.geometry("900x700")
    janela.configure(bg=BG)

    selecionado = {"index": None}

    # 🔥 separar por fontec
    genius_results = [(i, r) for i, r in enumerate(resultados) if r.get("fonte") == "Genius"]
    lyrics_results = [(i, r) for i, r in enumerate(resultados) if r.get("fonte") == "LRCLIB"]

    # 📦 container principal
    container = tk.Frame(janela, bg=BG)
    container.pack(fill="both", expand=True)

    frame_genius = tk.Frame(container, bg=BG)
    frame_genius.pack(side="left", fill="both", expand=True, padx=5)

    frame_letras = tk.Frame(container, bg=BG)
    frame_letras.pack(side="right", fill="both", expand=True, padx=5)

    # títulos
    tk.Label(frame_genius, text="🎵 Genius", bg=BG, fg=FG, font=("Arial", 12, "bold")).pack()
    tk.Label(frame_letras, text="🌐 LRCLIB", bg=BG, fg=FG, font=("Arial", 12, "bold")).pack()

    # 🎯 função de seleção
    def selecionar(idx, card):
        selecionado["index"] = idx

        for f in [frame_genius, frame_letras]:
            for c in f.winfo_children():
                c.config(bg="#1E1E1E")

        card.config(bg="#1DB954")

    # 🃏 criar cards
    def criar_lista(frame, lista_com_indices):
        for idx, r in lista_com_indices:
             card = tk.Frame(frame, bg="#1E1E1E", padx=10, pady=8, cursor="hand2")
             card.pack(fill="x", padx=5, pady=5)

             lbl_artista = tk.Label(
                    card,
                    text=r["artista"],
                    bg="#1E1E1E",
                    fg="#B3B3B3",
                    font=("Arial", 9)
             )
             lbl_artista.pack(anchor="w")

             lbl_titulo = tk.Label(
                    card,
                    text="🎶 " + r["titulo"],
                    bg="#1E1E1E",
                    fg="#FFFFFF",
                    font=("Arial", 10, "bold")
             )
             lbl_titulo.pack(anchor="w")

             for widget in (card, lbl_artista, lbl_titulo):
                widget.bind("<Button-1>", lambda e, i=idx, c=card: selecionar(i, c))

    # 🔥 criar colunas
    criar_lista(frame_genius, genius_results)
    criar_lista(frame_letras, lyrics_results)



    # ✅ confirmar
    def confirmar():
        idx = selecionado["index"]

        if idx is None:
            messagebox.showwarning("Erro", "Selecione uma música")
            return

        fonte = resultados[idx].get("fonte")
        url = resultados[idx]["url"]
        janela.destroy()

        letra = pegar_letra_por_fonte(url, fonte)

        if not letra:
            messagebox.showerror("Erro", "Não foi possível obter a letra")
            return


        versos = letra.split("\n")

        text_resultado.delete(1.0, tk.END)

        for v in versos:
            v = v.strip()
            if v:  # evita linhas vazias excessivas
                text_resultado.insert(tk.END, v + "\n")  
            else:     
                text_resultado.insert(tk.END, "\n")

    tk.Button(
        janela,
        text="Confirmar",
        command=confirmar,
        bg=BTN_BG,
        fg=BTN_FG,
        relief="flat",
        padx=10,
        pady=5
    ).pack(pady=10)

def traduzir():
    texto = text_resultado.get(1.0, tk.END)

    try:
        traducao = GoogleTranslator(source="auto", target="pt").translate(texto)

        text_resultado.delete(1.0, tk.END)
        text_resultado.insert(tk.END, traducao)
    except:
        messagebox.showerror("Erro", "Falha na tradução")

def abrir_editor_manual():
    janela = tk.Toplevel(root)
    janela.title("Adicionar Letra")
    janela.geometry("700x500")
    janela.configure(bg=BG)

    tk.Label(
        janela,
        text="Cole ou digite a letra abaixo:",
        bg=BG,
        fg=FG
    ).pack(pady=10)

    texto = tk.Text(
        janela,
        wrap="word",
        bg="#181818",
        fg=FG
    )

    texto.pack(
        expand=True,
        fill="both",
        padx=10,
        pady=10
    )

    def usar_letra():

        letra = texto.get(
            1.0,
            tk.END
        ).strip()

        if not letra:
            messagebox.showwarning(
                "Erro",
                "Digite uma letra"
            )
            return

        text_resultado.delete(
            1.0,
            tk.END
        )

        text_resultado.insert(
            tk.END,
            letra
        )

        janela.destroy()

    tk.Button(
        janela,
        text="Usar Letra",
        command=usar_letra,
        bg=BTN_BG,
        fg=BTN_FG
    ).pack(pady=10)

def salvar_favorito():
    artista = entry_artista.get()
    musica = entry_musica.get()
    letra = text_resultado.get(1.0, tk.END)

    if not letra.strip():
        messagebox.showwarning("Erro", "Nada para salvar")
        return

    if adicionar(artista, musica, letra):
        messagebox.showinfo("Sucesso", "Salvo nos favoritos!")
    else:
        messagebox.showinfo(
            "Favoritos",
            "Essa música já está salva."
        )

def mostrar_favoritos():
    favoritos = carregar()

    if not favoritos:
        messagebox.showinfo("Favoritos", "Nenhum favorito salvo")
        return
    
    janela = tk.Toplevel(root)
    janela.title("⭐ Favoritos")
    janela.geometry("700x500")
    janela.configure(bg=BG)

    lista = tk.Listbox(
        janela,
        bg="#181818",
        fg="white",
        selectbackground="#1DB954",
        font=("Arial", 10)
    )
    lista.pack(fill="both", expand=True, padx=10, pady=10)

    for fav in favoritos:
        lista.insert(
            tk.END,
            f"{fav['artista']} - {fav['musica']}"
        )

    def abrir():
        selecionado = lista.curselection()

        if not selecionado:
            messagebox.showwarning(
                "Favoritos",
                "Selecione uma música"
            )
            return
        
        indice = selecionado[0]
        favorito = favoritos[indice]

        entry_artista.delete(0, tk.END)
        entry_artista.insert(0, favorito["artista"])

        entry_musica.delete(0, tk.END)
        entry_musica.insert(0, favorito["musica"])

        text_resultado.delete(1.0, tk.END)
        text_resultado.insert(tk.END, favorito["letra"])

        janela.destroy()

    tk.Button(
        janela,
        text="Abrir",
        command=abrir,
        bg=BTN_BG,
        fg=BTN_FG
    ).pack(pady=10)


# 🖥️ JANELA
root = tk.Tk()
root.title("🎧 Lyrics App")
root.geometry("600x700")
root.configure(bg=BG)

# 🔝 TÍTULO
titulo = tk.Label(
    root,
    text="🎧 Lyrics App",
    font=("Arial", 18, "bold"),
    bg=BG,
    fg=FG
)
titulo.pack(pady=10)

# 📦 FRAME INPUT
frame_inputs = tk.Frame(root, bg=BG)
frame_inputs.pack(pady=10)

# ARTISTA
tk.Label(frame_inputs, text="Artista", bg=BG, fg=FG).grid(row=0, column=0, sticky="w")
entry_artista = tk.Entry(frame_inputs, bg=ENTRY_BG, fg=FG, width=30)
entry_artista.grid(row=1, column=0, padx=5, pady=5)

# MÚSICA
tk.Label(frame_inputs, text="Música", bg=BG, fg=FG).grid(row=0, column=1, sticky="w")
entry_musica = tk.Entry(frame_inputs, bg=ENTRY_BG, fg=FG, width=30)
entry_musica.grid(row=1, column=1, padx=5, pady=5)

# 📦 FRAME BOTÕES
frame_botoes = tk.Frame(root, bg=BG)
frame_botoes.pack(pady=10)

def criar_botao(texto, comando):
    return tk.Button(
        frame_botoes,
        text=texto,
        command=comando,
        bg=BTN_BG,
        fg=BTN_FG,
        relief="flat",
        padx=10,
        pady=5
    )

criar_botao("Buscar", buscar).grid(row=0, column=0, padx=5)
criar_botao("Traduzir", traduzir).grid(row=0, column=1, padx=5)
criar_botao("Favoritar ⭐", salvar_favorito).grid(row=0, column=2, padx=5)
criar_botao("⭐ Favoritos", mostrar_favoritos).grid(row=0, column=3, padx=5)
criar_botao("➕ Letra manual", abrir_editor_manual).grid(row=0, column=4, padx=5)

# 📦 RESULTADO
frame_resultado = tk.Frame(root, bg=BG)
frame_resultado.pack(expand=True, fill="both", padx=10, pady=10)

text_resultado = tk.Text(
    frame_resultado,
    wrap="word",
    bg="#181818",
    fg=FG,
    insertbackground=FG
)
text_resultado.pack(expand=True, fill="both")

# SCROLL
scroll = tk.Scrollbar(text_resultado)
scroll.pack(side="right", fill="y")
text_resultado.config(yscrollcommand=scroll.set)
scroll.config(command=text_resultado.yview)

root.mainloop()