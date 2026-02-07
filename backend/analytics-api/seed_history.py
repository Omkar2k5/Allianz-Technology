import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from app.database.connection import SessionLocal
from app.database.models import GenAIRequest, App, User, Team
from datetime import datetime, timedelta
import random
import uuid

def seed_history():
    db = SessionLocal()
    
    # 1. Ensure we have a Team, User, and App
    # Check for existing user or create one
    user = db.query(User).first()
    if not user:
        print("Creating dummy user...")
        user = User(
            email="demo@example.com",
            hashed_password="hashed_dummy_password",
            full_name="Demo User",
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # Check for existing team or create one
    team = db.query(Team).first()
    if not team:
        print("Creating dummy team...")
        team = Team(
            name="Demo Team",
            organization="Demo Org"
        )
        db.add(team)
        db.commit()
        db.refresh(team)

    # Check for existing app or create one
    app = db.query(App).filter(App.name == "Demo App").first()
    if not app:
        print("Creating dummy app...")
        app = App(
            team_id=team.id,
            name="Demo App",
            api_key_hash="dummy_hash_" + str(uuid.uuid4())
        )
        db.add(app)
        db.commit()
        db.refresh(app)
    
    app_id = app.id
    user_id = user.id
    
    models = ["gpt-4", "llama-3-70b", "claude-3-opus", "gpt-3.5-turbo"]
    regions = ["us-east-1", "eu-west-1", "us-west-2"]
    
    print(f"Seeding historical data for App: {app_id}...")
    
    # Generate data for the last 120 days
    start_date = datetime.utcnow() - timedelta(days=120)
    
    records = []
    for day in range(120):
        current_date = start_date + timedelta(days=day)
        
        # Random number of requests per day (variable pattern)
        # Weekdays have more traffic
        is_weekend = current_date.weekday() >= 5
        base_requests = random.randint(5, 15) if is_weekend else random.randint(20, 50)
        
        for _ in range(base_requests):
            # Random time during the day
            timestamp = current_date + timedelta(hours=random.randint(0, 23), minutes=random.randint(0, 59))
            
            model = random.choice(models)
            tokens_in = random.randint(100, 2000)
            tokens_out = random.randint(50, 1000)
            
            # Rough estimates
            energy = (tokens_in + tokens_out) * 0.00001  # Wh
            co2 = energy * 0.4  # g
            
            req = GenAIRequest(
                app_id=app_id,
                user_id=user_id,
                timestamp=timestamp,
                request_hash=str(uuid.uuid4()),
                model_name=model,
                provider=model.split('-')[0],
                region=random.choice(regions),
                tokens_input=tokens_in,
                tokens_output=tokens_out,
                tokens_total=tokens_in + tokens_out,
                latency_ms=random.randint(200, 3000),
                energy_wh=energy,
                co2_g=co2,
                cost_usd=(tokens_in + tokens_out) * 0.000002
            )
            records.append(req)
            
    db.add_all(records)
    db.commit()
    print(f"✅ Added {len(records)} historical records covering 120 days.")
    db.close()

if __name__ == "__main__":
    seed_history()
