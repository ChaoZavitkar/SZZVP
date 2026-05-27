#!/usr/bin/env python
"""Vyčisti Connection nody"""
import sys
sys.path.insert(0, '/code')

from app import app

with app.app_context():
    from models.database import get_db
    
    db = get_db()
    
    # Smaž všechny Connection nody a vazby
    print("Mažu Connection nody...")
    db.execute('MATCH (c:Connection) DETACH DELETE c')
    
    # Smaž všechny LIKES vazby (reset)
    print("Mažu LIKES vazby...")
    db.execute('MATCH (u:User)-[r:LIKES]->(u2:User) DELETE r')
    
    print("✅ Databáze vyčištěna")
