from db_config import get_db_connection, clear_screen, pause, get_valid_input, OperationCancelled

def menu():
    while True:
        clear_screen()
        print("--- [G3] CHECK-IN COUNTER ---")
        print("1. Perform Check-in")
        print("0. Back to Main Menu")
        choice = input("\nSelect: ")

        if choice == '1': perform_checkin(); pause()
        elif choice == '0': break

def perform_checkin():
    try:
        # 1. GET AND VALIDATE PNR
        pnr = get_valid_input("\nEnter Booking Reference (PNR)").upper()
        if not pnr or len(pnr) != 6 or not pnr.isalnum():
            print("[!] Invalid PNR format. Must be 6 alphanumeric characters.")
            return

        # 2. CONNECT TO DATABASE
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # 3. FETCH CONFIRMED BOOKING
        query = """
            SELECT b.booking_id, b.seat_number, b.seat_class,
                   f.flight_number, f.destination, f.origin, f.gate,
                   p.name 
            FROM bookings b
            JOIN flights f ON b.flight_id = f.flight_id
            JOIN passengers p ON b.passenger_id = p.passenger_id
            WHERE b.pnr = %s AND b.status = 'Confirmed'
        """
        cursor.execute(query, (pnr,))
        booking = cursor.fetchone()

        if not booking:
            print("[!] Booking not found or not confirmed.")
            conn.close()
            return

        # 4. CHECK IF ALREADY CHECKED-IN
        cursor.execute(
            "SELECT checkin_id FROM checkin WHERE booking_id = %s",
            (booking['booking_id'],)
        )
        if cursor.fetchone():
            print("[!] Passenger already checked in.")
            conn.close()
            return

        # 5. GET NUMBER OF BAGS
        while True: 
            try:
                bags = int(get_valid_input("Number of bags to check-in"))
                if 0 <= bags <= 3:
                    break
                print("[!] Oops! You can only check in up to 3 bags. Please try again.")
            except ValueError:
                print("[!] Please enter a valid number.")

        # 6. INSERT CHECK-IN RECORD (NOW SAVES STATUS)
        cursor.execute(
            "INSERT INTO checkin (booking_id, bags_checked, status) VALUES (%s, %s, 'Checked-In')",
            (booking['booking_id'], bags)
        )
        conn.commit()

        # 7. DISPLAY BOARDING PASS
        gate_display = booking['gate'] if booking['gate'] else "TBA"

        print("\n" + "=" * 40)
        print(f"       BOARDING PASS - {booking['seat_class'].upper()}")
        print("=" * 40)
        print(f" PASSENGER: {booking['name']}")
        print(f" FLIGHT:    {booking['flight_number']}")
        print(f" ROUTE:     {booking['origin']} -> {booking['destination']}")
        print(f" GATE:      {gate_display}")
        print(f" SEAT:      {booking['seat_number']}")
        print(f" BAGS:      {bags}")
        print(f" STATUS:    Checked-In") 
        print("=" * 40 + "\n")

    except OperationCancelled:
        print("\n[!] Check-in Cancelled.")

    except Exception as e:
        print(f"[!] Error during check-in: {e}")

    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()
