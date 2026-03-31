from models.db import db
from prettytable import PrettyTable
from datetime import datetime, timezone

class Admin_services:
    @staticmethod
    def view_transaction():
        table = PrettyTable()
        table.field_names = ["ID", "Order ID", "Amount (₦)", "Method", "Status", "Created At"]
        rows = db(db.transaction).select()
        for row in rows:
            table.add_row([
                row.id,
                row.order_id,
                f"₦{row.amount:,.2f}",
                row.payment_method,
                row.status,
                row.created_at.strftime("%Y-%m-%d %H:%M")
            ])
        print(table)
    @staticmethod
    def view_transaction_count():
        success_sum = db.transaction.amount.sum()
        query = (db.transaction.status == 'success')
        total_success = db(query).select(success_sum).first()[success_sum] or 0.0
        print(f"Confirmed Revenue: ₦{total_success:,.2f}")
    @staticmethod
    def view_bundles():
        table = PrettyTable()
        table.field_names = ["ID", "Name", "Size (MB)", "Duration", "Price", "Active"]
        # Fetch all bundles from the DB
        rows = db(db.bundle).select()
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
    @staticmethod
    def add_bundles(name : str, size : int , duration : str, price : int , is_active : bool):
        new_id = db.bundle.insert(
        name=name,
        size_mb=size,
        duration_type=duration,
        price=price,
        is_active=is_active
         )
        db.commit()
        mini_table = PrettyTable()
        mini_table.field_names = ["ID", "Bundle Name", "Size", "Price"]

        # 3. Add just the new data
        mini_table.add_row([new_id, name, f"{size}MB", f"₦{price:,.2f}"])

        # 4. Print it
        print("\n✅ Bundle successfully added:")
        print(mini_table)
    
    @staticmethod
    def toggle_by_name(bundle_name):
        search_name = bundle_name.strip()
        bundle = db(db.bundle.name == search_name).select().first()
        
        if not bundle:
            print(f"❌ Invalid bundle name: '{search_name}'")
            return 
        new_status = not bundle.is_active
        db(db.bundle.id == bundle.id).update(is_active=new_status)
        db.commit()
        confirm_table = PrettyTable()
        confirm_table.field_names = ["ID", "Bundle Name", "Previous", "Current Status"]
        
        old_icon = "✅ ACTIVE" if bundle.is_active else "❌ INACTIVE"
        new_icon = "✅ ACTIVE" if new_status else "❌ INACTIVE"
        
        confirm_table.add_row([bundle.id, bundle.name, old_icon, new_icon])
        
        print("\n🔄 Bundle Status Updated:")
        print(confirm_table)
    @staticmethod
    def view_users() :
        table = PrettyTable()
        table.field_names = ["ID", "Name","Role", "Balance", "Time created"]
        rows = db(db.user).select() 
        for r in rows:
            table.add_row([
                r.id, 
                r.username, 
                r.role,
                f"₦{r.wallet_balance:,.2f}", 
                r.created_at.strftime("%Y-%m-%d %H:%M") # Format the date nicely
            ])
        print(table)
    @staticmethod
    def users_count():
        count = db(db.user).count()
        print(f"Amount of users {count}")
    @staticmethod
    def edit_bundle_factory(bundle_id, **updates):
        """Dynamicly updates any field in a bundle (price, name, etc.)"""
        bundle = db.bundle(bundle_id)
        if not bundle:
            print(f"❌ Bundle ID {bundle_id} not found.")
            return

        # Perform the update
        db(db.bundle.id == bundle_id).update(**updates)
        db.commit()

        # UI Confirmation
        table = PrettyTable(["Field", "New Value"])
        for key, val in updates.items():
            table.add_row([key.replace("_", " ").title(), val])
        
        print(f"\n✅ Bundle '{bundle.name}' updated:")
        print(table)

    @staticmethod
    def search_transactions(phone_number=None, status=None):
        """Filters transactions by user phone or status"""
        query = db.transaction.id > 0 # Base query
        
        if phone_number:
            # Assumes transaction table has a 'user_phone' field or similar
            query &= (db.transaction.user_phone == phone_number)
        if status:
            query &= (db.transaction.status == status)

        rows = db(query).select(orderby=~db.transaction.created_at) # Newest first
        
        table = PrettyTable(["ID", "Phone", "Amount", "Status", "Date"])
        for r in rows:
            table.add_row([r.id, r.user_phone, f"₦{r.amount:,.2f}", r.status, r.created_at])
        
        print(f"\n🔍Search Results ({len(rows)} found):")
        print(table)

    @staticmethod
    def manual_deposit(phone_number, amount):
        """Adds money to a user's balance via phone number"""
        user = db(db.user.phone_number == phone_number).select().first()
        if not user:
            print(f"User with phone {phone_number} not found.")
            return

        new_balance = user.balance + float(amount)
        db(db.user.phone == phone_number).update(balance=new_balance)
        db.commit()

        print(f"Deposit Successful! {user.name}'s new balance: ₦{new_balance:,.2f}")

    @staticmethod
    def delete_record(table_name, record_id):
        """Safety-first deletion for bundles or users"""
        # Mapping string names to actual DB tables
        tables = {"bundle": db.bundle, "user": db.user}
        
        if table_name not in tables:
            print("Invalid table name.")
            return

        target_table = tables[table_name]
        if db(target_table.id == record_id).delete():
            db.commit()
            print(f"🗑️Successfully deleted {table_name} ID: {record_id}")
        else:
            print(f"❌Could not find {table_name} with ID {record_id}")
        