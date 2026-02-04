
import logging
from app.database.connection import engine, Base
# Import all models to ensure they are registered with Base.metadata
from app.database.models import Team, App, Agent, GenAIRequest, Model, Alert, Recommendation, RefreshToken, User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    logger.info("Creating database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info(" Tables created successfully!")
    except Exception as e:
        logger.error(f"Error creating tables: {e}")

if __name__ == "__main__":
    init_db()
