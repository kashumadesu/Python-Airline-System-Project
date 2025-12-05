from db_config import get_db_connection, clear_screen, pause

def menu():
    while True:
        clear_screen()
        print("--- [G3] CHECK-IN COUNTER ---")
        print("1. Perform Check-in")
        print("0. Back to Main Menu")
        choice = input("\nSelect: ")

        if choice == '1':
            perform_checkin()
            pause()
        elif choice == '0':
            break

def perform_checkin():
    pnr = input("\nEnter Booking Reference (PNR): ").upper()
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = """
        SELECT b.booking_id, b.seat_number, b.seat_class, f.flight_number, f.destination, f.origin, p.name 
        FROM bookings b
        JOIN flights f ON b.flight_id = f.flight_id
        JOIN passengers p ON b.passenger_id = p.passenger_id
        WHERE b.pnr = %s AND b.status = 'Confirmed'
    """
    cursor.execute(query, (pnr,))
    res = cursor.fetchone()
    
    if not res:
        print("[!] Booking not found or cancelled.")
        conn.close()
        return
        
    bags = input("Number of bags to check-in: ")
    
    try:
        cursor.execute("INSERT INTO checkin (booking_id, bags_checked) VALUES (%s, %s)", (res['booking_id'], bags))
        conn.commit()
        
        print("\n" + "="*40)
        print(f"       BOARDING PASS - {res['seat_class'].upper()}")
        print("="*40)
        print(f" PASSENGER: {res['name']}")
        print(f" FLIGHT:    {res['flight_number']}")
        print(f" ROUTE:     {res['origin']} -> {res['destination']}")
        print(f" SEAT:      {res['seat_number']}")
        print(f" BAGS:      {bags}")
        print("="*40 + "\n")
        
    except:
        print("[!] Passenger already checked in.")
    conn.close()