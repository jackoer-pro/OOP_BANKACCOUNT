import json
import os
class BankAccount():
    def __init__(self,account_number,owner,password,balance=0,**kwargs):
        self.account_number = account_number
        self.owner = owner
        self.password=password
        self.balance = balance
    def add_balance(self,amount):
        self.balance+=amount
        print(f"✅ Deposited ${amount}. New balance: ${self.balance}")
    def with_draw(self,amount):
        if amount > self.balance:
            print("❌ Insufficient funds")
        else:
            self.balance -= amount
            print(f"✅ Withdrew ${amount}. New balance: ${self.balance}")
    def to_dict(self):
        return {
            "type": self.__class__.__name__,
            "account_number": self.account_number,
            "owner": self.owner,
            "password": self.password,
            "balance": self.balance
        }
    @staticmethod
    def from_dict(data):
        account_type = data.pop("type", "BankAccount")
        if account_type == "CheckingAccount":
            return CheckingAccount(**data)
        elif account_type == "SavingsAccount":
            sa = SavingAccount(**data)
            sa.saving_balance = data.get("saving_balance", 0)
            return sa
        else:
            return BankAccount(**data)

class CheckingAccount(BankAccount):
    pass
class SavingAccount(BankAccount):
    def __init__(self,account_number,owner,password,balance=0,saving_balance=0,**kwargs):
        super().__init__(account_number,owner,password,balance)
        self.saving_balance=saving_balance
    def deposit_to_saving(self,amount):
        if amount> self.balance:
            print("not enough balance")
        else:
            self.balance-=amount
            self.saving_balance+=amount
            print(f"✅ Savings: ${self.saving_balance}")
    def withdraw_from_checking(self,amount):
        if amount> self.saving_balance:
            print("❌ Not enough savings")
        else:
            self.saving_balance -= amount
            self.balance += amount
            print(f"✅ Savings: ${self.saving_balance}")
    def to_dict(self):
        data=super().to_dict()
        data["saving_balance"]=self.saving_balance
        return data
class AccountStorage:
    DATA_FILE = "bank_data.json"
    @staticmethod
    def load_data():
        if not os.path.exists(AccountStorage.DATA_FILE):
            return []
        with open(AccountStorage.DATA_FILE,"r") as f:
            data=json.load(f)
        return([BankAccount.from_dict(acc) for acc in data])
    @staticmethod
    def save_data(accounts):
        with open(AccountStorage.DATA_FILE,"w") as f:
            json.dump([BankAccount.to_dict(acc) for acc in accounts],f, indent=4)
### main loop ##
accounts=AccountStorage.load_data()
while True:
    print("\n1. Register | 2. Show | 3. Deposit | 4. Withdraw | 5. Savings | 6. Exit")
    choice = input("Choose: ")
    if choice=="1":
        num=input("type your account number: ")
        name=input("owner: ")
        pw=input("password: ")
        t=input("Type (checking/savings): ").lower()
        bal = float(input("Initial: "))
        new_acc= SavingAccount(num,name,pw,bal) if t=="savings" else CheckingAccount(num,name,pw,t,bal)
        accounts.append(new_acc)
        AccountStorage.save_data(accounts)
    elif choice=="2":
        s_num = input("Acc #: ")
        S_pw = input("PW: ")

        acc = next((a for a in accounts if a.account_number == num and a.password == pw), None)
        if acc:
            s_bal=f"| Savings: ${acc.saving_balance}" if isinstance(acc,SavingAccount) else ""
            print(f"{acc.account_number} | {acc.owner} | Bal: ${acc.balance}{s_bal}")
    elif choice in ["3","4","5"]:
        um = input("Acc #: ")
        pw = input("PW: ")
        # Find account in the existing list (RAM)
        acc = next((a for a in accounts if a.account_number == num and a.password == pw), None)
        if acc:
            if choice=="3":
                acc.add_balance(float(input("Amount: ")))
            elif choice=="4":
                acc.with_draw(float(input("Amount: ")))
            elif choice=="5":
                act = input("Deposit/Withdraw (d/w): ").lower()
                amt=input("choose your amount: ")
                if act=="d":
                    acc.deposit_to_saving(amt)
                else:
                    acc.withdraw_from_checking(amt)
            AccountStorage.save_data()
        else: 
            print("invaid credibility")
    elif choice=="6":
        break
