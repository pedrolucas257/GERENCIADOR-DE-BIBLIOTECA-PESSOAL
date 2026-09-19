import mysql.connector
from datetime import date
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from dotenv import load_dotenv
import os

load_dotenv()

db_host = os.getenv("DB_HOST")
db_user = os.getenv("DB_USER")
db_senha = os.getenv("DB_SENHA")
db_nome = os.getenv("DB_NOME")

conexao = mysql.connector.connect(
    host=db_host,
    user=db_user,
    password=db_senha,
    database=db_nome
)
cursor = conexao.cursor()
# Consultar registros
cursor.execute("SELECT * FROM livros")
for linha in cursor.fetchall():
    print(linha)

def limpar_campos():
    entry_titulo.delete(0, tk.END)
    entry_editora.delete(0, tk.END)
    entry_num_pag.delete(0, tk.END)
    entry_genero.delete(0, tk.END)
    entry_nota.delete(0, tk.END)
    combo_status.set("")

def adicionar_livro():
    try:
        nome = entry_titulo.get()
        editora = entry_editora.get()
        num = int(entry_num_pag.get())
        genero = entry_genero.get()
        data = date.today()
        status = combo_status.get()
        if status == "fila" or status == "abandonado":
            nota = 0
        else:
            nota = float(entry_nota.get())
        cursor.execute("insert into livros (titulo,editora,numero_pag,nota,genero,data_cad,status) values (%s, %s, %s, %s, %s, %s, %s)", (nome,editora,num,nota,genero,data,status))
        conexao.commit()
        print("CADASTRO REALIZADO!")
        limpar_campos()
        listar_livros()
    except ValueError:
        messagebox.showerror("Erro", "Verifique se todos os campos foram preenchidos com valores válidos.")
    except Exception as e:
        messagebox.showerror("Erro", f"Não foi possível cadastrar: {e}")

def remover_livro():
    selecionado = tabela.selection()
    if not selecionado:
        messagebox.showwarning("Atenção", "Selecione um livro na tabela para excluir.")
        return
    valores = tabela.item(selecionado[0], "values")
    id_livro = valores[0]
    nome = valores[1]
    resp = messagebox.askyesno("Confirmar exclusão", f"Confirma exclusão do livro '{nome}'?")
    if resp:
        try:
            cursor.execute("DELETE FROM livros WHERE id=%s", (id_livro,))
            conexao.commit()
            messagebox.showinfo("Sucesso", "Exclusão realizada!")
            listar_livros()
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível excluir: {e}")

def listar_livros():
    # limpa a tabela antes de recarregar, senão duplica os dados a cada clique
    for item in tabela.get_children():
        tabela.delete(item)

    cursor.execute("SELECT * FROM livros")
    for linha in cursor.fetchall():
        tabela.insert("", tk.END, values=linha)

def atualiza_livros():
    selecionado = tabela.selection()

    if not selecionado:
        messagebox.showwarning("Atenção", "Selecione um livro na tabela para atualizar.")
        return

    valores = tabela.item(selecionado[0], "values")
    id_livro = valores[0]
    nome = valores[1]
    nota_atual = valores[4]
    status_atual = valores[7]

    if status_atual == "lido":
        messagebox.showwarning("Aviso", "Este livro já foi lido e não pode ser atualizado.")
        return

    # ---------- janela secundária ----------
    janela_att = tk.Toplevel(janela)
    janela_att.title(f"Atualizar - {nome}")
    janela_att.geometry("300x200")
    janela_att.transient(janela)   # mantém vinculada à janela principal
    janela_att.grab_set()          # bloqueia interação com a janela principal até fechar essa

    tk.Label(janela_att, text=f"Livro: {nome}", font=("Arial", 10, "bold")).pack(pady=10)

    frame_campos = tk.Frame(janela_att)
    frame_campos.pack(pady=5)

    tk.Label(frame_campos, text="Status:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    combo_status_att = ttk.Combobox(
        frame_campos, width=15, state="readonly",
        values=["Lendo", "Lido", "Fila", "Abandonado"]
    )
    combo_status_att.set(status_atual)  # já vem preenchido com o valor atual
    combo_status_att.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(frame_campos, text="Nota:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
    entry_nota_att = tk.Entry(frame_campos, width=10)
    entry_nota_att.insert(0, nota_atual)  # já vem preenchido com o valor atual
    entry_nota_att.grid(row=1, column=1, padx=5, pady=5)

    def salvar_atualizacao():
        novo_status = combo_status_att.get()
        try:
            nova_nota = float(entry_nota_att.get())
        except ValueError:
            messagebox.showerror("Erro", "Nota inválida.")
            return

        try:
            cursor.execute(
                "UPDATE livros SET status = %s, nota = %s WHERE id = %s",
                (novo_status, nova_nota, id_livro)
            )
            conexao.commit()
            messagebox.showinfo("Sucesso", "Livro atualizado!")
            listar_livros()
            janela_att.destroy()  # fecha a janela secundária
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível atualizar: {e}")

    tk.Button(janela_att, text="Salvar", command=salvar_atualizacao, width=15).pack(pady=15)

#Interface
janela = tk.Tk()
janela.title("Gerenciador de Biblioteca")
janela.geometry("850x600")
janela.minsize(800, 500)
frame_form = tk.LabelFrame(janela, text="Dados do Livro", padx=10, pady=10)
frame_form.pack(padx=10, pady=10, fill="x")

# Linha 0
tk.Label(frame_form, text="Título:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
entry_titulo = tk.Entry(frame_form, width=40)
entry_titulo.grid(row=0, column=1, columnspan=3, padx=5, pady=5, sticky="w")

# Linha 1 - Editora
tk.Label(frame_form, text="Editora:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
entry_editora = tk.Entry(frame_form, width=40)
entry_editora.grid(row=1, column=1, columnspan=3, padx=5, pady=5, sticky="w")

# Linha 2 - Gênero
tk.Label(frame_form, text="Gênero:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
entry_genero = tk.Entry(frame_form, width=40)
entry_genero.grid(row=2, column=1, columnspan=3, padx=5, pady=5, sticky="w")

# Linha 3 - Número de páginas e Nota lado a lado
tk.Label(frame_form, text="Nº de páginas:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
entry_num_pag = tk.Entry(frame_form, width=10)
entry_num_pag.grid(row=3, column=1, padx=5, pady=5, sticky="w")

tk.Label(frame_form, text="Nota:").grid(row=3, column=2, sticky="w", padx=5, pady=5)
entry_nota = tk.Entry(frame_form, width=10)
entry_nota.grid(row=3, column=3, padx=5, pady=5, sticky="w")

# Linha 4 - Status (Combobox)
tk.Label(frame_form, text="Status:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
combo_status = ttk.Combobox(
    frame_form,
    width=20,
    state="readonly",  # impede o usuário de digitar algo fora da lista
    values=["lendo", "lido", "fila", "abandonado"]
)
combo_status.grid(row=4, column=1, padx=5, pady=5, sticky="w")

# ===================== FRAME DOS BOTÕES =====================
frame_botoes = tk.Frame(janela)
frame_botoes.pack(pady=5)

botao_criar = tk.Button(frame_botoes, text="Criar",command=adicionar_livro, width=12)
botao_criar.grid(row=0, column=0, padx=5)

botao_atualizar = tk.Button(frame_botoes, text="Atualizar",command=atualiza_livros, width=12)
botao_atualizar.grid(row=0, column=1, padx=5)

botao_excluir = tk.Button(frame_botoes, text="Excluir",command=remover_livro, width=12, bg="#e57373")
botao_excluir.grid(row=0, column=2, padx=(20, 5))

botao_limpar = tk.Button(frame_botoes, text="Limpar",command=limpar_campos, width=12)
botao_limpar.grid(row=0, column=3, padx=5)

# ===================== FRAME TABELA =====================
frame_tabela = tk.Frame(janela)
frame_tabela.pack(padx=10, pady=10, fill="both", expand=True)
tabela = ttk.Treeview(
    frame_tabela,
    columns=("id", "titulo", "editora", "num_pag", "nota", "genero", "data_cad", "status"),
    show="headings"
)
tabela.column("id", width=35, anchor="center")
tabela.column("titulo", width=140)
tabela.column("editora", width=100)
tabela.column("num_pag", width=60, anchor="center")
tabela.column("nota", width=50, anchor="center")
tabela.column("genero", width=90)
tabela.column("data_cad", width=80, anchor="center")
tabela.column("status", width=80, anchor="center")
tabela.heading("id", text="ID")
tabela.heading("titulo", text="Título")
tabela.heading("editora", text="Editora")
tabela.heading("num_pag", text="Páginas")
tabela.heading("nota", text="Nota")
tabela.heading("genero", text="Gênero")
tabela.heading("data_cad", text="Data Cad.")
tabela.heading("status", text="Status")
scrollbar = ttk.Scrollbar(frame_tabela, orient="vertical", command=tabela.yview)
tabela.configure(yscrollcommand=scrollbar.set)

tabela.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")


listar_livros()
janela.mainloop()

#Chamando funcões primarias
#menu()
cursor.close()
conexao.close()