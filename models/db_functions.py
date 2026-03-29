from db import db as db
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
    def create_transaction(order_id, amount):
        return db.transaction.insert(
            order_id=order_id,
            amount=amount
        )

    @staticmethod
    def update_status(transaction_id, status):
        db(db.transaction.id == transaction_id).update(status=status)
class TopupService:

    @staticmethod
    def create_topup(user_id, amount, reference):
        return db.topup.insert(
            user_id=user_id,
            amount=amount,
            reference=reference
        )