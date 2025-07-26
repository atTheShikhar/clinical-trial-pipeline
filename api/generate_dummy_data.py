import duckdb;


conn = duckdb.execute(
    """
    ATTACH DATABASE 'local.duckdb' AS local_db;
    ATTACH ':memory:' AS memory_db;
    USE local_db;
    """
)

conn.execute(
    "CREATE TABLE IF NOT EXISTS t1 (i INTEGER, v VARCHAR)"
)

conn.executemany(
    """
    INSERT INTO t1 (i, v)
    VALUES ($i, $v)
    """,
    [{"i": 1, "v": "val1"}, {"i": 2, "v": "val2"}]
)

duckdb.execute(
    """
    USE memory_db;
    DETACH DATABASE IF EXISTS local_db;
    """
)