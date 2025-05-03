from density import Density
from datetime import datetime


class DatabaseManager:
    def __init__(self, session_factory):
        self.Session = session_factory

    def fetch_densities(self, pair=None):
        """Fetch all densities for a specific pair."""
        session = self.Session()
        try:
            condition = Density.pair == pair if pair else True
            densities = session.query(Density).filter(condition).order_by(Density.pair.asc(), Density.price.desc()).all()
            # densities = query.order_by(Density.pair.asc(), Density.price.desc()).all()
            return densities
        except Exception as e:
            print(f"Error fetching densities: {e}")
            return []
        finally:
            session.close()

    def update_density(self, density, side=None, size=None, worth=None, spread_price=None):
        """Update an existing density."""
        session = self.Session()
        existing_density = session.query(Density).filter_by(pair=density.pair, side=density.side, price=density.price).first()
        try:
            if side is not None:
                existing_density.side = side
            if size is not None:
                existing_density.size = size
            if worth is not None:
                existing_density.worth = worth
            if spread_price is not None:
                existing_density.spread_price = spread_price
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"Error updating density: {e}")
        finally:
            session.close()

    def delete_density(self, density):
        """Delete a density."""
        session = self.Session()
        try:
            session.delete(density)
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"Error deleting density: {e}")
        finally:
            session.close()

    def add_density(self, pair, side, price, size, worth, spread_price):
        """Add a new density to the database."""
        session = self.Session()
        try:
            density = Density(
                pair=pair,
                side=side,
                price=price,
                size=size,
                worth=worth,
                spread_price=spread_price,
                timestamp=datetime.utcnow()
            )
            session.add(density)
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"Error adding density: {e}")
        finally:
            session.close()
