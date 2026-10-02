from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)
BANCO = "achados_perdidos.db"

def conectar():
    banco = sqlite3.connect(BANCO)
    banco.row_factory = sqlite3.Row
    return banco

def criar_banco():
    banco = conectar()
    banco.execute("""
        CREATE TABLE IF NOT EXISTS itens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            descricao TEXT NOT NULL,
            local TEXT NOT NULL,
            contato TEXT NOT NULL,
            tipo TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Pendente'
        )
    """)
    banco.commit()
    banco.close()

@app.route("/")
def inicio():
    filtro = request.args.get("filtro", "todos")
    banco = conectar()

    if filtro == "perdidos":
        itens = banco.execute(
            "SELECT * FROM itens WHERE tipo = 'Perdido' ORDER BY id DESC"
        ).fetchall()
    elif filtro == "encontrados":
        itens = banco.execute(
            "SELECT * FROM itens WHERE tipo = 'Encontrado' ORDER BY id DESC"
        ).fetchall()
    else:
        itens = banco.execute(
            "SELECT * FROM itens ORDER BY id DESC"
        ).fetchall()

    banco.close()
    return render_template("index.html", itens=itens, filtro=filtro)

@app.route("/cadastrar", methods=["GET", "POST"])
def cadastrar():
    if request.method == "POST":
        nome = request.form["nome"]
        descricao = request.form["descricao"]
        local = request.form["local"]
        contato = request.form["contato"]
        tipo = request.form["tipo"]

        banco = conectar()
        banco.execute("""
            INSERT INTO itens
            (nome, descricao, local, contato, tipo)
            VALUES (?, ?, ?, ?, ?)
        """, (nome, descricao, local, contato, tipo))
        banco.commit()
        banco.close()
        return redirect(url_for("inicio"))

    return render_template("cadastro.html")

@app.route("/resolver/<int:id>", methods=["POST"])
def resolver(id):
    banco = conectar()
    banco.execute(
        "UPDATE itens SET status = 'Resolvido' WHERE id = ?",
        (id,)
    )
    banco.commit()
    banco.close()
    return redirect(url_for("inicio"))

@app.route("/excluir/<int:id>", methods=["POST"])
def excluir(id):
    banco = conectar()
    banco.execute("DELETE FROM itens WHERE id = ?", (id,))
    banco.commit()
    banco.close()
    return redirect(url_for("inicio"))

if __name__ == "__main__":
    criar_banco()
    app.run(debug=True)
