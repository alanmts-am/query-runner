from typing import List
import yaml
import pandas as pd

from model.database import Database
from model.postgres import Postgres
from model.result import Result
from logger import console, log_stage, log_success, log_error, log_info, log_warning, print_summary

from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, MofNCompleteColumn


CONFIG_PATH = "config.yml"
QUERY_PATH = "query.sql"


def generate_xlsx(databases_result: List[Result]) -> int:
    frames = [
        pd.DataFrame(data=r.data, columns=r.columns)
        for r in databases_result
        if r.collected
    ]
    if not frames:
        return 0
    result_df = pd.concat(frames, ignore_index=True)
    result_df.to_excel("data.xlsx", index=False)
    return len(result_df)


# ── Etapa 1: Carregamento de configuração ────────────────────────────────────

log_stage("[1/5]", "Carregando configuração",
          f"Config: {CONFIG_PATH}  |  Query: {QUERY_PATH}")

try:
    with open(CONFIG_PATH, "r", encoding="utf8") as f:
        config = yaml.full_load(f)
    with open(QUERY_PATH, "r", encoding="utf8") as f:
        query = f.read()
except FileNotFoundError as ex:
    log_error(f"Arquivo não encontrado: {ex}")
    raise SystemExit(1)

HOST = config["connection"]["host"]
PORT = config["connection"]["port"]
DATABASE = config["connection"]["database"]
USER = config["connection"]["username"]
PASSWORD = config["connection"]["password"]
SOURCE_DATABASE = config["sql"]["database"]

log_success(
    f"Configuração carregada  (host: {HOST}, port: {PORT}, database: {DATABASE})")

# ── Etapa 2: Conexão ao banco central e busca dos bancos-alvo ────────────────

log_stage("[2/5]", "Conectando ao banco central", f"{HOST}:{PORT}/{DATABASE}")

with console.status("[cyan]Conectando e executando query de fonte...[/cyan]", spinner="dots"):
    database_main: Database = Postgres(
        host=HOST, port=PORT, database=DATABASE, username=USER, pwd=PASSWORD)
    targets_result: Result = database_main.run(query=SOURCE_DATABASE)

if not targets_result.collected:
    log_error(f"Falha ao consultar banco central: {targets_result.error}")
    raise SystemExit(1)

n_targets = len(targets_result.data)
log_success(f"Conectado  |  {n_targets} banco(s)-alvo encontrado(s)")

# ── Etapa 3: Instanciar bancos-alvo ──────────────────────────────────────────

log_stage("[3/5]", "Preparando bancos-alvo")

databases: List[Postgres] = []
db_names: List[str] = []

for row in targets_result.data:
    host, port, database, username, pwd = row[0], row[1], row[2], row[3], row[4]
    databases.append(Postgres(host=host, port=port,
                     database=database, username=username, pwd=pwd))
    db_names.append(f"{host}:{port}/{database}")
    log_info(f"{host}:{port}/{database}")

# ── Etapa 4: Execução das queries nos bancos-alvo ────────────────────────────

log_stage("[4/5]", "Executando queries nos bancos-alvo")

databases_result: List[Result] = []

with Progress(
    SpinnerColumn(),
    BarColumn(),
    MofNCompleteColumn(),
    TextColumn("[cyan]{task.description}[/cyan]"),
    console=console,
    transient=False,
) as progress:
    task = progress.add_task("Iniciando...", total=n_targets)

    for db, name in zip(databases, db_names):
        progress.update(task, description=name)
        result = db.run(query=query)
        databases_result.append(result)

        if result.collected:
            log_success(f"{name}  →  {len(result.data)} linha(s)")
        else:
            log_error(f"{name}  →  {result.error}")

        progress.advance(task)

# ── Etapa 5: Geração do Excel ────────────────────────────────────────────────

log_stage("[5/5]", "Gerando arquivo Excel")

with console.status("[cyan]Escrevendo data.xlsx...[/cyan]", spinner="dots"):
    total_rows = generate_xlsx(databases_result)

if total_rows > 0:
    log_success(f"data.xlsx gerado  ({total_rows} linha(s) no total)")
else:
    log_warning("Nenhuma linha coletada — arquivo Excel não gerado")

# ── Resumo final ─────────────────────────────────────────────────────────────

print_summary(databases_result, db_names)
