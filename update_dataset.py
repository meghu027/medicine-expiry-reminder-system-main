import pandas as pd
from datetime import datetime, timedelta
import random

def update_dataset():
    # Read existing dataset
    df = pd.read_csv("medicine_dataset.csv")
    
    # Add recent medicines with realistic expiry dates
    new_medicines = []
    categories = ["Analgesic", "Antibiotic", "Antipyretic", "Anti-inflammatory", 
                 "Cardiac", "Diabetic", "Gastrointestinal", "Respiratory", 
                 "Vitamin", "Antihistamine"]
    
    medicine_names = [
        "Paracetamol", "Amoxicillin", "Aspirin", "Ibuprofen", "Metformin",
        "Amlodipine", "Omeprazole", "Salbutamol", "Vitamin D", "Cetirizine",
        "Insulin", "Atorvastatin", "Losartan", "Pantoprazole", "Azithromycin",
        "Levothyroxine", "Gabapentin", "Sertraline", "Simvastatin", "Metoprolol"
    ]
    
    # Generate medicines expiring at different time periods
    base_date = datetime.now()
    
    for i in range(100):  # Add 100 new medicines
        medicine_name = random.choice(medicine_names)
        category = random.choice(categories)
        batch_number = f"B{2000 + i}"
        
        # Random manufacturing date (last 2 years)
        mfg_date = base_date - timedelta(days=random.randint(30, 730))
        
        # Create balanced expiry distribution
        expiry_choice = random.choices(
            [7, 30, 90, 180, 365, 730],  # days from now
            weights=[15, 20, 25, 20, 15, 5],  # weights for balanced distribution
            k=1
        )[0]
        
        exp_date = base_date + timedelta(days=expiry_choice)
        quantity = random.randint(50, 500)
        
        new_medicines.append({
            "Medicine_Name": medicine_name,
            "Category": category,
            "Batch_Number": batch_number,
            "Manufacturing_Date": mfg_date.strftime("%Y-%m-%d"),
            "Expiry_Date": exp_date.strftime("%Y-%m-%d"),
            "Quantity": quantity
        })
    
    # Create DataFrame with new medicines
    new_df = pd.DataFrame(new_medicines)
    
    # Combine with existing dataset
    updated_df = pd.concat([df, new_df], ignore_index=True)
    
    # Save updated dataset
    updated_df.to_csv("medicine_dataset_updated.csv", index=False)
    
    print(f"Original dataset: {len(df)} medicines")
    print(f"Added: {len(new_df)} new medicines")
    print(f"Updated dataset: {len(updated_df)} total medicines")
    print(f"Saved as: medicine_dataset_updated.csv")
    
    # Quick analysis of new dataset
    updated_df["Expiry_Date"] = pd.to_datetime(updated_df["Expiry_Date"])
    today = pd.Timestamp(datetime.now())
    updated_df["days_to_expiry"] = (updated_df["Expiry_Date"] - today).dt.days
    
    print("\n=== Updated Dataset Analysis ===")
    expired = updated_df[updated_df["days_to_expiry"] < 0]
    expiring_30d = updated_df[(updated_df["days_to_expiry"] >= 0) & (updated_df["days_to_expiry"] <= 30)]
    expiring_90d = updated_df[(updated_df["days_to_expiry"] >= 0) & (updated_df["days_to_expiry"] <= 90)]
    
    print(f"Total medicines: {len(updated_df)}")
    print(f"Expired: {len(expired)} ({len(expired)/len(updated_df)*100:.1f}%)")
    print(f"Expiring within 30 days: {len(expiring_30d)} ({len(expiring_30d)/len(updated_df)*100:.1f}%)")
    print(f"Expiring within 90 days: {len(expiring_90d)} ({len(expiring_90d)/len(updated_df)*100:.1f}%)")

if __name__ == "__main__":
    update_dataset()
