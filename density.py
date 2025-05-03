from sqlalchemy import Column, Float, String, DateTime, Integer, create_engine, UniqueConstraint
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Base class for declarative models
Base = declarative_base()

# Density model for SQLAlchemy
class Density(Base):
    """SQLAlchemy model for storing order book densities"""
    __tablename__ = 'densities'
    
    pair = Column(String, primary_key=True, nullable=False)
    price = Column(Float, primary_key=True, nullable=False)
    side = Column(String, nullable=False)
    size = Column(Float, nullable=False)
    worth = Column(Float, nullable=False)
    spread_price = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('pair', 'price', name='uix_pair_price'),
    )
    
    def __repr__(self):
        return f"<Density(pair={self.pair}, side={self.side}, price={self.price}, "
        f"size={self.size}, worth={self.worth}, spread_price={self.spread_price}, time={self.timestamp})>"