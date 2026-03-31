

from models.db import db
from datetime import datetime
from admin.admin_ui import AdminUI
from UI.user_ui import UserUI
# ui = AdminUI("admin1") # Create the object first
# ui.main_menu()

user = UserUI("08000000002")
user.user_menu()

# def create_user(username, password, phone, email=None, role="customer"):
#     """
#     Inserts a new user into the user table.
#     Defaults to 0 wallet balance and 'customer' role.
#     """
#     try:
#         # Simple 'hash' placeholder - replace with a real library like passlib or bcrypt later
#         hashed_password = f"HASH_{password}" 

#         user_id = db.user.insert(
#             username=username,
#             password=hashed_password,
#             phone_number=phone,
#             email=email,
#             role=role,
#             wallet_balance=0.0,
#             created_at=datetime.now()
#         )
#         db.commit()
#         print(f"✅ User '{username}' created successfully with ID: {user_id}")
#         return user_id

#     except Exception as e:
#         db.rollback()
#         print(f"❌ Error creating user: {e}")
#         return None
# create_user("gam" , "12345erty" , 9023456789 , "customer")
