from db_config import get_db_connection, clear_screen, pause

def menu():
    while True:
        clear_screen()
        print("--- [G5] AIRCRAFT MAINTENANCE ---")
        print("1. View Fleet Status")
        print("2. Update Aircraft Status")
        print("0. Back to Main Menu")
        choice = input("\nSelect: ")

        if choice == '1':
            view_fleet()
            pause()
        elif choice == '2':
            update_status()
            pause()
        elif choice == '0':
            break

def view_fleet():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM aircrafts")
    print(f"\n{'ID':<5} {'MODEL':<20} {'STATUS'}")
    print("-" * 40)
    for a in cursor.fetchall():
        print(f"{a['aircraft_id']:<5} {a['model']:<20} {a['status']}")
    conn.close()

def update_status():
    view_fleet()
    aid = input("\nEnter Aircraft ID to modify: ")
    new_status = input("Set Status (Active/In-Maintenance): ")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE aircrafts SET status = %s WHERE aircraft_id = %s", (new_status, aid))
    conn.commit()
    print(f"\n[UPDATED] Aircraft {aid} is now {new_status}.")
    
    if new_status == 'In-Maintenance':
        print("[ALERT] G1 Flight Module has been notified. This plane cannot be scheduled.")
    conn.close()