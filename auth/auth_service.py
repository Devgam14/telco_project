import hashlib
from models.db import db
from datetime import datetime
from admin.admin_ui import AdminUI, Utils # Added Utils import
from UI.user_ui import UserUI

class Auth:
    def __init__(self):
        self.db = db

    def _hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def register(self):
        Utils.clear_screen()
        Utils.header("CREATE NEW ACCOUNT")
        
        username = input("Username: ")
        password = input("Password: ")
        phone = input("Phone Number: ")
        email = input("Email (Optional): ")
        
        hashed_pw = self._hash_password(password)
        
        try:
            self.db.user.insert(
                username=username,
                password=hashed_pw,
                phone_number=phone,
                email=email,
                role="customer",
                wallet_balance=0.0,
                mb=0.0,
                created_at=datetime.now()
            )
            self.db.commit()
            print("\n✅ Registration successful! Please log in.")
            input("\nPress Enter to continue...")
        except Exception as e:
            self.db.rollback()
            print(f"\n❌ Error: {e}")
            input("\nPress Enter to return...")

    def login(self):
        Utils.clear_screen()
        Utils.header("USER LOGIN")
        
        phone = input("Phone Number: ")
        password = input("Password: ")
        
        hashed_pw = self._hash_password(password)
        
        user = self.db((self.db.user.phone_number == phone) & 
                       (self.db.user.password == hashed_pw)).select().first()
        
        if user:
            print(f"\n✅ Login successful! Welcome {user.username}.")
            import time
            time.sleep(1) # Short pause so they see the success message
            
            if user.role == "admin":
                return AdminUI(user.username)
            else:
                return UserUI(user.phone_number)
        else:
            print("\n❌ Invalid phone number or password.")
            input("\nPress Enter to try again...")
            return None

    def start(self):
        while True:
            Utils.clear_screen()
            Utils.header("TELCO DATA HUB")
            print("1. 🔑 Login")
            print("2. 📝 Register")
            print("0. 🚪 Exit")
            print("-" * 30)
            
            choice = input("Select an option: ")

            if choice == "1":
                ui_instance = self.login()
                if ui_instance:
                    return ui_instance 
            elif choice == "2":
                self.register()
            elif choice == "0":
                Utils.clear_screen()
                print("Goodbye! 👋")
                exit()
            else:
                print("\n❌ Invalid choice.")
                import time
                time.sleep(1)