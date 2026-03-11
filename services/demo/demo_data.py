# Run this once to generate 100 rows for Person 2
import pandas as pd
import random
from datetime import datetime, timedelta

def generate_feedback_csv(rows=100):
    data = []
    vehicles = ['VEH001','VEH002','VEH003','VEH004','VEH005']
    customers = ['Rahul Sharma','Priya Singh','Amit Kumar','Neha Gupta','Raj Patel']
    issues = ['brake_failure','engine_warning','oil_change','tyre_pressure','battery']
    
    for i in range(rows):
        rating = random.choices([1,2,3,4,5], weights=[5,10,15,35,35])[0]
        sentiment = 'positive' if rating >= 4 else 'negative' if rating <= 2 else 'neutral'
        days_ago = random.randint(0, 90)
        date = datetime.now() - timedelta(days=days_ago)
        
        data.append({
            'vehicle_id':    random.choice(vehicles),
            'customer_name': random.choice(customers),
            'rating':        rating,
            'sentiment':     sentiment,
            'issue_type':    random.choice(issues),
            'resolved':      random.choice([True, True, True, False]),
            'timestamp':     date.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    df = pd.DataFrame(data)
    df.to_csv('ml/data/service_feedback.csv', index=False)
    print(f"Generated {rows} rows in ml/data/service_feedback.csv")
    print(df.head())
    print(f"Rating distribution:\n{df['rating'].value_counts().sort_index()}")

if __name__ == "__main__":
    generate_feedback_csv(100)