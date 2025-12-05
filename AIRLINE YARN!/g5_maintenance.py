from db_config import get_db_connection, clear_screen, pause, get_valid_input

def menu():
    while True:
        clear_screen()
        print("--- [G5] AIRCRAFT MAINTENANCE ---")
        print("1. View Fleet Status")
        print("2. Update Aircraft Status")
        print("3. Add New Aircraft")
        print("0. Back to Main Menu")
        choice = input("\nSelect: ")

        if choice == '1': view_fleet(); pause()
        elif choice == '2': update_status(); pause()
        elif choice == '3': add_aircraft(); pause()
        elif choice == '0': break

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
    aid = get_valid_input("\nEnter Aircraft ID to modify: ", int)
    new_status = get_valid_input("Set Status (Active/In-Maintenance): ").title()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE aircrafts SET status = %s WHERE aircraft_id = %s", (new_status, aid))
    conn.commit()
    print(f"\n[UPDATED] Aircraft {aid} is now {new_status}.")
    
    if new_status == 'In-Maintenance':
        print("[ALERT] G1 Flight Module has been notified. This plane cannot be scheduled.")
    conn.close()

def add_aircraft():
    conn = get_db_connection()
    cursor = conn.cursor()
    print("\n--- ACQUIRE NEW AIRCRAFT ---")
    model = get_valid_input("Enter Aircraft Model (e.g. Boeing 777): ")
    
    try:
        cursor.execute("INSERT INTO aircrafts (model, status) VALUES (%s, 'Active')", (model,))
        conn.commit()
        print(f"\n[SUCCESS] {model} added to fleet.")
    except Exception as e:
        print(f"[ERROR] {e}")
    conn.close()