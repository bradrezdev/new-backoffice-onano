# Load Testing - NNProtect Payment Service

Sistema completo de load testing para validar el rendimiento del servicio de pagos bajo alta concurrencia (100+ transacciones simultáneas).

## 🎯 Objetivos

- Validar que el sistema maneja 100+ pagos concurrentes sin errores
- Response time p95 < 2 segundos
- Error rate < 1%
- Sin race conditions ni deadlocks
- Sin corrupción de datos en wallets

## 📁 Estructura de Archivos

```
testers/load_testing/
├── seed_load_test_data.py       # Genera 200 usuarios de prueba (ID 80000-80199)
├── locustfile.py                # Script principal de Locust para load testing
├── monitor_load_test.py         # Monitoreo en tiempo real de DB
├── monitoring_queries.sql       # Queries SQL para análisis manual
├── validate_staging_env.sh      # Validación pre-test
├── post_test_analysis.sh        # Análisis post-test
├── alert_thresholds.py          # Umbrales de alerta
├── .env.staging.example         # Ejemplo de configuración
├── docker-compose.staging.yml   # PostgreSQL local para staging
└── README.md                    # Esta documentación
```

## 🚀 Guía de Inicio Rápido

### Paso 1: Configurar Ambiente de Staging

**Opción A: Usar Supabase Staging**
```bash
# 1. Crear proyecto staging en Supabase
# 2. Copiar credenciales
cp testers/load_testing/.env.staging.example .env.staging
# 3. Editar .env.staging con tus credenciales
```

**Opción B: Usar PostgreSQL Local (Docker)**
```bash
# 1. Levantar PostgreSQL staging
docker-compose -f testers/load_testing/docker-compose.staging.yml up -d

# 2. Configurar .env.staging
cat > .env.staging << 'EOF'
DATABASE_URL=postgresql://staging_user:staging_pass_CHANGE_ME@localhost:5433/nnprotect_staging
ENVIRONMENT=staging
EOF
```

### Paso 2: Instalar Dependencias

```bash
# Instalar Locust
pip install locust==2.32.5

# Verificar instalación
locust --version
```

### Paso 3: Validar Ambiente

```bash
# Ejecutar validación de seguridad
chmod +x testers/load_testing/validate_staging_env.sh
./testers/load_testing/validate_staging_env.sh
```

### Paso 4: Seed Data de Prueba

```bash
# Generar 200 usuarios con wallets
python testers/load_testing/seed_load_test_data.py
```

### Paso 5: Ejecutar Load Test

**Terminal 1: Monitoring**
```bash
python testers/load_testing/monitor_load_test.py
```

**Terminal 2: Load Test**
```bash
# Escenario 1: 100 usuarios concurrentes, 10 minutos
locust -f testers/load_testing/locustfile.py --headless \
  --users 100 \
  --spawn-rate 10 \
  --run-time 10m \
  --html reports/load_test_100users.html
```

### Paso 6: Análisis Post-Test

```bash
chmod +x testers/load_testing/post_test_analysis.sh
./testers/load_testing/post_test_analysis.sh
```

## 📊 Escenarios de Carga

### Escenario 1: Carga Sostenida (Baseline)
```bash
locust -f testers/load_testing/locustfile.py --headless \
  --users 100 \
  --spawn-rate 10 \
  --run-time 10m \
  --csv reports/scenario1 \
  --html reports/scenario1.html
```
**Objetivo:** Establecer baseline de performance

### Escenario 2: Rampa Gradual
```bash
locust -f testers/load_testing/locustfile.py --headless \
  --users 200 \
  --spawn-rate 20 \
  --run-time 10m \
  --csv reports/scenario2 \
  --html reports/scenario2.html
```
**Objetivo:** Validar escalabilidad gradual

### Escenario 3: Spike Test
```bash
locust -f testers/load_testing/locustfile.py --headless \
  --users 300 \
  --spawn-rate 300 \
  --run-time 3m \
  --csv reports/scenario3 \
  --html reports/scenario3.html
```
**Objetivo:** Identificar punto de quiebre

### Escenario 4: Endurance Test
```bash
locust -f testers/load_testing/locustfile.py --headless \
  --users 100 \
  --spawn-rate 10 \
  --run-time 1h \
  --csv reports/scenario4 \
  --html reports/scenario4.html
```
**Objetivo:** Detectar memory leaks

## 🔍 Métricas Monitoreadas

### Performance
- Response time (p50, p95, p99)
- Throughput (requests/second)
- Error rate (%)

### Database
- Active connections
- Connection pool usage
- Locks y deadlocks
- Query execution time

### Data Integrity
- Wallet balance consistency
- Transaction completeness
- Race conditions

## ⚠️ Umbrales de Alerta

| Métrica | Umbral | Severidad |
|---------|--------|-----------|
| Response time p95 | < 2000ms | WARNING |
| Error rate | < 1% | WARNING |
| Race conditions | 0 | CRITICAL |
| Deadlocks | 0 | CRITICAL |
| DB connections | < 150 activas | WARNING |
| Wallet mismatches | 0 | CRITICAL |

## 🛡️ Seguridad

### ✅ Medidas Implementadas
- Ambiente staging 100% aislado
- Member IDs en rango 80000-80199 (no conflicto con producción)
- Validación pre-test obligatoria
- `.env.staging` en `.gitignore`

### ❌ Nunca
- Ejecutar load tests contra producción
- Commitear `.env.staging` al repositorio
- Usar datos reales de usuarios

## 📈 Análisis de Resultados

### Revisar Reporte HTML
```bash
open reports/scenario1.html
```

### Queries Manuales de DB
```bash
# Conectar a staging
psql $DATABASE_URL

# Ejecutar queries de monitoring
\i testers/load_testing/monitoring_queries.sql
```

### Validar Integridad
```bash
python -c "
from testers.load_testing.alert_thresholds import check_thresholds, print_violations
metrics = {
    'response_time_p95_ms': 1800,
    'error_rate_percent': 0.3,
    'race_condition_count': 0
}
violations = check_thresholds(metrics)
print_violations(violations)
"
```

## 🐛 Troubleshooting

### Error: "Connection refused"
```bash
# Verificar que staging DB está corriendo
docker ps | grep postgres-staging

# O si usas Supabase, verifica la URL
echo $DATABASE_URL
```

### Error: "Locust not found"
```bash
pip install locust==2.32.5
```

### Error: "No hay productos en DB staging"
```bash
# Copiar productos desde producción o crearlos manualmente
# Los productos se reutilizan de la tabla Products existente
```

### Race conditions detectadas
```bash
# Revisar logs detallados
grep "ya fue procesada" reports/*.log

# Analizar orden de locks en PaymentService
# payment_service/payment_service.py:45-120
```

## 📚 Referencias

- [Locust Documentation](https://docs.locust.io/)
- [PostgreSQL Performance Tuning](https://wiki.postgresql.org/wiki/Performance_Optimization)
- [SQLAlchemy Connection Pooling](https://docs.sqlalchemy.org/en/20/core/pooling.html)

## 🤝 Soporte

Para issues o preguntas sobre el load testing:
1. Revisar logs en `reports/`
2. Consultar `monitoring_queries.sql`
3. Ejecutar `post_test_analysis.sh`

---

**Última actualización:** 2025-10-02
**Mantenedor:** DevOps Team
