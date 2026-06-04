# Query Runner

Ferramenta para executar queries SQL em múltiplos bancos PostgreSQL em sequência. A partir de um banco central que armazena as conexões dos demais, o Query Runner conecta em cada banco-alvo, executa a query desejada e exporta os resultados consolidados para um arquivo Excel.

## Como funciona

```
Banco central (config.yml)
        │
        ▼
  Lista de conexões  ──►  Banco A  ──┐
  (via sql.database)  ──►  Banco B  ──┤──►  data.xlsx
                      ──►  Banco C  ──┘
```

1. Conecta no banco central definido em `config.yml`
2. Executa a query configurada em `sql.database` para obter a lista de bancos-alvo
3. Conecta em cada banco-alvo e executa a query em `query.sql`
4. Consolida os resultados e exporta para `data.xlsx` (somente para SELECT)

## Pré-requisitos

- Python 3.10+
- [Poetry](https://python-poetry.org/docs/#installation)

## Instalação

```bash
poetry install
```

## Configuração

### 1. Arquivo de configuração (`config.yml`)

Copie o template e preencha com suas credenciais:

```bash
cp config.template.yml config.yml
```

```yml
# Banco central que contém as demais conexões
connection:
  host: localhost
  port: 5432
  database: meu_banco
  username: usuario
  password: senha

sql:
  # Query que retorna as conexões dos bancos-alvo
  # Deve retornar as colunas nessa ordem: host, port, database_name, username, password
  database: SELECT host, port, database, username, password FROM connections
```

### 2. Query a ser executada (`query.sql`)

Insira na raiz do projeto a query que será executada em cada banco-alvo:

```sql
-- Exemplo para SELECT
SELECT id, name, created_at FROM users WHERE active = true;
```

```sql
-- Exemplo para UPDATE
UPDATE users SET status = 'inactive' WHERE last_login < NOW() - INTERVAL '1 year';
```

## Execução

```bash
poetry run python src/main.py
```

Para SELECT, o resultado consolidado de todos os bancos será salvo em `data.xlsx` na raiz do projeto.

## Estrutura do projeto

```
query-runner/
├── config.yml          # Configurações (não versionado)
├── config.template.yml # Template do config.yml
├── query.sql           # Query a ser executada nos bancos-alvo
└── src/
    ├── main.py
    └── model/
        ├── database.py # Classe base abstrata
        ├── postgres.py # Implementação PostgreSQL
        └── result.py   # Modelo de resultado
```
