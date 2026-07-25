import json
import os

import psycopg2
import psycopg2.extras

def _get_config():
    """Re-read config from env vars (allows test overrides via monkeypatch)."""
    return {
        "host": os.environ.get("DB_HOST", "db"),
        "port": os.environ.get("DB_PORT", "5432"),
        "dbname": os.environ.get("DB_NAME", "appdb"),
        "user": os.environ.get("DB_USER", "appuser"),
        "password": os.environ.get("DB_PASSWORD", "apppassword"),
    }


def execute_query(sql: str) -> str:
    """Execute arbitrary SQL and return results as a JSON string.

    Intentionally has NO input validation -- security demo vulnerability.
    """
    config = _get_config()
    try:
        conn = psycopg2.connect(**config)
    except Exception as e:
        return json.dumps({"error": str(e)})
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql)
            if cur.description:
                rows = cur.fetchall()
                return json.dumps([dict(row) for row in rows], default=str)
            else:
                conn.commit()
                return json.dumps({"affected_rows": cur.rowcount})
    except Exception as e:
        conn.rollback()
        return json.dumps({"error": str(e)})
    finally:
        conn.close()


def get_tables() -> str:
    """Return all user tables and their columns as JSON."""
    config = _get_config()
    try:
        conn = psycopg2.connect(**config)
    except Exception as e:
        return json.dumps({"error": str(e)})
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                """
                SELECT table_name, column_name, data_type
                FROM information_schema.columns
                WHERE table_schema = 'public'
                ORDER BY table_name, ordinal_position
                """
            )
            rows = cur.fetchall()

            tables = {}
            for row in rows:
                tname = row["table_name"]
                if tname not in tables:
                    tables[tname] = {"table_name": tname, "columns": []}
                tables[tname]["columns"].append(
                    {"column_name": row["column_name"], "data_type": row["data_type"]}
                )

            return json.dumps(list(tables.values()), default=str)
    except Exception as e:
        return json.dumps({"error": str(e)})
    finally:
        conn.close()
