TABLE_CREATE_QUERIES = ["""
CREATE TABLE "posts" (
    "id"	INTEGER NOT NULL UNIQUE,
    "coin_type"	TEXT NOT NULL,
    "user"	TEXT NOT NULL,
    "content"	TEXT NOT NULL,
    "source"	TEXT NOT NULL,
    "interaction"	INTEGER DEFAULT 0,
    "time"	INTEGER NOT NULL,
    "unique_id"	TEXT NOT NULL UNIQUE,
    "type"	TEXT NOT NULL,
    PRIMARY KEY("id" AUTOINCREMENT)
)
""", """
    CREATE TABLE "prices" (
    "id"	INTEGER NOT NULL UNIQUE,
    "coin_type"	TEXT NOT NULL,
    "price"	REAL NOT NULL,
    "time"	INTEGER NOT NULL,
    "volume"	REAL NOT NULL,
    "type"	TEXT NOT NULL,
    PRIMARY KEY("id" AUTOINCREMENT)
)
""", """
CREATE TABLE "cached_ranges" (
    "id"	INTEGER NOT NULL UNIQUE,
    "low"	INTEGER NOT NULL,
    "high"	INTEGER NOT NULL,
    "type"	TEXT NOT NULL,
    PRIMARY KEY("id" AUTOINCREMENT)
)
""", """
CREATE TABLE "users" (
    "id"	INTEGER NOT NULL UNIQUE,
    "username"	TEXT NOT NULL UNIQUE,
    "password" TEXT NOT NULL,
    "salt" TEXT NOT NULL,
    PRIMARY KEY("id" AUTOINCREMENT)
)
""", """
CREATE TABLE "followed_coins" (
    "id"	INTEGER NOT NULL UNIQUE,
    "userid" INTEGER NOT NULL,
    "coin_type" TEXT NOT NULL,
    PRIMARY KEY("id" AUTOINCREMENT)
)
""", """
CREATE TABLE "followed_sources" (
    "id"	INTEGER NOT NULL UNIQUE,
    "userid" INTEGER NOT NULL,
    "source" TEXT NOT NULL,
    PRIMARY KEY("id" AUTOINCREMENT)
)
""", """
CREATE TABLE "sessions" (
    "id"	INTEGER NOT NULL UNIQUE,
    "userid" INTEGER NOT NULL,
    "token" TEXT NOT NULL,
    "expiration" INTEGER NOT NULL,
    PRIMARY KEY("id" AUTOINCREMENT)
)"""
                        ]


class RangeSelector:
    def __init__(self, col, low, high):
        self.col = col
        self.low = low
        self.high = high


class MatchSelector:
    def __init__(self, col, needle):
        self.col = col
        self.needle = needle


# Creates an INSERT query.
def generate_insert_query(table_name, cols):
    cols_sql = "(" + ",".join(cols) + ")"
    vals_sql = "(" + ",".join(["?"] * len(cols)) + ")"
    return "INSERT INTO " + table_name + cols_sql + " VALUES " + vals_sql


# Creates an INSERT query.
# Should ignore errors during batch insertion.
def generate_insert_with_ignore_query(table_name, cols):
    cols_sql = "(" + ",".join(cols) + ")"
    vals_sql = "(" + ",".join(["?"] * len(cols)) + ")"
    return "INSERT OR IGNORE INTO " + table_name + cols_sql + " VALUES " + vals_sql


def create_conditionals(selectors: list) -> (str, list):
    params = []
    conds = []
    sql = ""
    for (i, selector) in enumerate(selectors):
        if isinstance(selector, RangeSelector):
            cond = "(" + selector.col + " <= ? AND " + selector.col + " >= ?)"
            conds.append(cond)
            params += [selector.high, selector.low]
        elif isinstance(selector, MatchSelector):
            cond = "(" + selector.col + " = ?)"
            conds.append(cond)
            params += [selector.needle]
    if len(conds) > 0:
        sql = "WHERE " + " AND ".join(conds)
    return sql, params


# Creates a SELECT query with given predicates in the form of selector objects.
def generate_select_query(table_name, selectors: list) -> (str, list):
    sql = "SELECT * FROM " + table_name
    cond_sql, cond_params = create_conditionals(selectors)
    sql += " " + cond_sql
    return sql, cond_params


# Creates a DELETE query with given predicates in the form of selector objects.
def generate_delete_query(table_name, selectors: list):
    sql = "DELETE FROM " + table_name
    cond_sql, cond_params = create_conditionals(selectors)
    sql += " " + cond_sql
    return sql, cond_params


def generate_top_query(table_name, order_by, order_dir: str, limit: int, selectors: list):
    sql = "SELECT * FROM " + table_name
    cond_sql, cond_params = create_conditionals(selectors)
    sql += " " + cond_sql
    sql += " ORDER BY " + order_by + " " + order_dir
    sql += " LIMIT " + str(limit)
    return sql, cond_params


def generate_grouped_top_query(table_name, group_by, group_selector: str, limit: int, selectors: list):
    sql = "SELECT " + group_selector + ",* FROM " + table_name
    cond_sql, cond_params = create_conditionals(selectors)
    sql += " " + cond_sql
    sql += " GROUP BY " + group_by
    sql += " ORDER BY " + group_selector + " DESC"
    sql += " LIMIT " + str(limit)
    return sql, cond_params
