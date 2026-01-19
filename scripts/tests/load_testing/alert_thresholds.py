"""
UMBRALES DE ALERTA PARA LOAD TESTING
=====================================

Define los umbrales aceptables para métricas de performance.
"""

THRESHOLDS = {
    # Performance
    "response_time_p95_ms": 2000,
    "response_time_p99_ms": 5000,

    # Reliability
    "error_rate_percent": 1.0,
    "race_condition_count": 0,  # Zero tolerance
    "deadlock_count": 0,  # Zero tolerance

    # Database
    "db_connection_pool_usage_percent": 80,
    "db_active_connections_max": 150,

    # Data Integrity
    "wallet_balance_mismatch_count": 0,  # Zero tolerance
    "orphan_transactions_count": 0,

    # Memory
    "memory_usage_mb_max": 2048,
    "memory_leak_trend": "stable"  # stable | increasing
}

def check_thresholds(metrics: dict) -> list:
    """
    Valida métricas contra umbrales.

    Args:
        metrics: Diccionario con las métricas capturadas

    Returns:
        Lista de violaciones encontradas
    """
    violations = []

    for key, threshold in THRESHOLDS.items():
        if key in metrics:
            if isinstance(threshold, (int, float)):
                if metrics[key] > threshold:
                    severity = "CRITICAL" if any(x in key for x in ["race_condition", "deadlock", "mismatch"]) else "WARNING"
                    violations.append({
                        "metric": key,
                        "value": metrics[key],
                        "threshold": threshold,
                        "severity": severity
                    })

    return violations

def print_violations(violations: list):
    """Imprime violaciones en formato legible."""
    if not violations:
        print("✅ Todas las métricas dentro de umbrales aceptables")
        return

    print(f"\n⚠️  {len(violations)} VIOLACIONES DETECTADAS:")
    print("="*80)

    for v in violations:
        icon = "🔴" if v["severity"] == "CRITICAL" else "⚠️ "
        print(f"{icon} [{v['severity']}] {v['metric']}")
        print(f"   Valor: {v['value']} | Umbral: {v['threshold']}")
        print()

if __name__ == "__main__":
    # Ejemplo de uso
    test_metrics = {
        "response_time_p95_ms": 2500,  # Viola umbral
        "error_rate_percent": 0.5,  # OK
        "race_condition_count": 2,  # Viola umbral (CRITICAL)
        "db_active_connections_max": 120  # OK
    }

    violations = check_thresholds(test_metrics)
    print_violations(violations)
