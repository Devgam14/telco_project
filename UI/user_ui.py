from admin.admin_ui import Utils
from admin.admin_services import Admin_services
from models.db import db
from prettytable import PrettyTable
from datetime import datetime

class UserUI:
    def __init__(self, user_phone):
        self.user_phone = user_phone
        # Fetch the user's current record from the DB
        self.user = db(db.user.phone_number == user_phone).select().first()

    def refresh_user_data(self):
        """Syncs the local user object with the database (important for balance)."""
        self.user = db(db.user.phone_number == self.user_phone).select().first()

    def user_menu(self):
        """The main dashboard for the customer."""
        while True:
            self.refresh_user_data()
            Utils.clear_screen()
            Utils.header("User Dashboard")
            
            print(f"👤 Welcome, {self.user.username} | 📱 {self.user_phone}")
            print(f"💰 Wallet Balance: ₦{self.user.wallet_balance:,.2f}")
            print("-" * 50)
            
            print("1. 🛒 Buy Data Bundle")
            print("2. 💳 Fund My Wallet (Deposit)")
            print("3. 📜 My Transaction History")
            print("4. 👤 View My Profile")
            print("0. 🚪 Logout")
            print("-" * 50)

            choice = input("Select an option: ")

            if choice == "1":
                self.purchase_bundle_flow()
            elif choice == "2":
                self.deposit_flow()
            elif choice == "3":
                self.view_history()
            elif choice == "4":
                self.view_profile()
            elif choice == "0":
                print("\nLogging out... Stay connected! 🚀")
                break
            else:
                print("❌ Invalid selection.")
                import time
                time.sleep(1)

    def purchase_bundle_flow(self):
        """Handles viewing active bundles and processing the sale."""
        Utils.clear_screen()
        print("--- 📱 AVAILABLE DATA BUNDLES ---")
        # Reuse admin's view_bundles to show the table
        Admin_services.view_bundles()
        
        bundle_id = input("\nEnter Bundle ID to purchase (or 'q' to cancel): ")
        if bundle_id.lower() == 'q': return

        try:
            bundle = db.bundle(int(bundle_id))
            if not bundle or not bundle.is_active:
                print("❌ This bundle is currently unavailable.")
            elif self.user.wallet_balance < bundle.price:
                print(f"❌ Insufficient Balance! You need ₦{bundle.price - self.user.wallet_balance:,.2f} more.")
            else:
                # 1. Update User Balance
                new_balance = self.user.wallet_balance - bundle.price
                db(db.user.phone_number == self.user_phone).update(wallet_balance=new_balance)
                
                # 2. Record the Transaction
                db.transaction.insert(
                    order_id=f"DATA-{bundle.id}-{int(datetime.now().timestamp())}",
                    user_phone=self.user_phone,
                    amount=bundle.price,
                    payment_method="wallet",
                    status="success"
                )
                db.commit()
                print(f"\n✅ Success! You have purchased {bundle.name}.")
                print(f"New Balance: ₦{new_balance:,.2f}")
        except ValueError:
            print("❌ Please enter a valid ID number.")
        
        input("\nPress Enter to return...")

    def deposit_flow(self):
        """The 'Self-Funding' privilege requested."""
        Utils.clear_screen()
        print("--- 💳 TOP-UP WALLET ---")
        try:
            user_input = input("Enter amount to deposit: ₦")
            amount = float(user_input) # Use float so they can enter 450.50
            
            if amount <= 0:
                print("❌ Invalid amount.")
            else:
                # Use .get() or a fallback to 0 if the current balance is None
                current_balance = self.user.wallet_balance or 0.0
                new_balance = current_balance + amount
                
                # 1. Update using the CORRECT field name: wallet_balance
                db(db.user.phone_number == self.user_phone).update(wallet_balance=new_balance)
                
                # 2. Log the transaction
                db.transaction.insert(
                    order_id=f"DEP-{int(datetime.now().timestamp())}",
                    user_phone=self.user_phone,
                    amount=amount,
                    payment_method="deposit",
                    status="success"
                )
                
                db.commit()
                
                # 3. IMPORTANT: Update the local object so the UI shows the new balance immediately
                self.user.wallet_balance = new_balance
            
                print(f"\n✅ Wallet Funded! New Balance: ₦{new_balance:,.2f}")

        except ValueError:
            print("❌ Invalid input. Please enter a valid number (e.g., 500).")
        except Exception as e:
            print(f"❌ Database Error: {e}") # This helps you see if it's a DB issue vs an Input issue
            
        input("\nPress Enter to return...")

    def view_history(self):
        """Restricted history view - user only sees their own phone data."""
        Utils.clear_screen()
        print(f"--- 📜 TRANSACTION HISTORY ({self.user_phone}) ---")
        # Reuse admin's search method but hard-code the phone number for safety
        Admin_services.search_transactions(phone_number=self.user_phone)
        input("\nPress Enter to return...")

    def view_profile(self):
        Utils.clear_screen()
        print("--- 👤 MY PROFILE ---")
        table = PrettyTable(["Field", "Detail"])
        table.add_row(["Full Name", self.user.username])
        table.add_row(["Phone Number", self.user.phone_number])
        table.add_row(["Account Type", self.user.role.upper()])
        table.add_row(["Joined Date", self.user.created_at.strftime("%d %b %Y")])
        print(table)
        input("\nPress Enter to return...")