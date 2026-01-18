#!/usr/bin/env python3
"""Verificar estado actual de la BD"""
import sys
sys.path.insert(0, '.')

import reflex as rx
from sqlmodel import select, func
from database.users import Users

with rx.session() as session:
    total = session.exec(select(func.count(Users.id))).one()
    masters = session.exec(
        select(func.count(Users.id))
        .where(Users.sponsor_id.is_(None))
    ).one()
    
    print(f"Total usuarios: {total}")
    print(f"Cuentas master: {masters}")
