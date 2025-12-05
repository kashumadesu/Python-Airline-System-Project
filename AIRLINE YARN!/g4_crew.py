from db_config import get_db_connection, clear_screen, pause

def menu():
    while True:
        clear_screen()
        print("--- [G4] CREW MANAGEMENT ---")
        print("1. View Crew Roster")
        print("0. Back to Main Menu")
        choice = input("\nSelect: ")
        
        if choice == '1':
            view_crew()
            pause()
        elif choice == '0':
            break

def view_crew():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM crew")
    print("\n--- CREW ROSTER ---")
    for c in cursor.fetchall():
        print(f"ID {c['crew_id']}: {c['name']} ({c['role']}) - {c['status']}")
    conn.close()