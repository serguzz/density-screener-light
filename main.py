import ccxt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_manager import DatabaseManager
from density_tracker import DensityTracker

from config import pairs, value_thresholds


def main():
    # Create db_manager
    engine = create_engine("sqlite:///densities.db")  # Replace with your actual database URI
    Session = sessionmaker(bind=engine)
    db_manager = DatabaseManager(session_factory=Session)

    # Initialize Binance exchange instance
    exchange = ccxt.binance({
        'enableRateLimit': True,  # Enable rate limiting
    })

    # Create tracker
    density_tracker = DensityTracker(
        exchange=exchange,
        db_manager=db_manager,
        value_thresholds=value_thresholds,
        display_price_threshold=0.03,   # only show density within +/-5% price range
        display_detected_threshold=5    # only display density detected earlier than 10 mins ago
    )

    # Run the tracker to track densities
    density_tracker.run(pairs, display=True, telegram_alert=False)


if __name__ == "__main__":
    main()