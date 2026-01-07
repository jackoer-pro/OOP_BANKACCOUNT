import json
import os
from datetime import datetime, timedelta

# --- 1. INTEREST FORMULA ---
class FlexibleInterest:
    @staticmethod
    def calculate(balance, days):
        # 0.1% per day (Example: 10 days = 1% interest)
        rate = days * 0.001 
        return balance * rate

# --- 2. THE HYBRID MODEL ---
class HybridAccount:
    def __init__(self, account_number, owner, password, balance=0, saving_balance=0, 
                 unlock_date=None, last_fee_date=None, last_interest_date=None, 
                 saved_days=0, **kwargs):
        
        self.account_number = account_number
        self.owner = owner
        self.password = password
        self.balance = balance
        self.saving_balance = saving_balance
        self.saved_days = saved_days 
        
        # Load dates or set to now
        self.last_fee_date = datetime.fromisoformat(last_fee_date) if last_fee_date else datetime.now()
        self.last_interest_date = datetime.fromisoformat(last_interest_date) if last_interest_date else datetime.now()
        self.unlock_date = datetime.fromisoformat(unlock_date) if unlock_date else datetime.now()

    def apply_monthly_fee(self):
        """Deducts $10 for every 30-day block passed since last check"""
        while datetime.now() >= self.last_fee_date + timedelta(days=30):
            self.balance -= 10.0
            self.last_fee_date += timedelta(days=30)
            print(f"📉 $10 Fee deducted from Main.")

    def apply_interest(self):
        """Applies interest for every 'X' day cycle passed since last check"""
        if self.saved_days <= 0 or self.saving_balance <= 0:
            return

        interest_period = timedelta(days=self.saved_days)
        while datetime.now() >= self.last_interest_date + interest_period:
            earned = FlexibleInterest.calculate(self.saving_balance, self.saved_days)
            self.saving_balance += earned
            self.last_interest_date += interest_period # This 'breaks' the loop once caught up
            print(f"🎊 Interest Paid: ${earned:.2f} ({self.saved_days} day cycle)")

    def move_to_savings(self, amount, days):
        if 0 < amount <= self.balance:
            self.balance -= amount
            self.saving_balance += amount
            self.saved_days = days
            self.unlock_date = datetime.now() + timedelta(days=days)
            self.last_interest_date = datetime.now() # Reset clock to start new countdown
            print(f"✅ Locked ${amount} for {days} days.")
            return True
        print("❌ Insufficient funds in Main.")
        return False

    def withdraw_to_main(self, amount):
        if datetime.now() < self.unlock_date:
            delta = self.unlock_date - datetime.now()
            print(f"❌ LOCKED! Wait {delta.days + 1} more days.")
            return False
        
        if 0 < amount <= self.saving_balance:
            self.saving_balance -= amount
            self.balance += amount
            print(f"✅ Moved ${amount} back to Main.")
            return True
        print("❌ Insufficient Savings.")
        return False

    def get_full_details(self):
        days_left = max(0, (self.unlock_date - datetime.now()).days)
        return (f"\n--- 🏦 Acc: {self.account_number} | {self.owner} ---"
                f"\nMain Balance:   ${self.balance:.2f}"
                f"\nSavings Balance: ${self.saving_balance:.2f}"
                f"\nLock Duration:   {self.saved_days} days"
                f"\nDays to Unlock:  {days_left} days"
                f"\n-----------------------")

    def to_dict(self):
        return {
            "account_number": self.account_number, "owner": self.owner,
            "password": self.password, "balance": self.balance,
            "saving_balance": self.saving_balance, "saved_days": self.saved_days,
            "unlock_date": self.unlock_date.isoformat(),
            "last_fee_date": self.last_fee_date.isoformat(),
            "last_interest_date": self.last_interest_date.isoformat()
        }

# --- 3. STORAGE & MAIN ---
class AccountStorage:
    def __init__(self, filename="hybrid_bank.json"):
        self.filename = filename
    def load(self):
        if not os.path.exists(self.filename): return []
        with open(self.filename, "r") as f:
            try: return [HybridAccount(**d) for d in json.load(f)]
            except: return []
    def save(self, accounts):
        with open(self.filename, "w") as f:
            json.dump([acc.to_dict() for acc in accounts], f, indent=4)

storage = AccountStorage()
accounts = storage.load()

while True:
    print("\n1. Register | 2. Info | 3. Deposit | 4. Withdraw (Main) | 5. Manage Savings | 6. Exit")
    choice = input("Select: ")

    if choice == "1":
        num, name, pw = input("Acc #: "), input("Owner: "), input("PW: ")
        bal = float(input("Initial Deposit: "))
        accounts.append(HybridAccount(num, name, pw, balance=bal))
        storage.save(accounts); print("✅ Registered!")

    elif choice in ["2", "3", "4", "5"]:
        num, pw = input("Acc #: "), input("PW: ")
        acc = next((a for a in accounts if a.account_number == num and a.password == pw), None)
        if not acc: print("❌ Invalid Login"); continue

        # Trigger logic updates automatically
        acc.apply_monthly_fee()
        acc.apply_interest()
        storage.save(accounts)

        if choice == "2":
            print(acc.get_full_details())
        elif choice == "3":
            acc.balance += float(input("Deposit Amount: "))
            storage.save(accounts)
        elif choice == "4":
            amt = float(input("Withdraw from Main: "))
            if amt <= acc.balance:
                acc.balance -= amt; print("✅ Success")
            else: print("❌ Insufficient funds.")
            storage.save(accounts)
        elif choice == "5":
            print("a. Main -> Savings | b. Savings -> Main")
            act = input("Action: ").lower()
            amt = float(input("Amount: "))
            if act == "a":
                days = int(input("Lock for how many days? "))
                acc.move_to_savings(amt, days)
            else:
                acc.withdraw_to_main(amt)
            storage.save(accounts)

    elif choice == "6":
        print("👋 Goodbye!"); break