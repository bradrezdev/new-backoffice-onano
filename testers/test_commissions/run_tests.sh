#!/bin/bash
#
# Script de Ejecución de Tests - Sistema de Comisiones MLM
#
# Autor: QA Engineer Giovann
# Fecha: Octubre 2025
#
# Uso:
#   ./run_tests.sh               # Ejecutar todos los tests
#   ./run_tests.sh fast          # Solo tests rápidos
#   ./run_tests.sh critical      # Solo tests críticos
#   ./run_tests.sh coverage      # Con reporte de cobertura
#

set -e  # Exit on error

# Colors para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Banner
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  TESTING - SISTEMA DE COMISIONES MLM  ${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Navegar al directorio del proyecto
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname $(dirname "$SCRIPT_DIR"))"
cd "$PROJECT_ROOT"

echo -e "${YELLOW}Directorio de trabajo:${NC} $PROJECT_ROOT"
echo ""

# Verificar que pytest está instalado
if ! command -v pytest &> /dev/null; then
    echo -e "${RED}ERROR: pytest no está instalado${NC}"
    echo -e "${YELLOW}Ejecuta: pip install pytest pytest-cov${NC}"
    exit 1
fi

# Determinar qué tests ejecutar
TEST_MODE="${1:-all}"

case $TEST_MODE in
    fast)
        echo -e "${GREEN}Modo: Tests Rápidos (excluyendo slow)${NC}"
        PYTEST_ARGS="-m 'not slow' -v"
        ;;
    critical)
        echo -e "${GREEN}Modo: Tests Críticos${NC}"
        PYTEST_ARGS="-m critical -v"
        ;;
    coverage)
        echo -e "${GREEN}Modo: Con Reporte de Cobertura${NC}"
        PYTEST_ARGS="-v --cov=NNProtect_new_website.modules.network.backend --cov-report=html --cov-report=term"
        ;;
    parallel)
        echo -e "${GREEN}Modo: Ejecución Paralela${NC}"
        if ! command -v pytest-xdist &> /dev/null; then
            echo -e "${YELLOW}ADVERTENCIA: pytest-xdist no está instalado${NC}"
            echo -e "${YELLOW}Ejecuta: pip install pytest-xdist${NC}"
            PYTEST_ARGS="-v"
        else
            PYTEST_ARGS="-n auto -v"
        fi
        ;;
    unit)
        echo -e "${GREEN}Modo: Solo Tests Unitarios${NC}"
        PYTEST_ARGS="testers/test_commissions/unit/ -v"
        ;;
    integration)
        echo -e "${GREEN}Modo: Solo Tests de Integración${NC}"
        PYTEST_ARGS="testers/test_commissions/integration/ -v"
        ;;
    e2e)
        echo -e "${GREEN}Modo: Solo Tests End-to-End${NC}"
        PYTEST_ARGS="testers/test_commissions/e2e/ -v"
        ;;
    all)
        echo -e "${GREEN}Modo: Todos los Tests${NC}"
        PYTEST_ARGS="-v"
        ;;
    *)
        echo -e "${RED}ERROR: Modo desconocido: $TEST_MODE${NC}"
        echo ""
        echo -e "${YELLOW}Modos disponibles:${NC}"
        echo "  all          - Ejecutar todos los tests (default)"
        echo "  fast         - Tests rápidos (excluyendo slow)"
        echo "  critical     - Solo tests críticos"
        echo "  coverage     - Con reporte de cobertura"
        echo "  parallel     - Ejecución paralela"
        echo "  unit         - Solo tests unitarios"
        echo "  integration  - Solo tests de integración"
        echo "  e2e          - Solo tests end-to-end"
        exit 1
        ;;
esac

echo ""
echo -e "${BLUE}Ejecutando tests...${NC}"
echo ""

# Ejecutar pytest
pytest testers/test_commissions/ $PYTEST_ARGS

# Resultado
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  ✅ TESTS COMPLETADOS EXITOSAMENTE    ${NC}"
    echo -e "${GREEN}========================================${NC}"

    # Si se generó coverage, mostrar ubicación
    if [ "$TEST_MODE" = "coverage" ]; then
        echo ""
        echo -e "${YELLOW}Reporte de cobertura generado en:${NC}"
        echo "  htmlcov/index.html"
        echo ""
        echo -e "${YELLOW}Para ver el reporte:${NC}"
        echo "  open htmlcov/index.html"
    fi
else
    echo ""
    echo -e "${RED}========================================${NC}"
    echo -e "${RED}  ❌ TESTS FALLARON                     ${NC}"
    echo -e "${RED}========================================${NC}"
    exit 1
fi
