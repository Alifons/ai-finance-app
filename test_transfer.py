import sqlite3
import os

DATABASE = 'finance.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def test_transfer_exclusion():
    conn = get_db()
    c = conn.cursor()
    
    print("=== TEST EXCLUDERE TRANSFERURI ===")
    
    # Test 1: Toate veniturile (inclusiv transferuri)
    print("\n1. Toate veniturile (inclusiv transferuri):")
    venituri_cu_transfer = c.execute("SELECT operator, SUM(suma) as total FROM tranzactii WHERE tip='venit' GROUP BY operator").fetchall()
    for v in venituri_cu_transfer:
        print(f"  {v['operator']}: {v['total']} lei")
    
    # Test 2: Venituri fără transferuri
    print("\n2. Venituri fără transferuri:")
    venituri_fara_transfer = c.execute("SELECT operator, SUM(suma) as total FROM tranzactii WHERE tip='venit' AND obiect != 'transfer' GROUP BY operator").fetchall()
    for v in venituri_fara_transfer:
        print(f"  {v['operator']}: {v['total']} lei")
    
    # Test 3: Transferuri separate
    print("\n3. Transferuri separate:")
    transferuri = c.execute("SELECT operator, tip, suma, comentariu FROM tranzactii WHERE obiect = 'transfer' ORDER BY data DESC").fetchall()
    for t in transferuri:
        print(f"  {t['operator']} ({t['tip']}): {t['suma']} lei - {t['comentariu']}")
    
    # Test 4: Comparație
    print("\n4. Comparație:")
    for v_cu in venituri_cu_transfer:
        operator = v_cu['operator']
        total_cu = v_cu['total']
        
        # Găsește veniturile fără transfer pentru acest operator
        v_fara = next((v for v in venituri_fara_transfer if v['operator'] == operator), None)
        total_fara = v_fara['total'] if v_fara else 0
        
        # Calculează transferurile pentru acest operator
        transferuri_op = c.execute("SELECT SUM(suma) as total FROM tranzactii WHERE operator = ? AND obiect = 'transfer' AND tip = 'venit'", (operator,)).fetchone()
        transferuri_venit = transferuri_op['total'] if transferuri_op['total'] else 0
        
        print(f"  {operator}:")
        print(f"    Total cu transferuri: {total_cu} lei")
        print(f"    Total fără transferuri: {total_fara} lei")
        print(f"    Transferuri (venit): {transferuri_venit} lei")
        print(f"    Diferența: {total_cu - total_fara} lei")
    
    conn.close()

if __name__ == "__main__":
    test_transfer_exclusion() 