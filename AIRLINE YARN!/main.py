import sys
from db_config import clear_screen, pause
import g1_flights
import g2_reservations
import g3_checkin
import g4_crew
import g5_maintenance
import g6_customer
import admin_panel

def main_menu():
    while True:
        clear_screen()
        print("="*50)
        print("   AIRLINE MANAGEMENT SYSTEM (ENTERPRISE EDITION)")
        print("="*50)
        print("1. [G1] Flight Operations")
        print("2. [G2] Reservation & Ticketing")
        print("3. [G3] Check-in & Boarding")
        print("4. [G4] Crew Management")
        print("5. [G5] Maintenance & Engineering")
        print("6. [G6] Customer Loyalty (CRM)")
        # Option 7 is hidden (Secret Admin Mode)
        print("0. Exit Application")
        
        choice = input("\nSelect Module: ")
        
        if choice == '1': g1_flights.menu()
        elif choice == '2': g2_reservations.menu()
        elif choice == '3': g3_checkin.menu()
        elif choice == '4': g4_crew.menu()
        elif choice == '5': g5_maintenance.menu()
        elif choice == '6': g6_customer.menu()
        elif choice == '7': admin_panel.menu() 
        elif choice == '0': 
            print("System Shutdown..."); sys.exit()
        else:
            print("[!] Invalid Selection")
            pause()

if __name__ == "__main__":
    main_menu()
