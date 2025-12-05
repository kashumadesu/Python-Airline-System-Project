from db_config import get_db_connection, clear_screen, pause, get_valid_input, OperationCancelled
import random
import string
import time

def menu():
    while True:
        clear_screen()
        print("--- [G2] RESERVATION SYSTEM ---")
        print("1. Book a Ticket")
        print("2. View My Bookings")
        print("3. Cancel a Booking") 
        print("0. Back to Main Menu")
        choice = input("\nSelect: ")
        
        if choice == '1': book_ticket(); pause()
        elif choice == '2': view_my_bookings(); pause()
        elif choice == '3': cancel_booking(); pause()
        elif choice == '0': break

def show_seat_map(conn, flight_id):
    """
    Displays a realistic 20-Row Aircraft Layout.
    Returns a list of ALL valid seat codes to ensure user input is correct.
    """
    print("\n" + "="*20 + " SEAT MAP " + "="*20)
    print("      [A] [B] [C]    [D] [E] [F]") # Layout Header
    
    # Get taken seats
    cursor = conn.cursor()
    cursor.execute("SELECT seat_number FROM bookings WHERE flight_id = %s AND status = 'Confirmed'", (flight_id,))
    taken = [row[0] for row in cursor.fetchall()] 
    
    # Define Plane Size (Realism Upgrade)
    rows = 20
    cols = ['A', 'B', 'C', 'D', 'E', 'F']
    valid_seat_codes = [] # We will store every possible seat here (e.g. 1A, 1B... 20F)
    
    for r in range(1, rows + 1):
        # Format row number (e.g. " 1" or "10")
        row_str = f"{r:<2}" 
        line = f"Row {row_str}| "
        
        for i, c in enumerate(cols):
            seat_code = f"{r}{c}"
            valid_seat_codes.append(seat_code) # Add to valid list
            
            # Visual logic
            if seat_code in taken:
                marker = "[X]" # Taken
            else:
                marker = "[ ]" # Available
            
            line += f"{marker} "
            
            # Add an aisle after column C
            if i == 2: 
                line += "   " 
        
        print(line)
        
    print("="*50)
    print("Legend: [ ] = Available, [X] = Taken")
    return taken, valid_seat_codes

def book_ticket():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # 1. Identify Passenger
        email = get_valid_input("\nEnter Passenger Email")
        cursor.execute("SELECT * FROM passengers WHERE email = %s", (email,))
        p = cursor.fetchone()
        
        if p:
            print(f"Welcome back, {p['name']} (Tier: {p['tier']})")
            pid = p['passenger_id']
        else:
            print("New Passenger Detected.")
            name = get_valid_input("Full Name")
            cursor.execute("INSERT INTO passengers (name, email) VALUES (%s, %s)", (name, email))
            conn.commit()
            pid = cursor.lastrowid

        # 2. Select Flight
        cursor.execute("SELECT flight_id, flight_number, destination, flight_date FROM flights WHERE status='Scheduled'")
        flights = cursor.fetchall()
        print("\n--- AVAILABLE FLIGHTS ---")
        for f in flights: print(f"ID {f['flight_id']} | {f['flight_number']} to {f['destination']} on {f['flight_date']}")
        
        fid = get_valid_input("\nEnter Flight ID", int)
        
        # 3. SEAT SELECTION (With Strict Validation)
        # We now get 'valid_codes' from the map function
        taken_seats, valid_codes = show_seat_map(conn, fid)
        
        while True:
            seat = get_valid_input("Select Seat (e.g. 10A)").upper()
            
            # VALIDATION 1: Does the seat exist on this plane?
            if seat not in valid_codes:
                print(f"   [!] Error: Seat '{seat}' does not exist. Please look at the map.")
                continue
                
            # VALIDATION 2: Is it taken?
            if seat in taken_seats:
                print(f"   [!] Error: Seat '{seat}' is already occupied.")
                continue
                
            break # Input is valid and available
        
        seat_class = get_valid_input("Class (Economy/Business)").title()
        price = 5000 if "Econ" in seat_class else 15000
        
        # 4. PAYMENT SIMULATION 
        print(f"\n" + "="*40)
        print(f"   SECURE PAYMENT GATEWAY (₱{price:,.2f})")
        print("="*40)
        
        while True:
            card = get_valid_input("Enter Credit Card Number (16 digits)")
            if len(card) == 16 and card.isdigit():
                break
            print("   [!] Declined: Invalid Card Format.")

        cvv = get_valid_input("Enter CVV")
        
        print("\nContacting Bank...", end="", flush=True)
        time.sleep(1)
        print(" Authorized.")
        print(f"[SUCCESS] Payment of ₱{price} Received.")
        print("="*40)

        # 5. Finalize Booking
        pnr = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        
        cursor.execute("""
            INSERT INTO bookings (pnr, flight_id, passenger_id, seat_class, seat_number, price, status) 
            VALUES (%s, %s, %s, %s, %s, %s, 'Confirmed')
        """, (pnr, fid, pid, seat_class, seat, price))
        
        points = int(price * 0.10)
        cursor.execute("UPDATE passengers SET loyalty_points = loyalty_points + %s WHERE passenger_id = %s", (points, pid))
        
        conn.commit()
        print(f"\n[SYSTEM] Ticket Issued.")
        print(f"PNR: {pnr} | Loyalty Points Earned: +{points}")
        
    except OperationCancelled:
        print("\n[!] Booking Process Cancelled.")
    except Exception as e:
        print(f"[ERROR] Booking Failed: {e}")
    finally:
        conn.close()

def view_my_bookings():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        email = get_valid_input("\nEnter your Email to view bookings")
        
        query = """
            SELECT b.pnr, f.flight_number, f.origin, f.destination, f.flight_date, b.seat_number, b.status
            FROM bookings b
            JOIN passengers p ON b.passenger_id = p.passenger_id
            JOIN flights f ON b.flight_id = f.flight_id
            WHERE p.email = %s
        """
        cursor.execute(query, (email,))
        bookings = cursor.fetchall()
        
        if not bookings:
            print("\n[!] No bookings found for this email.")
        else:
            print(f"\n--- BOOKINGS FOR {email} ---")
            print(f"{'PNR':<8} {'FLIGHT':<8} {'ROUTE':<20} {'DATE':<12} {'SEAT':<6} {'STATUS'}")
            print("-" * 70)
            for b in bookings:
                print(f"{b['pnr']:<8} {b['flight_number']:<8} {b['origin']}->{b['destination']:<16} {str(b['flight_date']):<12} {b['seat_number']:<6} {b['status']}")
        
    except OperationCancelled:
        print("\n[!] Cancelled.")
    finally:
        conn.close()

def cancel_booking():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        pnr = get_valid_input("\nEnter PNR to Cancel").upper()
        
        cursor.execute("SELECT * FROM bookings WHERE pnr = %s", (pnr,))
        booking = cursor.fetchone()
        
        if not booking:
            print(f"\n[!] Error: Booking {pnr} not found.")
            return

        if booking['status'] == 'Cancelled':
            print(f"\n[!] Booking {pnr} is already cancelled.")
            return
            
        confirm = get_valid_input(f"Are you sure you want to cancel PNR {pnr}? (Y/N)").upper()
        if confirm != 'Y':
            print("\n[!] Cancellation aborted.")
            return
            
        cursor.execute("UPDATE bookings SET status = 'Cancelled' WHERE pnr = %s", (pnr,))
        conn.commit()
        print(f"\n[SUCCESS] Booking {pnr} has been CANCELLED.")
        
    except OperationCancelled:
        print("\n[!] Cancelled.")
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        conn.close()
