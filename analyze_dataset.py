import pandas as pd
from datetime import date
from pathlib import Path

def analyze_dataset():
    df = pd.read_csv("medicine_dataset.csv")
    
    # Convert dates
    df["Manufacturing_Date"] = pd.to_datetime(df["Manufacturing_Date"], errors="coerce")
    df["Expiry_Date"] = pd.to_datetime(df["Expiry_Date"], errors="coerce")
    
    today = pd.Timestamp(date.today())
    df["days_to_expiry"] = (df["Expiry_Date"] - today).dt.days
    
    print("=== DATASET ANALYSIS ===")
    print(f"Total medicines: {len(df)}")
    print(f"Valid expiry dates: {df['Expiry_Date'].notna().sum()}")
    print()
    
    # Expiry analysis
    print("=== EXPIRY ANALYSIS ===")
    expired = df[df["days_to_expiry"] < 0]
    print(f"Already expired: {len(expired)} ({len(expired)/len(df)*100:.1f}%)")
    
    expiring_7d = df[(df["days_to_expiry"] >= 0) & (df["days_to_expiry"] <= 7)]
    print(f"Expiring within 7 days: {len(expiring_7d)} ({len(expiring_7d)/len(df)*100:.1f}%)")
    
    expiring_30d = df[(df["days_to_expiry"] >= 0) & (df["days_to_expiry"] <= 30)]
    print(f"Expiring within 30 days: {len(expiring_30d)} ({len(expiring_30d)/len(df)*100:.1f}%)")
    
    expiring_90d = df[(df["days_to_expiry"] >= 0) & (df["days_to_expiry"] <= 90)]
    print(f"Expiring within 90 days: {len(expiring_90d)} ({len(expiring_90d)/len(df)*100:.1f}%)")
    
    valid_future = df[df["days_to_expiry"] > 0]
    print(f"Valid (not expired): {len(valid_future)} ({len(valid_future)/len(df)*100:.1f}%)")
    print()
    
    # Category analysis
    print("=== CATEGORY ANALYSIS ===")
    category_expiry = df.groupby("Category")["days_to_expiry"].agg(["count", "mean", "min", "max"]).round(1)
    print(category_expiry)
    print()
    
    # Show some examples
    print("=== SAMPLE DATA ===")
    print("Medicines expiring soon:")
    soon = df[(df["days_to_expiry"] >= 0) & (df["days_to_expiry"] <= 30)].sort_values("days_to_expiry")
    if len(soon) > 0:
        print(soon[["Medicine_Name", "Category", "Expiry_Date", "days_to_expiry"]].head(10))
    else:
        print("No medicines expiring within 30 days")
    
    print("\nAlready expired medicines:")
    if len(expired) > 0:
        print(expired[["Medicine_Name", "Category", "Expiry_Date", "days_to_expiry"]].head(10))
    else:
        print("No expired medicines")

if __name__ == "__main__":
    analyze_dataset()
