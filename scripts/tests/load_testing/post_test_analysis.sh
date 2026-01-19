#!/bin/bash

echo "📊 POST-TEST ANALYSIS"
echo "===================="

# 1. Verificar integridad de datos
echo ""
echo "🔍 Verificando integridad de datos..."

python3 << 'EOF'
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import sqlmodel
from dotenv import load_dotenv
load_dotenv('.env.staging')

from NNProtect_new_website.utils.environment import Environment
from database.wallet import Wallets, WalletTransactions

engine = sqlmodel.create_engine(Environment.get_database_url(), echo=False)

with sqlmodel.Session(engine) as session:
    # Verificar que balance = balance_after de última transacción
    wallets = session.exec(
        sqlmodel.select(Wallets).where(
            Wallets.member_id >= 80000,
            Wallets.member_id <= 80199
        )
    ).all()

    errors = 0
    for wallet in wallets:
        last_tx = session.exec(
            sqlmodel.select(WalletTransactions)
            .where(WalletTransactions.member_id == wallet.member_id)
            .order_by(sqlmodel.desc(WalletTransactions.created_at))
        ).first()

        if last_tx and abs(wallet.balance - last_tx.balance_after) > 0.01:
            print(f"❌ Corrupción en wallet {wallet.id}: balance={wallet.balance:.2f}, esperado={last_tx.balance_after:.2f}")
            errors += 1

    if errors == 0:
        print("✅ INTEGRIDAD DE DATOS: OK - Todos los balances coinciden")
    else:
        print(f"❌ ERRORES DE INTEGRIDAD: {errors} wallets con discrepancias")
EOF

# 2. Contar race conditions
echo ""
echo "🔍 Buscando race conditions en reportes..."
if [ -f reports/*.log ]; then
    race_conditions=$(grep -r "ya fue procesada" reports/*.log 2>/dev/null | wc -l)
    echo "⚠️  Race conditions detectadas: $race_conditions"
else
    echo "ℹ️  No se encontraron logs para analizar"
fi

# 3. Verificar reportes HTML generados
echo ""
echo "📄 Reportes generados:"
ls -lh reports/*.html 2>/dev/null || echo "ℹ️  No se encontraron reportes HTML"

echo ""
echo "✅ ANÁLISIS COMPLETADO"
echo "====================="
echo ""
echo "Revisa los reportes en el directorio reports/ para ver métricas detalladas"
