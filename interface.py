import tkinter as tk
from tkinter import ttk, messagebox
import crud

# widgets que precisam ser acessados por várias funções ficam declarados aqui
janela = None
entry_titulo = None
entry_editora = None
entry_genero = None
entry_num_pag = None
entry_nota = None
combo_status = None
tabela = None

STATUS_SEM_NOTA = ("fila", "abandonado")
OPCOES_STATUS = ["lendo", "lido", "fila", "abandonado"]


# ===================== FUNÇÕES DE TELA =====================
def limpar_campos():
    entry_titulo.delete(0, tk.END)
    entry_editora.delete(0, tk.END)
    entry_num_pag.delete(0, tk.END)
    entry_genero.delete(0, tk.END)
    entry_nota.delete(0, tk.END)
    combo_status.set("")

def obter_opcoes_autores():
    autores = crud.listar_autores()
    return [autor[1] for autor in autores]

def listar_desejos():
    pass


def atualizar_tabela_na_tela():
    for item in tabela.get_children():
        tabela.delete(item)
    for linha in crud.listar_livros():
        tabela.insert("", tk.END, values=linha)


def adicionar_livro_click():
    try:
        titulo = entry_titulo.get()
        editora = entry_editora.get()
        num_pag = int(entry_num_pag.get())
        genero = entry_genero.get()
        status = combo_status.get()
        autor = combo_autores.get().strip()

        if not autor:
            messagebox.showerror("Error", "O campo autor não pode ficar vazio")
            return

        if status in STATUS_SEM_NOTA:
            nota = 0
        else:
            nota = float(entry_nota.get())

        crud.adicionar_livro(titulo, editora, num_pag, genero, status, nota,autor)

        messagebox.showinfo("Sucesso", "Cadastro realizado!")
        limpar_campos()
        atualizar_tabela_na_tela()
        combo_autores['values'] = obter_opcoes_autores()

    except ValueError:
        messagebox.showerror("Erro", "Verifique se todos os campos foram preenchidos com valores válidos.")
    except Exception as e:
        messagebox.showerror("Erro", f"Não foi possível cadastrar: {e}")


def remover_livro_click():
    selecionado = tabela.selection()
    if not selecionado:
        messagebox.showwarning("Atenção", "Selecione um livro na tabela para excluir.")
        return

    valores = tabela.item(selecionado[0], "values")
    id_livro = valores[0]
    nome = valores[1]

    resp = messagebox.askyesno("Confirmar exclusão", f"Confirma exclusão do livro '{nome}'?")
    if not resp:
        return

    try:
        crud.remover_livro(id_livro)
        messagebox.showinfo("Sucesso", "Exclusão realizada!")
        atualizar_tabela_na_tela()
    except Exception as e:
        messagebox.showerror("Erro", f"Não foi possível excluir: {e}")


def atualizar_livro_click():
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
    janela_att.transient(janela)
    janela_att.grab_set()

    tk.Label(janela_att, text=f"Livro: {nome}", font=("Arial", 10, "bold")).pack(pady=10)

    frame_campos = tk.Frame(janela_att)
    frame_campos.pack(pady=5)

    tk.Label(frame_campos, text="Status:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    combo_status_att = ttk.Combobox(
        frame_campos, width=15, state="readonly", values=OPCOES_STATUS
    )
    combo_status_att.set(status_atual)
    combo_status_att.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(frame_campos, text="Nota:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
    entry_nota_att = tk.Entry(frame_campos, width=10)
    entry_nota_att.insert(0, nota_atual)
    entry_nota_att.grid(row=1, column=1, padx=5, pady=5)

    def salvar_atualizacao():
        novo_status = combo_status_att.get()
        try:
            nova_nota = float(entry_nota_att.get())
        except ValueError:
            messagebox.showerror("Erro", "Nota inválida.")
            return

        try:
            crud.atualizar_livro(id_livro, novo_status, nova_nota)
            messagebox.showinfo("Sucesso", "Livro atualizado!")
            atualizar_tabela_na_tela()
            janela_att.destroy()
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível atualizar: {e}")

    tk.Button(janela_att, text="Salvar", command=salvar_atualizacao, width=15).pack(pady=15)


def ao_fechar_janela():
    crud.fechar_conexao()
    janela.destroy()


# ===================== MONTAGEM DA INTERFACE =====================
def iniciar():
    global janela, entry_titulo, entry_editora, entry_genero
    global entry_num_pag, entry_nota, combo_status,combo_autores, tabela

    janela = tk.Tk()
    janela.title("Gerenciador de Biblioteca")
    janela.geometry("850x600")
    janela.minsize(800, 500)
    janela.protocol("WM_DELETE_WINDOW", ao_fechar_janela)

    # ---------- Formulário ----------
    frame_form = tk.LabelFrame(janela, text="Dados do Livro", padx=10, pady=10)
    frame_form.pack(padx=10, pady=10, fill="x")

    tk.Label(frame_form, text="Título:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
    entry_titulo = tk.Entry(frame_form, width=40)
    entry_titulo.grid(row=0, column=1, columnspan=3, padx=5, pady=5, sticky="w")

    tk.Label(frame_form, text="Editora:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
    entry_editora = tk.Entry(frame_form, width=40)
    entry_editora.grid(row=1, column=1, columnspan=3, padx=5, pady=5, sticky="w")

    tk.Label(frame_form, text="Gênero:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
    entry_genero = tk.Entry(frame_form, width=40)
    entry_genero.grid(row=2, column=1, columnspan=3, padx=5, pady=5, sticky="w")

    tk.Label(frame_form, text="Nº de páginas:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
    entry_num_pag = tk.Entry(frame_form, width=10)
    entry_num_pag.grid(row=3, column=1, padx=5, pady=5, sticky="w")

    tk.Label(frame_form, text="Nota:").grid(row=3, column=2, sticky="w", padx=5, pady=5)
    entry_nota = tk.Entry(frame_form, width=10)
    entry_nota.grid(row=3, column=3, padx=5, pady=5, sticky="w")

    tk.Label(frame_form, text="Status:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
    combo_status = ttk.Combobox(frame_form, state="readonly", width=20, values=OPCOES_STATUS)
    combo_status.grid(row=4, column=1, padx=5, pady=5, sticky="w")

    tk.Label(frame_form, text="Autor:").grid(row=4, column=2, sticky="w", padx=5, pady=5)
    combo_autores = ttk.Combobox(frame_form, width=20, values=obter_opcoes_autores())
    combo_autores.grid(row=4, column=3, padx=5, pady=5, sticky="w")

    # ---------- Botões ----------
    frame_botoes = tk.Frame(janela)
    frame_botoes.pack(pady=5)

    tk.Button(frame_botoes, text="Criar", command=adicionar_livro_click, width=12).grid(row=0, column=0, padx=5)
    tk.Button(frame_botoes, text="Atualizar", command=atualizar_livro_click, width=12).grid(row=0, column=1, padx=5)
    tk.Button(frame_botoes, text="Excluir", command=remover_livro_click, width=12, bg="#e57373").grid(row=0, column=2, padx=(20, 5))
    tk.Button(frame_botoes, text="Limpar", command=limpar_campos, width=12).grid(row=0, column=3, padx=5)
    

    # ---------- Tabela ----------
    frame_tabela = tk.Frame(janela)
    frame_tabela.pack(padx=10, pady=10, fill="both", expand=True)

    tabela = ttk.Treeview(
        frame_tabela,
        columns=("id", "titulo", "editora", "num_pag", "nota", "genero", "data_cad", "status", "Autor"),
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

    atualizar_tabela_na_tela()
    janela.mainloop()
