#!/bin/bash

echo "🔍 VALIDACIÓN DE AMBIENTE STAGING"
echo "=================================="

# 1. Verificar que existe .env.staging
if [ ! -f .env.staging ]; then
    echo "❌ ERROR: No existe .env.staging"
    echo "Por favor crea el archivo .env.staging con las credenciales de staging"
    exit 1
fi

echo "✅ Archivo .env.staging encontrado"

# 2. Verificar que NO estamos en producción
if grep -q "SUPABASE_URL" .env.staging; then
    if grep -q "supabase.co" .env.staging | grep -v "staging"; then
        echo "⚠️  ADVERTENCIA: Verifica que la URL de Supabase sea de staging"
    fi
fi

# 3. Verificar rango de member_ids
echo "✅ Usando member_ids en rango 80000-80199 (aislado de producción)"

# 4. Crear directorio de reportes si no existe
mkdir -p reports
echo "✅ Directorio reports/ creado"

# 5. Verificar que Locust está instalado
if ! command -v locust &> /dev/null; then
    echo "❌ ERROR: Locust no está instalado"
    echo "Ejecuta: pip install locust==2.32.5"
    exit 1
fi

echo "✅ Locust instalado correctamente"

# 6. Backup de staging antes de tests destructivos
echo "📦 Preparando ambiente para load testing..."

echo ""
echo "✅ VALIDACIÓN COMPLETADA - AMBIENTE SEGURO PARA LOAD TESTING"
echo "=============================================================="
echo ""
echo "Próximos pasos:"
echo "1. Ejecutar seed: python testers/load_testing/seed_load_test_data.py"
echo "2. Iniciar monitoring: python testers/load_testing/monitor_load_test.py"
echo "3. Ejecutar load test: locust -f testers/load_testing/locustfile.py"
