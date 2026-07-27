#!/usr/bin/env python3
"""Create the schema and load every trigger and procedure into a real Oracle.

Parsing SQL only proves the text is well formed. This creates the fourteen
tables, then compiles each trigger and procedure, so a wrong column name or a
broken PL/SQL block fails here instead of passing quietly.

Uses python-oracledb in thin mode, so no Oracle client is needed.

    pip install oracledb
    python3 tools/run-against-oracle.py

Connection comes from ORACLE_DSN, ORACLE_USER and ORACLE_PASSWORD, defaulting
to the gvenzl/oracle-free container used in CI.

@author Ismael Sallami Moreno
"""

import os
import pathlib
import re
import sys

import oracledb

DSN = os.environ.get("ORACLE_DSN", "localhost:1521/FREEPDB1")
USER = os.environ.get("ORACLE_USER", "system")
PASSWORD = os.environ.get("ORACLE_PASSWORD", "test")

SCHEMA = pathlib.Path("database/00_init_tablas.sql")
DATABASE = pathlib.Path("database")

LINE_COMMENT = re.compile(r"--[^\n]*")

# "Table does not exist" and "no such constraint", both raised by the DROP TABLE
# header of the schema on a clean database.
MISSING_OBJECT = (942, 2289)


def statements(path: pathlib.Path) -> list[str]:
    """Split a script into statements.

    Oracle scripts mix two terminators: a semicolon ends a plain statement, and a
    lone slash on its own line ends a PL/SQL block, whose body is full of
    semicolons that must not be split on. So the file is cut on slashes first,
    and only the chunks without a block are cut on semicolons.
    """
    sql = LINE_COMMENT.sub("", path.read_text(encoding="utf-8"))
    out: list[str] = []
    for chunk in re.split(r"^\s*/\s*$", sql, flags=re.MULTILINE):
        chunk = chunk.strip()
        if not chunk:
            continue
        if re.search(r"\b(BEGIN|DECLARE|CREATE\s+(OR\s+REPLACE\s+)?(TRIGGER|PROCEDURE|FUNCTION|PACKAGE))\b",
                     chunk, re.IGNORECASE):
            out.append(chunk)
        else:
            out.extend(s.strip() for s in chunk.split(";") if s.strip())
    return out


def run_script(cursor, path: pathlib.Path, *, tolerate_missing: bool = False) -> int:
    done = 0
    for statement in statements(path):
        try:
            cursor.execute(statement)
            done += 1
        except oracledb.DatabaseError as error:
            (info,) = error.args
            if tolerate_missing and info.code in MISSING_OBJECT:
                continue
            print(f"\nFAIL in {path}:\n{statement[:400]}\n  ORA-{info.code:05d}: {info.message}")
            raise
    return done


def invalid_objects(cursor) -> list[tuple[str, str]]:
    """Triggers and procedures that compiled with errors are invalid, not missing."""
    cursor.execute(
        "SELECT object_type, object_name FROM user_objects "
        "WHERE status = 'INVALID' ORDER BY object_type, object_name"
    )
    return cursor.fetchall()


def main() -> int:
    with oracledb.connect(user=USER, password=PASSWORD, dsn=DSN) as connection:
        with connection.cursor() as cursor:
            count = run_script(cursor, SCHEMA, tolerate_missing=True)
            print(f"{SCHEMA}: {count} statements")

            for path in sorted(DATABASE.rglob("*.sql")):
                if path == SCHEMA or path.name.endswith("_vAnterior.sql"):
                    continue
                count = run_script(cursor, path)
                print(f"{path}: {count} statements")

            broken = invalid_objects(cursor)
            if broken:
                print("\nObjects that did not compile:")
                for kind, name in broken:
                    print(f"  {kind} {name}")
                return 1

            cursor.execute("SELECT COUNT(*) FROM user_tables")
            (tables,) = cursor.fetchone()
            cursor.execute("SELECT COUNT(*) FROM user_triggers")
            (triggers,) = cursor.fetchone()
            print(f"\n{tables} tables and {triggers} triggers created, all valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
