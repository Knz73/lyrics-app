import tkinter as tk
from tkinter import messagebox
from api import buscar_todas_fontes, pegar_letra_por_fonte
from database import adicionar, carregar, remover, atualizar, adicionar_manual, carregar_manuais, remover_manual, buscar_manuais
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
    
    manuais = buscar_manuais(artista if artista else "", musica if musica else "")
    resultados.extend(manuais)

    if not resultados:
        resposta = messagebox.askyesno(
            "Nenhum resultado",
            "Nenhuma letra encontrada.\nDeseja adicionar manualmente?"
        )
        if resposta:
            mostrar_manuais()
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
    manual_results = [(i, r) for i, r in enumerate(resultados) if r.get("fonte") == "Manual"]

    # 📦 container principal
    container = tk.Frame(janela, bg=BG)
    container.pack(fill="both", expand=True)

    frame_genius = tk.Frame(container, bg=BG)
    frame_genius.pack(side="left", fill="both", expand=True, padx=5)

    frame_letras = tk.Frame(container, bg=BG)
    frame_letras.pack(side="left", fill="both", expand=True, padx=5)

    frame_manuais = tk.Frame(container, bg=BG)
    frame_manuais.pack(side="left", fill="both", expand=True, padx=5)

    # títulos
    tk.Label(frame_genius, text="🎵 Genius", bg=BG, fg=FG, font=("Arial", 12, "bold")).pack()
    tk.Label(frame_letras, text="🌐 LRCLIB", bg=BG, fg=FG, font=("Arial", 12, "bold")).pack()
    tk.Label(frame_manuais, text="✨ Salvos", bg=BG, fg=FG, font=("Arial", 12, "bold")).pack()

    # 🎯 função de seleção
    def selecionar(idx, card):
        selecionado["index"] = idx

        for f in [frame_genius, frame_letras, frame_manuais]:
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
    criar_lista(frame_manuais, manual_results)



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

    tk.Button(
        janela,
        text="➕ Adicionar manualmente",
        command=lambda: [janela.destroy(), abrir_adicionar_manual()],
        bg="#555555",
        fg=FG,
        relief="flat",
        padx=10,
        pady=5
    ).pack(pady=5)

def traduzir():
    texto = text_resultado.get(1.0, tk.END)

    try:
        traducao = GoogleTranslator(source="auto", target="pt").translate(texto)

        text_resultado.delete(1.0, tk.END)
        text_resultado.insert(tk.END, traducao)
    except:
        messagebox.showerror("Erro", "Falha na tradução")

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

def abrir_adicionar_manual():
    editor = tk.Toplevel(root)
    editor.title("Adicionar Manual")
    editor.geometry("600x500")
    editor.configure(bg=BG)

    tk.Label(editor, text="Artista:", bg=BG, fg=FG).pack(pady=2, anchor="w", padx=10)
    entry_edit_artista = tk.Entry(editor, bg=ENTRY_BG, fg=FG)
    entry_edit_artista.insert(0, entry_artista.get())
    entry_edit_artista.pack(pady=2, padx=10, fill="x")

    tk.Label(editor, text="Música:", bg=BG, fg=FG).pack(pady=2, anchor="w", padx=10)
    entry_edit_musica = tk.Entry(editor, bg=ENTRY_BG, fg=FG)
    entry_edit_musica.insert(0, entry_musica.get())
    entry_edit_musica.pack(pady=2, padx=10, fill="x")

    tk.Label(editor, text="Letra:", bg=BG, fg=FG).pack(pady=2, anchor="w", padx=10)
    texto_edit = tk.Text(editor, wrap="word", bg="#181818", fg=FG, height=15)
    texto_edit.pack(pady=2, padx=10, fill="both", expand=True)

    def salvar():
        artista = entry_edit_artista.get().strip()
        musica = entry_edit_musica.get().strip()
        letra = texto_edit.get(1.0, tk.END).strip()

        if not artista or not musica or not letra:
            messagebox.showwarning("Erro", "Preencha todos os campos")
            return

        adicionar_manual(artista, musica, letra)
        messagebox.showinfo("Sucesso", "Música manual adicionada!")
        editor.destroy()
        mostrar_manuais()

    tk.Button(
        editor,
        text="Salvar",
        command=salvar,
        bg=BTN_BG,
        fg=BTN_FG,
        relief="flat",
        padx=20,
        pady=5
    ).pack(pady=10)

def mostrar_manuais():
    manuais = carregar_manuais()

    janela = tk.Toplevel(root)
    janela.title("✨ Salvos")
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

    for idx, manual in enumerate(manuais):
        lista.insert(
            tk.END,
            f"{manual['artista']} - {manual['musica']}"
        )

    if not manuais:
        messagebox.showinfo("Salvos", "Nenhuma música salva")
        return

    def abrir():
        selecionado = lista.curselection()

        if not selecionado:
            messagebox.showwarning(
                "Salvos",
                "Selecione uma música"
            )
            return
        
        indice = selecionado[0]
        manual = manuais[indice]

        entry_artista.delete(0, tk.END)
        entry_artista.insert(0, manual["artista"])

        entry_musica.delete(0, tk.END)
        entry_musica.insert(0, manual["musica"])

        text_resultado.delete(1.0, tk.END)
        text_resultado.insert(tk.END, manual["letra"])

        janela.destroy()

    def remover():
        selecionado = lista.curselection()

        if not selecionado:
            messagebox.showwarning(
                "Salvos",
                "Selecione uma música"
            )
            return

        indice = selecionado[0]
        manual = manuais[indice]

        resposta = messagebox.askyesno(
            "Confirmar",
            f"Remover '{manual['artista']} - {manual['musica']}' dos salvos?"
        )

        if resposta:
            remover_manual(indice)
            messagebox.showinfo("Sucesso", "Removido!")
            janela.destroy()
            mostrar_manuais()

    tk.Button(
        janela,
        text="Abrir",
        command=abrir,
        bg=BTN_BG,
        fg=BTN_FG
    ).pack(pady=10, side="left", padx=5)

    tk.Button(
        janela,
        text="➕ Adicionar",
        command=lambda: [janela.destroy(), abrir_adicionar_manual()],
        bg="#1DB954",
        fg=BTN_FG,
        relief="flat",
        padx=10,
        pady=5
    ).pack(pady=10, side="left", padx=5)

    tk.Button(
        janela,
        text="Remover",
        command=remover,
        bg="#E63946",
        fg=FG,
        relief="flat",
        padx=10,
        pady=5
    ).pack(pady=10, side="left", padx=5)

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

    def editar():
        selecionado = lista.curselection()

        if not selecionado:
            messagebox.showwarning(
                "Favoritos",
                "Selecione uma música"
            )
            return

        indice = selecionado[0]
        favorito = favoritos[indice]

        editor = tk.Toplevel(janela)
        editor.title("Editar Favorito")
        editor.geometry("500x350")
        editor.configure(bg=BG)

        tk.Label(editor, text="Artista:", bg=BG, fg=FG).pack(pady=2, anchor="w", padx=10)
        entry_edit_artista = tk.Entry(editor, bg=ENTRY_BG, fg=FG)
        entry_edit_artista.insert(0, favorito["artista"])
        entry_edit_artista.pack(pady=2, padx=10, fill="x")

        tk.Label(editor, text="Música:", bg=BG, fg=FG).pack(pady=2, anchor="w", padx=10)
        entry_edit_musica = tk.Entry(editor, bg=ENTRY_BG, fg=FG)
        entry_edit_musica.insert(0, favorito["musica"])
        entry_edit_musica.pack(pady=2, padx=10, fill="x")

        tk.Label(editor, text="Letra:", bg=BG, fg=FG).pack(pady=2, anchor="w", padx=10)
        texto_edit = tk.Text(editor, wrap="word", bg="#181818", fg=FG, height=6)
        texto_edit.insert(tk.END, favorito["letra"])
        texto_edit.pack(pady=2, padx=10, fill="both", expand=True)

        def salvar_edicao():
            novo_artista = entry_edit_artista.get().strip()
            nova_musica = entry_edit_musica.get().strip()
            nova_letra = texto_edit.get(1.0, tk.END).strip()

            if not novo_artista or not nova_musica:
                messagebox.showwarning("Erro", "Preencha artista e música")
                return

            if atualizar(indice, novo_artista, nova_musica, nova_letra):
                messagebox.showinfo("Sucesso", "Favorito atualizado!")
                janela.destroy()
                mostrar_favoritos()
            else:
                messagebox.showerror("Erro", "Não foi possível atualizar")

        tk.Button(
            editor,
            text="Salvar",
            command=salvar_edicao,
            bg=BTN_BG,
            fg=BTN_FG,
            relief="flat",
            padx=20,
            pady=5
        ).pack(pady=8)

    def remover_fav():
        selecionado = lista.curselection()

        if not selecionado:
            messagebox.showwarning(
                "Favoritos",
                "Selecione uma música"
            )
            return

        indice = selecionado[0]
        favorito = favoritos[indice]

        resposta = messagebox.askyesno(
            "Confirmar",
            f"Remover '{favorito['artista']} - {favorito['musica']}' dos favoritos?"
        )

        if resposta:
            remover(indice)
            messagebox.showinfo("Sucesso", "Removido!")
            janela.destroy()
            mostrar_favoritos()

    tk.Button(
        janela,
        text="Abrir",
        command=abrir,
        bg=BTN_BG,
        fg=BTN_FG
    ).pack(pady=10, side="left", padx=5)

    tk.Button(
        janela,
        text="Editar",
        command=editar,
        bg="#555555",
        fg=FG,
        relief="flat",
        padx=10,
        pady=5
    ).pack(pady=10, side="left", padx=5)

    tk.Button(
        janela,
        text="Remover",
        command=remover_fav,
        bg="#E63946",
        fg=FG,
        relief="flat",
        padx=10,
        pady=5
    ).pack(pady=10, side="left", padx=5)


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
criar_botao("✨ Salvos", mostrar_manuais).grid(row=0, column=4, padx=5)

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