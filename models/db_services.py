from models.db import db
class UserService:
    @staticmethod
    def create_user(username, password, phone_number, role="customer"):
        return db.user.insert(
            username=username,
            password=password,  # already hashed
            phone_number=phone_number,
            role=role
        )

    @staticmethod
    def get_user_by_phone(phone_number):
        return db(db.user.phone_number == phone_number).select().first()

    @staticmethod
    def update_wallet(user_id, amount):
        user = db.user(user_id)
        if not user:
            return None

        new_balance = user.wallet_balance + amount
        db(db.user.id == user_id).update(wallet_balance=new_balance)
        return new_balance
class BundleService:
    @staticmethod
    def create_bundle(name, size_mb, duration_type, price):
        return db.bundle.insert(
            name=name,
            size_mb=size_mb,
            duration_type=duration_type,
            price=price
        )

    @staticmethod
    def get_active_bundles():
        return db(db.bundle.is_active == True).select()
class OrderService:
    @staticmethod
    def create_order(user_id, bundle_id, recipient_phone):
        return db.order.insert(
            user_id=user_id,
            bundle_id=bundle_id,
            recipient_phone=recipient_phone
        )

    @staticmethod
    def update_status(order_id, status):
        db(db.order.id == order_id).update(status=status)
class TransactionService:

    @staticmethod
    def create_transaction(order_id, amount, user_phone):
        """
        Creates a new transaction record linked to a specific user phone.
        """
        # We add user_phone here so the Admin can search for it later
        new_id = db.transaction.insert(
            order_id=order_id,
            amount=amount,
            user_phone=user_phone,
            status="pending" # Defaulting to pending is safer
        )
        db.commit()
        return new_id

    @staticmethod
    def update_status(transaction_id, status):
        """
        Updates the status (success/failed) of a transaction.
        """
        # IS_IN_SET validation usually happens at the form level, 
        # but we do a quick check here for safety.
        valid_statuses = ["pending", "success", "failed"]
        if status not in valid_statuses:
            print(f"⚠️ Invalid status: {status}")
            return False

        updated = db(db.transaction.id == transaction_id).update(status=status)
        db.commit()
        return updated
class TopupService:

    @staticmethod
    def create_topup(user_id, amount, reference):
        return db.topup.insert(
            user_id=user_id,
            amount=amount,
            reference=reference
        )