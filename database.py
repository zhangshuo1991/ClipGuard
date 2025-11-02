# database.py
import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.expanduser("~/.clipguard/clipboard.db")

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS clipboard (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            masked_content TEXT NOT NULL,
            source_app TEXT,
            category TEXT,
            sensitive_types TEXT,
            has_sensitive BOOLEAN,
            timestamp TEXT,
            is_favorite INTEGER DEFAULT 0,
            is_deleted INTEGER DEFAULT 0
        )
    """)
    _ensure_column(conn, "is_favorite", "INTEGER DEFAULT 0")
    _ensure_column(conn, "is_deleted", "INTEGER DEFAULT 0")
    _ensure_fts(conn)
    conn.commit()
    conn.close()


def _ensure_column(conn, column, definition):
    cursor = conn.execute("PRAGMA table_info(clipboard)")
    columns = {row[1] for row in cursor.fetchall()}
    if column not in columns:
        conn.execute(f"ALTER TABLE clipboard ADD COLUMN {column} {definition}")


def add_record(masked, app, category, sensitive_types, has_sensitive, timestamp=None):
    conn = sqlite3.connect(DB_PATH)
    if timestamp is None:
        timestamp = datetime.now().isoformat()
    types_serialized = ",".join(sensitive_types)
    print(f"[调试] 写入数据库：app={app}, category={category}, has_sensitive={has_sensitive}, types={types_serialized}, timestamp={timestamp}")
    cursor = conn.execute("""
        INSERT INTO clipboard (masked_content, source_app, category, sensitive_types, has_sensitive, timestamp, is_favorite, is_deleted)
        VALUES (?, ?, ?, ?, ?, ?, 0, 0)
    """, (masked, app, category, types_serialized, has_sensitive, timestamp))
    row_id = cursor.lastrowid
    _upsert_fts(conn, row_id, masked, app, category, types_serialized)
    conn.commit()
    conn.close()
    return row_id


def set_deleted(record_id, deleted=True):
    conn = sqlite3.connect(DB_PATH)
    flag = 1 if deleted else 0
    print(f"[调试] 更新数据库记录删除状态 id={record_id}, deleted={flag}")
    conn.execute("UPDATE clipboard SET is_deleted = ? WHERE id = ?", (flag, record_id))
    conn.commit()
    conn.close()


def delete_permanently(record_id):
    conn = sqlite3.connect(DB_PATH)
    print(f"[调试] 永久删除数据库记录 id={record_id}")
    conn.execute("DELETE FROM clipboard WHERE id = ?", (record_id,))
    _delete_fts(conn, record_id)
    conn.commit()
    conn.close()


def set_favorite(record_id, favorite=True):
    conn = sqlite3.connect(DB_PATH)
    flag = 1 if favorite else 0
    print(f"[调试] 更新收藏状态 id={record_id}, favorite={flag}")
    conn.execute("UPDATE clipboard SET is_favorite = ? WHERE id = ?", (flag, record_id))
    conn.commit()
    conn.close()


def get_all_records(limit=200):
    return get_records(limit=limit)


def get_records(limit=200, search=None):
    conn = sqlite3.connect(DB_PATH)
    try:
        if search:
            match_query = _build_match_query(search)
            if not match_query:
                match_query = search.strip()
            cursor = conn.execute(
                """
                SELECT c.id,
                       c.masked_content,
                       c.source_app,
                       c.category,
                       c.sensitive_types,
                       c.has_sensitive,
                       c.timestamp,
                       c.is_favorite,
                       c.is_deleted
                FROM clipboard_fts
                JOIN clipboard c ON c.id = clipboard_fts.rowid
                WHERE clipboard_fts MATCH ?
                ORDER BY rank, c.timestamp DESC
                LIMIT ?
                """,
                (match_query, limit),
            )
        else:
            cursor = conn.execute(
                """
                SELECT id, masked_content, source_app, category, sensitive_types, has_sensitive, timestamp, is_favorite, is_deleted
                FROM clipboard
                ORDER BY timestamp DESC
                LIMIT ?
                """,
                (limit,),
            )
        rows = cursor.fetchall()
    except sqlite3.OperationalError as exc:
        print(f"[调试] FTS 查询失败，退回全文数据：{exc}")
        cursor = conn.execute(
            """
            SELECT id, masked_content, source_app, category, sensitive_types, has_sensitive, timestamp, is_favorite, is_deleted
            FROM clipboard
            ORDER BY timestamp DESC
            LIMIT ?
            """,
            (limit,),
        )
        rows = cursor.fetchall()
    conn.close()
    return rows


def _ensure_fts(conn):
    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='clipboard_fts'"
    )
    existed = cursor.fetchone() is not None
    conn.execute(
        """
        CREATE VIRTUAL TABLE IF NOT EXISTS clipboard_fts
        USING fts5(
            masked_content,
            source_app,
            category,
            sensitive_types,
            tokenize='unicode61'
        )
        """
    )
    if not existed:
        _rebuild_fts(conn)
        return
    try:
        total = conn.execute("SELECT COUNT(*) FROM clipboard").fetchone()[0]
        current = conn.execute("SELECT COUNT(*) FROM clipboard_fts").fetchone()[0]
    except sqlite3.DatabaseError:
        _rebuild_fts(conn)
        return
    if total != current:
        _rebuild_fts(conn)


def _rebuild_fts(conn):
    conn.execute("DELETE FROM clipboard_fts")
    conn.execute(
        """
        INSERT INTO clipboard_fts(rowid, masked_content, source_app, category, sensitive_types)
        SELECT id,
               IFNULL(masked_content, ''),
               IFNULL(source_app, ''),
               IFNULL(category, ''),
               IFNULL(sensitive_types, '')
        FROM clipboard
        """
    )


def _upsert_fts(conn, record_id, masked, app, category, sensitive_types):
    conn.execute("DELETE FROM clipboard_fts WHERE rowid = ?", (record_id,))
    conn.execute(
        """
        INSERT INTO clipboard_fts(rowid, masked_content, source_app, category, sensitive_types)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            record_id,
            masked or "",
            app or "",
            category or "",
            _normalize_types_for_fts(sensitive_types),
        ),
    )


def _delete_fts(conn, record_id):
    conn.execute("DELETE FROM clipboard_fts WHERE rowid = ?", (record_id,))


def _normalize_types_for_fts(types_value):
    if not types_value:
        return ""
    if isinstance(types_value, (list, tuple)):
        parts = types_value
    else:
        parts = str(types_value).replace(",", " ").split()
    return " ".join(part for part in parts if part)


def _build_match_query(text: str) -> str:
    if not text:
        return ""
    tokens = _tokenize_query(text)
    if not tokens:
        return ""

    parsed = [_parse_token(tok) for tok in tokens]
    parsed = [item for item in parsed if item is not None]
    if not parsed:
        return ""

    result = []
    result_types = []
    total = len(parsed)
    for idx, item in enumerate(parsed):
        typ = item[0]
        val = item[1]
        if typ == "LPAREN":
            result.append(val)
            result_types.append(typ)
            continue
        if typ == "RPAREN":
            if result_types and result_types[-1] != "LPAREN":
                result.append(val)
                result_types.append(typ)
            continue
        if typ in {"AND", "OR", "NEAR"}:
            if not _can_include_binary(result_types, typ):
                continue
            if not _has_operand_ahead(parsed, idx + 1):
                continue
            result.append(val)
            result_types.append(typ)
            continue
        if typ == "NOT":
            if not _has_operand_ahead(parsed, idx + 1):
                continue
            result.append(val)
            result_types.append(typ)
            continue
        # term or phrase
        result.append(val)
        result_types.append(typ)

    if not result:
        return ""
    expression = " ".join(result)
    expression = expression.replace("( ", "(").replace(" )", ")")
    return expression


def _tokenize_query(text: str) -> list[str]:
    tokens = []
    buf = []
    in_quote = False
    for ch in text:
        if ch == '"':
            buf.append(ch)
            in_quote = not in_quote
        elif in_quote:
            buf.append(ch)
        elif ch.isspace():
            if buf:
                tokens.append("".join(buf))
                buf = []
        elif ch in "()":
            if buf:
                tokens.append("".join(buf))
                buf = []
            tokens.append(ch)
        else:
            buf.append(ch)
    if buf:
        tokens.append("".join(buf))
    return [tok for tok in tokens if tok]


def _append_wildcard(token: str) -> str:
    if not token:
        return token
    if ":" in token:
        field, value = token.split(":", 1)
        value = value.strip()
        if not value:
            return field
        if value.endswith("*"):
            return f"{field}:{value}"
        return f"{field}:{value}*"
    if token.endswith("*"):
        return token
    return f"{token}*"


def _parse_token(token: str):
    if token == "(":
        return ("LPAREN", "(")
    if token == ")":
        return ("RPAREN", ")")
    if token.startswith('"') and token.endswith('"') and len(token) >= 2:
        inner = token[1:-1].strip()
        if not inner:
            return None
        return ("PHRASE", f'"{inner}"')

    upper = token.upper()
    if upper in {"AND", "OR"} and token.isalpha() and len(token) == len(upper):
        return (upper, upper)

    if upper == "NOT" and token.isalpha() and len(token) == len(upper):
        return ("NOT", "NOT")

    if (token == token.upper() and upper.startswith("NEAR")) or upper.startswith("NEAR/"):
        if "/" in token:
            prefix, _, suffix = token.partition("/")
            suffix = suffix.strip()
            if suffix.isdigit():
                return ("NEAR", prefix.upper() + "/" + suffix)
        return ("NEAR", "NEAR")

    cleaned = token.replace('"', "").replace("'", "")
    if not cleaned:
        return None
    return ("TERM", _append_wildcard(cleaned))


def _can_include_binary(result_types, operator):
    if not result_types:
        return False
    last = result_types[-1]
    if last in {"AND", "OR", "NEAR", "NOT", "LPAREN"}:
        return False
    return True


def _has_operand_ahead(parsed, start_index):
    for i in range(start_index, len(parsed)):
        typ, _ = parsed[i]
        if typ in {"TERM", "PHRASE", "LPAREN"}:
            return True
        if typ == "NOT":
            # ensure NOT itself has operand further ahead
            return _has_operand_ahead(parsed, i + 1)
    return False
