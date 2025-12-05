from db_config import get_db_connection, clear_screen, pause

def menu():
    while True:
        clear_screen()
        print("--- [G6] CUSTOMER LOYALTY DATABASE ---")
        print("1. View Top Customers")
        print("0. Back to Main Menu")
        choice = input("\nSelect: ")
        
        if choice == '1': view_customers(); pause()
        elif choice == '0': break

def view_customers():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Update tiers automatically before showing
    cursor.execute("UPDATE passengers SET tier = 'Gold' WHERE loyalty_points > 10000")
    cursor.execute("UPDATE passengers SET tier = 'Silver' WHERE loyalty_points BETWEEN 5000 AND 10000")
    conn.commit()
    
    cursor.execute("SELECT * FROM passengers ORDER BY loyalty_points DESC")
    print(f"\n{'ID':<5} {'NAME':<20} {'POINTS':<10} {'TIER'}")
    print("-" * 50)
    for p in cursor.fetchall():
        print(f"{p['passenger_id']:<5} {p['name']:<20} {p['loyalty_points']:<10} {p['tier']}")
        
    conn.close()