from pydal import DAL , Field 
import os
from datetime import datetime, timezone
from pydal.validators import IS_IN_SET
folder_path = 'db'

# Pro-tip: Always ensure the directory exists before initializing
if not os.path.exists(folder_path):
    os.makedirs(folder_path)

# Pass the folder path as a separate argument
db = DAL('sqlite://telco.db', folder=folder_path)
db.define_table(
    "user",
    Field("username", "string", length=100, unique=True),
    Field("password", "string"),  # hashed before insert
    Field("phone_number", "string", unique=True),
    Field("role", "string", default="customer", requires=IS_IN_SET(["customer", "admin"])),
    Field("wallet_balance", "double", default=0.0),
    Field("mb" , "double", default=0.0),
    Field("created_at", "datetime", default=lambda: datetime.now(timezone.utc))
)
db.define_table(
    "bundle",
    Field("name", "string"),
    Field("size_mb", "double"),
    Field("duration_type", "string", requires=IS_IN_SET(["daily", "weekly", "monthly"])),
    Field("price", "double"),
    Field("is_active", "boolean", default=True)
)
db.define_table(
    "order",
    Field("user_id", "reference user"),
    Field("bundle_id", "reference bundle"),
    Field("recipient_phone", "string"),
    Field("status", "string", default="pending",
          requires=IS_IN_SET(["pending", "completed", "failed"])),
    Field("created_at", "datetime", default=lambda: datetime.now(timezone.utc))
)
db.define_table(
    "transaction",
    Field("order_id", "string"),
    Field("user_phone", "string"), 
    Field("amount", "double"),
    Field("payment_method", "string", default="wallet"),
    Field("status", "string", default="pending"),
    Field("created_at", "datetime", default=lambda: datetime.now(timezone.utc))
)
db.define_table(
    "topup",
    Field("user_id", "reference user"),
    Field("amount", "double"),
    Field("reference", "string", unique=True),
    Field("status", "string", default="success",
          requires=IS_IN_SET(["success", "pending", "failed"])),
    Field("created_at", "datetime", default=lambda: datetime.now(timezone.utc))
)
import hashlib

def hash_password(p):
    return hashlib.sha256(p.encode()).hexdigest()


# def seed_data(db):
#     """
#     Seeds initial users and bundles.
#     Safe to run multiple times (no duplicates).
#     """

#     # ── USERS ────────────────────────────────────────────
#     users = [
#         dict(
#             username="admin1",
#             password=hash_password("admin123  "),
#             phone_number="08000000001",
#             role="admin",
#             wallet_balance=0.0
#         ),
#         dict(
#             username="admin2",
#             password=hash_password("admin123"),
#             phone_number="08000000002",
#             role="admin",
#             wallet_balance=0.0
#         ),
#         dict(
#             username="user1",
#             password=hash_password("user123"),
#             phone_number="08000000003",
#             role="customer",
#             wallet_balance=500.0
#         ),
#     ]

#     for u in users:
#         exists = db(db.user.username == u["username"]).count()
#         if not exists:
#             db.user.insert(**u)
#             print(f"✅ Created user: {u['username']}")

#     # ── BUNDLES ──────────────────────────────────────────
#     bundles = [
#         dict(name="Daily 500MB", size_mb=500, duration_type="daily", price=100),
#         dict(name="Daily 1GB", size_mb=1000, duration_type="daily", price=200),
#         dict(name="Weekly 2GB", size_mb=2000, duration_type="weekly", price=500),
#         dict(name="Weekly 5GB", size_mb=5000, duration_type="weekly", price=1200),
#         dict(name="Monthly 10GB", size_mb=10000, duration_type="monthly", price=2500),
#     ]

#     for b in bundles:
#         exists = db(db.bundle.name == b["name"]).count()
#         if not exists:
#             db.bundle.insert(**b)
#             print(f"✅ Added bundle: {b['name']}")

#     db.commit()
# seed_data(db)