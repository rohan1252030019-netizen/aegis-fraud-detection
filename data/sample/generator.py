"""AEGIS - Synthetic Financial Data Generator"""
import random
import uuid
from datetime import datetime, timedelta
import pandas as pd


def generate_synthetic_transactions(num_accounts: int = 50, num_txs: int = 500) -> pd.DataFrame:
    accounts = [f"ACC_{1000 + i}" for i in range(num_accounts)]
    mules = random.sample(accounts, k=max(2, num_accounts // 10))

    data = []
    base_time = datetime.now() - timedelta(days=30)

    for i in range(num_txs):
        # Decide if this transaction is part of mule activity
        is_mule = random.random() < 0.25
        if is_mule:
            mule = random.choice(mules)
            sender = random.choice([a for a in accounts if a != mule])
            receiver = mule
            amount = round(random.uniform(2000, 9500), 2)
        else:
            sender, receiver = random.sample(accounts, 2)
            amount = round(random.uniform(10, 800), 2)

        tx_time = base_time + timedelta(minutes=random.randint(1, 43200))
        data.append({
            "transaction_id": f"TX_{uuid.uuid4().hex[:10].upper()}",
            "sender_account_id": sender,
            "receiver_account_id": receiver,
            "amount": amount,
            "currency": "USD",
            "transaction_type": "TRANSFER",
            "timestamp": tx_time.isoformat(),
        })

    return pd.DataFrame(data)


if __name__ == "__main__":
    df = generate_synthetic_transactions()
    output_path = "c:/Users/ADMIN/Documents/EDI PROJECT/aegis/data/sample/transactions.csv"
    df.to_csv(output_path, index=False)
    print(f"Generated {len(df)} sample transactions at {output_path}")
