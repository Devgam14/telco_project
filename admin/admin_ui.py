import os
import platform
from prettytable import PrettyTable
from admin.admin_services import Admin_services

class Utils:
    @staticmethod
    def clear_screen():
        """Wipes the terminal screen based on the OS."""
        if platform.system() == "Windows":
            os.system('cls')
        else:
            os.system('clear')

    @staticmethod
    def header(value : str):
        """A stylish header for the Admin Panel."""
        print("="*50)
        print(f"       🚀 DATA VEND - {value}       ")
        print("="*50)

class AdminUI:
    def __init__(self, admin_name):
        self.admin_name = admin_name

    def main_menu(self):
        while True:
            Utils.clear_screen()
            Utils.header("ADMIN CONTROL PANEL")
            print(f"Logged in as: {self.admin_name} (Admin)")
            print("-" * 50)
            
            # --- Menu Options ---
            print("1. 📊 View Transactions & Revenue")
            print("2. 🔍 Search Transactions (Filter)")
            print("3. 📦 Manage Bundles (View/Add/Toggle)")
            print("4. 📝 Edit Bundle Details (Factory)")
            print("5. 👥 User Management (View/Count)")
            print("6. 💰 Manual Wallet Deposit")
            print("7. 🗑️  Delete Records")
            print("0. 🚪 Logout")
            print("-" * 50)
            
            choice = input("Select an option: ")

            if choice == "1":
                Admin_services.view_transaction()
                Admin_services.view_transaction_count()
            
            elif choice == "2":
                phone = input("Enter Phone (or leave blank): ")
                status = input("Enter Status (success/failed/pending): ")
                Admin_services.search_transactions(phone or None, status or None)
            
            elif choice == "3":
                self.bundle_submenu()
                
            elif choice == "4":
                bid = int(input("Enter Bundle ID: "))
                field = input("Field to change (price/name/size_mb): ")
                val = input("Enter new value: ")
                # Convert to float/int if necessary
                if field in ['price', 'size_mb']: val = float(val)
                Admin_services.edit_bundle_factory(bid, **{field: val})

            elif choice == "5":
                Admin_services.view_users()
                Admin_services.users_count()

            elif choice == "6":
                phone = input("User Phone Number: ")
                amt = input("Amount to deposit: ₦")
                Admin_services.manual_deposit(phone, amt)

            elif choice == "7":
                tbl = input("Table (user/bundle): ")
                rid = int(input("Record ID: "))
                Admin_services.delete_record(tbl, rid)

            elif choice == "0":
                print("Logging out...")
                break
            
            input("\nPress Enter to return to menu...")

    def bundle_submenu(self):
        """Sub-navigation for Bundle management to keep the UI clean."""
        Utils.clear_screen()
        print("--- BUNDLE MANAGEMENT ---")
        print("a. View All Bundles")
        print("b. Add New Bundle")
        print("c. Toggle Active Status")
        sub_choice = input("Select: ").lower()

        if sub_choice == "a":
            Admin_services.view_bundles()
        elif sub_choice == "b":
            name = input("Name: ")
            size = int(input("Size (MB): "))
            dur = input("Duration (daily/weekly/monthly): ")
            price = int(input("Price: ₦"))
            Admin_services.add_bundles(name, size, dur, price, True)
        elif sub_choice == "c":
            name = input("Enter Bundle Name to Toggle: ")
            Admin_services.toggle_by_name(name)