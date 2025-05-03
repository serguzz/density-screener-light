from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_manager import DatabaseManager
import config


def main():
    # Create db_manager

    engine = create_engine("sqlite:///densities.db")  # Replace with your actual database URI
    Session = sessionmaker(bind=engine)
    db_manager = DatabaseManager(session_factory=Session)