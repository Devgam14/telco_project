from models.db import db
from datetime import datetime
import hashlib

def hash_pw(password):
    return hashlib.sha256(password.encode()).hexdigest()

def run_seed():
    print("--- 🔧 Seeding Database ---")
    
    # 1. Clear existing data (Optional, but recommended for a fresh seed)
    db.transaction.truncate()
    db.bundle.truncate()
    db.user.truncate()
    db.commit()

    # 2. Seed Admins (2 Admins)
    admins = [
        {"username": "admin_one", "phone": "08000000001", "email": "admin1@telco.com"},
        {"username": "admin_two", "phone": "08000000002", "email": "admin2@telco.com"}
    ]
    
    for a in admins:
        db.user.insert(
            username=a['username'],
            password=hash_pw("admin123"),
            phone_number=a['phone'],
            email=a['email'],
            role="admin",
            wallet_balance=2000.0,
            mb=0.0,
            created_at=datetime.now()
        )

    # 3. Seed Users (10 Users)
    for i in range(1, 11):
        db.user.insert(
            username=f"user_test_{i}",
            password=hash_pw("user123"),
            phone_number=f"0900000000{i}",
            email=f"user{i}@example.com",
            role="customer",
            wallet_balance=2000.0,
            mb=0.0,
            created_at=datetime.now()
        )

    # 4. Seed Data Bundles (Daily, Weekly, Monthly - 4 Plans Each)
    # Format: (Name, Size_MB, Duration, Price)
    plans = [
        # Daily Plans
        ("Daily Lite", 200, "daily", 50.0),
        ("Daily Standard", 500, "daily", 100.0),
        ("Daily Heavy", 1000, "daily", 200.0),
        ("Daily Unlimited", 2500, "daily", 500.0),
        
        # Weekly Plans
        ("Weekly Small", 1000, "weekly", 300.0),
        ("Weekly Medium", 3000, "weekly", 700.0),
        ("Weekly Mega", 5000, "weekly", 1200.0),
        ("Weekly Giga", 10000, "weekly", 2000.0),
        
        # Monthly Plans
        ("Monthly Starter", 5000, "monthly", 1500.0),
        ("Monthly Value", 12000, "monthly", 3500.0),
        ("Monthly Pro", 25000, "monthly", 6000.0),
        ("Monthly Extreme", 50000, "monthly", 10000.0),
    ]

    for name, size, dur, price in plans:
        db.bundle.insert(
            name=name,
            size_mb=size,
            duration_type=dur,
            price=price,
            is_active=True
        )

    db.commit()
    print("✅ Seeding Complete!")
    print(f"Created: 2 Admins, 10 Users (₦2,000 each), and 12 Data Plans.")

if __name__ == "__main__":
    run_seed()