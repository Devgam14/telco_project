from admin.admin_ui import Utils
from admin.admin_services import Admin_services
from models.db import db
from prettytable import PrettyTable
from datetime import datetime

class UserUI:
    def __init__(self, user_phone):
        self.user_phone = user_phone
        self.user = db(db.user.phone_number == user_phone).select().first()

    def refresh_user_data(self):
        """Syncs the local user object with the database."""
        self.user = db(db.user.phone_number == self.user_phone).select().first()
    def view_bundles(self):
        table = PrettyTable()
        table.field_names = ["ID", "Name", "Size (MB)", "Duration", "Price", "Active"]
        
        # --- FILTER ADDED HERE ---
        # Only select rows where is_active is True
        rows = db(db.bundle.is_active == True).select()
        
        for r in rows:
            table.add_row([
                r.id, 
                r.name, 
                r.size_mb, 
                r.duration_type, 
                f"₦{r.price:,.2f}", 
                "✅" if r.is_active else "❌"
            ])
        print(table)
    def user_menu(self):
        while True:
            self.refresh_user_data()
            Utils.clear_screen()
            Utils.header("User Dashboard")
            
            # Updated Header to show both Naira and Data MB
            print(f"👤 Welcome, {self.user.username} | 📱 {self.user_phone}")
            print(f"💰 Wallet: ₦{self.user.wallet_balance:,.2f} | 📶 Data: {self.user.mb or 0} MB")
            print("-" * 50)
            
            print("1. 🛒 Buy Data Bundle")
            print("2. 💳 Fund My Wallet")
            print("3. 📲 Share Data")
            print("4. 📜 Transaction History")
            print("5. 👤 My Profile / Balance")
            print("0. 🚪 Logout")
            print("-" * 50)

            choice = input("Select an option: ")

            if choice == "1":
                self.purchase_bundle_flow()
            elif choice == "2":
                self.deposit_flow()
            elif choice == "3":
                self.share_data_flow()
            elif choice == "4":
                self.view_history()
            elif choice == "5":
                self.view_profile()
            elif choice == "0":
                break
    def view_history(self):
        """Displays a table of all transactions related to this user's phone number."""
        Utils.clear_screen()
        Utils.header(f"📜 TRANSACTION HISTORY ({self.user_phone})")
        
        # 1. Fetch transactions for this specific user
        transactions = db(db.transaction.user_phone == self.user_phone).select(orderby=~db.transaction.id)

        if not transactions:
            print("\n📭 No transactions found yet. Start shopping! 🛒")
        else:
            # 2. Setup the PrettyTable
            table = PrettyTable()
            table.field_names = ["Date", "Order ID", "Amount", "Method", "Status"]
            
            # 3. Populate rows
            for tx in transactions:
                # Format the date if your table has a created_at field, otherwise use a placeholder
                date_str = tx.created_on.strftime("%Y-%m-%d %H:%M") if hasattr(tx, 'created_on') else "N/A"
                
                table.add_row([
                    date_str,
                    tx.order_id,
                    f"₦{tx.amount:,.2f}",
                    tx.payment_method.capitalize(),
                    "✅ Success" if tx.status == "success" else "❌ Failed"
                ])
            
            print(table)
            print(f"\nTotal Transactions: {len(transactions)}")

        input("\nPress Enter to return to menu...")
    def purchase_bundle_flow(self):
        """Purchases data and adds MB to the user's account."""
        Utils.clear_screen()
        self.view_bundles()
        
        bundle_id = input("\nEnter Bundle ID to purchase (or 'q' to cancel): ")
        if bundle_id.lower() == 'q': return

        try:
            bundle = db.bundle(int(bundle_id))
            if not bundle or not bundle.is_active:
                print("❌ Bundle unavailable.")
            elif self.user.wallet_balance < bundle.price:
                print(f"❌ Insufficient Balance!")
            else:
                # 1. Calculate new totals (Using .size_mb based on your table)
                new_wallet = self.user.wallet_balance - bundle.price
                new_data = (self.user.mb or 0) + bundle.size_mb 

                # 2. Update Database
                db(db.user.phone_number == self.user_phone).update(
                    wallet_balance=new_wallet,
                    mb=new_data
                )
                
                # 3. Record Transaction
                db.transaction.insert(
                    order_id=f"DATA-{int(datetime.now().timestamp())}",
                    user_phone=self.user_phone,
                    amount=bundle.price,
                    payment_method="wallet",
                    status="success"
                )
                db.commit()

                # 4. Sync local user object so UI updates immediately
                self.user.wallet_balance = new_wallet
                self.user.mb = new_data
                
                print(f"✅ Success! Added {bundle.size_mb} MB. Total: {new_data} MB")
        except Exception as e:
            print(f"❌ Error Try again")
            
        input("\nPress Enter to return...")
    def deposit_flow(self):
        """The 'Self-Funding' privilege: Allows users to add money to their wallet."""
        Utils.clear_screen()
        Utils.header("💳 FUND MY WALLET")
        
        try:
            print(f"Current Balance: ₦{self.user.wallet_balance:,.2f}")
            user_input = input("\nEnter amount to deposit (₦): ")
            amount = float(user_input) 
            
            if amount <= 0:
                print("❌ Please enter an amount greater than zero.")
            else:
                # 1. Calculate New Balance (Handle None/Null safety)
                current_balance = self.user.wallet_balance or 0.0
                new_balance = current_balance + amount
                
                # 2. Update Database using the phone number as the unique ID
                db(db.user.phone_number == self.user_phone).update(wallet_balance=new_balance)
                
                # 3. Log the Transaction for history tracking
                db.transaction.insert(
                    order_id=f"DEP-{int(datetime.now().timestamp())}",
                    user_phone=self.user_phone,
                    amount=amount,
                    payment_method="self-deposit",
                    status="success"
                )
                
                # 4. Save changes to the DB
                db.commit()
                
                # 5. Update the local object so the UI shows the new balance immediately
                self.user.wallet_balance = new_balance
            
                print(f"\n✅ Wallet Successfully Funded!")
                print(f"New Balance: ₦{new_balance:,.2f}")

        except ValueError:
            print("❌ Invalid input. Please enter a number (e.g., 1000).")
        except Exception as e:
            print(f"❌ Database Error: {e}")
            
        input("\nPress Enter to return to menu...")
    def share_data_flow(self):
        """Subtracts MB from current user and adds to recipient, logging both transactions."""
        Utils.clear_screen()
        print("--- 📲 SHARE DATA ---")
        print(f"Your Current Balance: {self.user.mb or 0} MB")
        
        recipient_phone = input("Enter recipient phone number: ")
        recipient = db(db.user.phone_number == recipient_phone).select().first()

        if not recipient:
            print("❌ Recipient user not found.")
        elif recipient_phone == self.user_phone:
            print("❌ You cannot share data with yourself.")
        else:
            try:
                amount_to_share = int(input("Enter amount to share (MB): "))
                
                if amount_to_share <= 0:
                    print("❌ Invalid amount.")
                elif (self.user.mb or 0) < amount_to_share:
                    print("❌ Insufficient data balance.")
                else:
                    # 1. Update Sender
                    new_sender_mb = self.user.mb - amount_to_share
                    db(db.user.phone_number == self.user_phone).update(mb=new_sender_mb)
                    
                    # 2. Update Recipient
                    new_recp_mb = (recipient.mb or 0) + amount_to_share
                    db(db.user.phone_number == recipient_phone).update(mb=new_recp_mb)
                    
                    # 3. Log Transaction for SENDER
                    db.transaction.insert(
                        order_id=f"SHR-OUT-{int(datetime.now().timestamp())}",
                        user_phone=self.user_phone,
                        amount=0,  # Cash amount is 0
                        payment_method=f"Data Share (Sent {amount_to_share}MB)",
                        status="success",
                        created_at=datetime.now()
                    )

                    # 4. Log Transaction for RECIPIENT
                    db.transaction.insert(
                        order_id=f"SHR-IN-{int(datetime.now().timestamp())}",
                        user_phone=recipient_phone,
                        amount=0,  # Cash amount is 0
                        payment_method=f"Data Share (Received {amount_to_share}MB)",
                        status="success",
                        created_at=datetime.now()
                    )
                    
                    db.commit()
                    
                    # Sync local object for the UI
                    self.user.mb = new_sender_mb
                    
                    print(f"✅ Successfully shared {amount_to_share} MB with {recipient.username}!")
                    
            except ValueError:
                print("❌ Please enter a valid number for MB.")
            except Exception as e:
                db.rollback()
                print(f"❌ Transaction failed: {e}")
        
        input("\nPress Enter to return...")

    def view_profile(self):
        """Shows full profile including Data Balance."""
        self.refresh_user_data()
        Utils.clear_screen()
        print("--- 👤 MY PROFILE & BALANCE ---")
        table = PrettyTable(["Description", "Value"])
        table.align["Description"] = "l"
        table.add_row(["Full Name", self.user.username])
        table.add_row(["Phone Number", self.user.phone_number])
        table.add_row(["Wallet Cash", f"₦{self.user.wallet_balance:,.2f}"])
        table.add_row(["Data Balance", f"{self.user.mb or 0} MB"])
        table.add_row(["Account Status", "Active"])
        print(table)
        input("\nPress Enter to return...")