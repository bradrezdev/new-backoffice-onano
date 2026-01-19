-- QUERIES DE MONITOREO PARA LOAD TESTING
-- ========================================

-- 1. MONITOREAR CONNECTION POOL
SELECT
    count(*) as total_connections,
    count(*) FILTER (WHERE state = 'active') as active,
    count(*) FILTER (WHERE state = 'idle') as idle,
    count(*) FILTER (WHERE state = 'idle in transaction') as idle_in_transaction
FROM pg_stat_activity
WHERE datname = current_database();

-- 2. DETECTAR LOCKS Y DEADLOCKS
SELECT
    blocked_locks.pid AS blocked_pid,
    blocked_activity.usename AS blocked_user,
    blocking_locks.pid AS blocking_pid,
    blocking_activity.usename AS blocking_user,
    blocked_activity.query AS blocked_statement,
    blocking_activity.query AS blocking_statement
FROM pg_catalog.pg_locks blocked_locks
JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
JOIN pg_catalog.pg_locks blocking_locks
    ON blocking_locks.locktype = blocked_locks.locktype
    AND blocking_locks.database IS NOT DISTINCT FROM blocked_locks.database
    AND blocking_locks.relation IS NOT DISTINCT FROM blocked_locks.relation
    AND blocking_locks.page IS NOT DISTINCT FROM blocked_locks.page
    AND blocking_locks.tuple IS NOT DISTINCT FROM blocked_locks.tuple
    AND blocking_locks.virtualxid IS NOT DISTINCT FROM blocked_locks.virtualxid
    AND blocking_locks.transactionid IS NOT DISTINCT FROM blocked_locks.transactionid
    AND blocking_locks.classid IS NOT DISTINCT FROM blocked_locks.classid
    AND blocking_locks.objid IS NOT DISTINCT FROM blocked_locks.objid
    AND blocking_locks.objsubid IS NOT DISTINCT FROM blocked_locks.objsubid
    AND blocking_locks.pid != blocked_locks.pid
JOIN pg_catalog.pg_stat_activity blocking_activity ON blocking_activity.pid = blocking_locks.pid
WHERE NOT blocked_locks.granted;

-- 3. TOP QUERIES MÁS LENTAS (requiere pg_stat_statements extension)
-- Habilitar con: CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
SELECT
    query,
    calls,
    total_exec_time / 1000 as total_time_sec,
    mean_exec_time / 1000 as avg_time_sec,
    max_exec_time / 1000 as max_time_sec
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;

-- 4. TABLA DE WALLETS - CONTENTION
SELECT
    relname as table_name,
    n_tup_ins as inserts,
    n_tup_upd as updates,
    n_tup_del as deletes,
    n_live_tup as live_tuples,
    n_dead_tup as dead_tuples
FROM pg_stat_user_tables
WHERE relname IN ('wallets', 'orders', 'wallet_transactions', 'commissions')
ORDER BY n_tup_upd DESC;

-- 5. VERIFICAR INTEGRIDAD DE WALLETS
SELECT
    w.id,
    w.member_id,
    w.balance as current_balance,
    wt.balance_after as last_transaction_balance,
    CASE
        WHEN w.balance = wt.balance_after THEN '✅ OK'
        ELSE '❌ MISMATCH'
    END as integrity_check
FROM wallets w
LEFT JOIN LATERAL (
    SELECT balance_after
    FROM wallet_transactions
    WHERE member_id = w.member_id
    ORDER BY created_at DESC
    LIMIT 1
) wt ON true
WHERE w.member_id BETWEEN 80000 AND 80199
ORDER BY w.member_id;

-- 6. DETECTAR DEADLOCKS
SELECT * FROM pg_stat_database_conflicts WHERE datname = current_database();
