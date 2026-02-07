
import sys
import os

# Add backend directory to path
sys.path.append(os.path.abspath("backend/analytics-api"))

try:
    print("Importing app.database.models...")
    from app.database import models
    print("✅ app.database.models imported successfully.")
    
    print("Importing app.routes.dashboard...")
    from app.routes import dashboard
    print("✅ app.routes.dashboard imported successfully.")
    
    print("Importing app.models.schemas...")
    from app.models import schemas
    print("✅ app.models.schemas imported successfully.")
    
    print("Importing app.models.agent_schemas...")
    from app.models import agent_schemas
    print("✅ app.models.agent_schemas imported successfully.")

except Exception as e:
    print(f"❌ Import failed: {e}")
    import traceback
    traceback.print_exc()
