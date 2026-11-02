"""Organizador de tarefas em linha de comando, com persistência SQLite."""
import argparse
import csv
import sqlite3
from datetime import date
from pathlib import Path


def connect(path):
    db = sqlite3.connect(path)
    db.row_factory = sqlite3.Row
    db.execute("""CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY, title TEXT NOT NULL,
        due TEXT NOT NULL, priority INTEGER NOT NULL CHECK(priority BETWEEN 1 AND 3),
        done INTEGER NOT NULL DEFAULT 0 CHECK(done IN (0, 1)))""")
    return db


def add_task(db, title, due, priority=2):
    title = title.strip()
    if not title or len(title) > 200:
        raise ValueError("O título deve ter entre 1 e 200 caracteres.")
    due = date.fromisoformat(due).isoformat()
    if type(priority) is not int or priority not in (1, 2, 3):
        raise ValueError("Prioridade deve ser 1, 2 ou 3.")
    with db:
        cursor = db.execute("INSERT INTO tasks(title,due,priority) VALUES (?,?,?)",
                            (title, due, priority))
    return cursor.lastrowid


def list_tasks(db, status="pending"):
    filters = {"pending": "WHERE done=0", "done": "WHERE done=1", "all": ""}
    if status not in filters:
        raise ValueError("Status inválido.")
    return db.execute(f"SELECT * FROM tasks {filters[status]} ORDER BY due, priority, id").fetchall()


def complete_task(db, task_id):
    with db:
        result = db.execute("UPDATE tasks SET done=1 WHERE id=?", (task_id,))
    if not result.rowcount:
        raise ValueError("Tarefa não encontrada.")


def csv_safe(value):
    # Evita que títulos sejam interpretados como fórmulas em planilhas.
    return "'" + value if isinstance(value, str) and value.lstrip().startswith(("=", "+", "-", "@")) else value


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", default="rotina.db", help="Caminho do banco SQLite")
    commands = parser.add_subparsers(dest="command", required=True)
    add = commands.add_parser("adicionar", help="Cadastrar uma tarefa")
    add.add_argument("title")
    add.add_argument("--prazo", required=True, help="Data AAAA-MM-DD")
    add.add_argument("--prioridade", type=int, choices=(1, 2, 3), default=2)
    listing = commands.add_parser("listar")
    listing.add_argument("--status", choices=("pending", "done", "all"), default="pending")
    finish = commands.add_parser("concluir")
    finish.add_argument("id", type=int)
    commands.add_parser("resumo")
    export = commands.add_parser("exportar")
    export.add_argument("arquivo", type=Path)
    args = parser.parse_args(argv)
    db = None
    try:
        db = connect(args.db)
        if args.command == "adicionar":
            task_id = add_task(db, args.title, args.prazo, args.prioridade)
            print(f"Tarefa #{task_id} cadastrada.")
        elif args.command == "concluir":
            complete_task(db, args.id)
            print("Tarefa concluída.")
        elif args.command == "listar":
            rows = list_tasks(db, args.status)
            for row in rows:
                state = "concluída" if row["done"] else "pendente"
                print(f'#{row["id"]} | {row["due"]} | P{row["priority"]} | {state} | {row["title"]}')
            if not rows:
                print("Nenhuma tarefa encontrada.")
        elif args.command == "resumo":
            rows = list_tasks(db, "all")
            done = sum(row["done"] for row in rows)
            late = sum(not row["done"] and row["due"] < date.today().isoformat() for row in rows)
            print(f"Total: {len(rows)} | Concluídas: {done} | Pendentes: {len(rows)-done} | Atrasadas: {late}")
        elif args.command == "exportar":
            with args.arquivo.open("x", newline="", encoding="utf-8-sig") as file:
                writer = csv.writer(file)
                writer.writerow(["id", "titulo", "prazo", "prioridade", "concluida"])
                for row in list_tasks(db, "all"):
                    writer.writerow([csv_safe(row[key]) for key in ("id", "title", "due", "priority", "done")])
            print(f"Exportado para {args.arquivo}.")
    except (ValueError, OSError, sqlite3.Error) as error:
        parser.exit(1, f"Erro: {error}\n")
    finally:
        if db is not None:
            db.close()


if __name__ == "__main__":
    main()
