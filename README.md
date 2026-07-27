# oracle-dbms-project

![Python](https://img.shields.io/badge/Python-3.12-3776AB)
![Oracle](https://img.shields.io/badge/Oracle-23%20Free-F80000)
[![checks](https://img.shields.io/github/actions/workflow/status/Ismael-Sallami/oracle-dbms-project/ci.yml?branch=main&logo=github&label=checks)](https://github.com/Ismael-Sallami/oracle-dbms-project/actions/workflows/ci.yml)
![license](https://img.shields.io/badge/license-MIT-4c1)

A social network built the long way round: requirements first, then data-flow diagrams, an
entity-relationship schema, normalisation, and only at the end the Oracle database and the
Python client that talks to it.

## Context

Coursework for **Diseño y Desarrollo de Sistemas de Información**, year 4 of the double
degree in Computer Science and Business Administration, University of Granada (2025-26).
Group work: the subsystems were split between the members of the team and each one signs
their own chapters in the reports. Mine are the advertising subsystem, the entry point and
the database connection.

## The problem

Design an information system end to end, in the order the subject insists on: you do not get
to write a `CREATE TABLE` until the requirements, the diagrams and the normalisation say
which tables there should be.

Six subsystems: users, publications, messaging, advertising, trends and legal terms. Each
one has its own requirements, its own data-flow diagram and its own part of the schema, and
all of them share a single database.

## The solution

**The database.** Fifteen tables, and the rules the model cannot express live in nine
triggers and a procedure: a user cannot befriend themselves, and so on.
`RAISE_APPLICATION_ERROR` is what turns a business rule into something the database refuses
instead of something the application is trusted to remember.

**The client.** A Python application with one package per subsystem, each with its `menu.py`
and its `functions.py`, over a single connection object. Messaging encrypts the body of every
message with Fernet before it reaches the table, so the database never stores plain text.

**The documents.** Five deliverables in LaTeX with the whole trail of the design:
requirements and semantic constraints, black-box and level-0 and level-1 data-flow diagrams,
external schemas per process, the E/R schema, the functional dependencies and the
normalisation that produced the final tables.

## Layout

```
src/                 the Python client, one package per subsystem
  main.py            entry point
  db_connection.py   the connection, read from the environment
database/            schema, triggers and procedures
docs/practice-1      requirements, diagrams and E/R schema
docs/practice-3      triggers, transactions and legal terms
docs/seminar-1..2    the seminars
docs/coursework-4    the fourth assignment
tools/               the checks the CI runs
```

## Requirements

- Python 3.12 and the packages in `requirements.txt`.
- An Oracle database. The CI uses `gvenzl/oracle-free:slim`; the subject used
  `oracle0.ugr.es:1521/practbd`.
- LaTeX with `minted` and Pygments, only to rebuild the reports.

## Build and run

**Credentials come from the environment.** Nothing is written in the code:

```bash
pip install -r requirements.txt

export ORACLE_USER=your_user
export ORACLE_PASSWORD=your_password
export ORACLE_DSN=oracle0.ugr.es:1521/practbd

python3 src/main.py
```

To create the schema and load the triggers into a database of your own, and to compile the
application:

```bash
python3 tools/run-against-oracle.py     # the same script the CI runs
bash tools/check-python.sh
```

## Results

What the CI prints on every push, against a real Oracle:

```
database/00_init_tablas.sql: 16 statements
database/mensajeria/triggers_mensajeria.sql: 1 statements
  known failure in database/publicaciones/triggers_publicaciones.sql: ORA-06550
  known failure in database/publicaciones/triggers_publicaciones.sql: ORA-06550
database/publicaciones/triggers_publicaciones.sql: 2 statements, 2 known failures
database/publicidad/procedures_publicidad.sql: 1 statements
database/publicidad/triggers_publicidad.sql: 3 statements
database/tendencias/triggers_tendencias.sql: 1 statements
database/usuarios/triggers_usuarios.sql: 1 statements

45 tables and 8 triggers created, all valid
```

The check is not that the SQL parses: it is that Oracle accepts it and that no trigger ends
up as an invalid object, which is what a typo in a column name produces. That is how the
`SQL_CODE` bug below was found, after the code had been handed in and marked.

## What I learned

- The order of the subject is the lesson. Writing requirements before tables feels slow until
  normalisation changes three tables at once and not a line of code has been written yet.
- A rule that must always hold belongs in the database. Enforced only in the Python menus, it
  is a rule the next client to connect can ignore.
- **Limitations, and the one thing that had to be fixed:**
  - **The delivered code had university Oracle credentials written in four files**, mine and
    two teammates', with the password equal to the username. They are gone from the tree and
    from the history, and the connection now reads `ORACLE_USER`, `ORACLE_PASSWORD` and
    `ORACLE_DSN` from the environment. This is the only change to what was handed in:
    publishing someone else's credentials is not a defect to document, it is one to remove.
  - **Two PL/SQL blocks never compiled.** `database/publicaciones/triggers_publicaciones.sql`
    catches the "index already exists" error with `IF SQL_CODE != -955`, and PL/SQL has
    `SQLCODE`, not `SQL_CODE`. Oracle raises PLS-00201 and the two indexes on `ME_GUSTA` are
    never created. Running the SQL against a real database is what surfaced it; parsing it
    would not have. Listed in `tools/known-sql-failures.txt` and asserted, not patched.
  - `src/publicaciones/menu_TUI.py` **does not compile**. A triple-quoted block opened to
    comment out an old terminal prototype is never closed, and it swallows the rest of the
    file. `tools/check-python.sh` asserts that failure instead of skipping it. Not patched.
  - The application has no tests. What the checks do is compile it and exercise the database,
    which is what there is to check.
  - Identifiers, comments and the reports are in Spanish.

## Author and licence

Ismael Sallami Moreno, with the group of the subject. Released under the MIT licence (see
`LICENSE`).
