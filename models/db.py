from pydal import DAL , Field 
from datetime import datetime
from pydal.validators import IS_IN_SET
db = DAL('sqlite://db/telco.db')


# id PK
# int
# name
# string
# size_mb
# double (MB)
# duration_type
# "daily"|"weekly"|"monthly"
# price
# double (₦)
# is_active
db.define_table(
    "user",
    Field("username", "string", length=100, unique=True),
    Field("password", "string"),  # hashed before insert
    Field("phone_number", "string", unique=True),
    Field("role", "string", default="customer", requires=IS_IN_SET(["customer", "admin"])),
    Field("wallet_balance", "double", default=0.0),
    Field("created_at", "datetime", default=datetime.utcnow)
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
    Field("ordered_at", "datetime", default=datetime.utcnow)
)
db.define_table(
    "transaction",
    Field("order_id", "reference order", unique=True),  # one-to-one
    Field("amount", "double"),
    Field("payment_method", "string", default="wallet",
          requires=IS_IN_SET(["wallet"])),
    Field("status", "string", default="pending",
          requires=IS_IN_SET(["pending", "success", "failed"])),
    Field("created_at", "datetime", default=datetime.utcnow)
)
db.define_table(
    "topup",
    Field("user_id", "reference user"),
    Field("amount", "double"),
    Field("reference", "string", unique=True),
    Field("status", "string", default="success",
          requires=IS_IN_SET(["success", "pending", "failed"])),
    Field("created_at", "datetime", default=datetime.utcnow)
)