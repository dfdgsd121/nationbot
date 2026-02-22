# src/oracle/models.py
from datetime import datetime
from sqlalchemy import Column, String, Boolean, Integer, DateTime, ForeignKey, ARRAY, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import declarative_base, relationship
import uuid

Base = declarative_base()

class OfficialSource(Base):
    """
    Represents an official news source (e.g. White House RSS).
    """
    __tablename__ = 'official_sources'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    url = Column(String(500), nullable=False)
    country_code = Column(String(3))          # ISO code, e.g. USA
    category = Column(String(50))             # politics, economy, etc.
    fetch_interval_minutes = Column(Integer, default=15)
    last_fetched_at = Column(DateTime(timezone=True))
    velocity_override = Column(Boolean, default=False) # True if currently in "Panic Search" mode
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationships
    feed_items = relationship("FeedItem", back_populates="source")

class FeedItem(Base):
    """
    Individual news item ingested from a source.
    """
    __tablename__ = 'feed_items'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_id = Column(UUID(as_uuid=True), ForeignKey('official_sources.id'))
    title = Column(Text, nullable=False)
    summary = Column(Text)
    url = Column(Text, nullable=False, unique=True)
    published_at = Column(DateTime(timezone=True))
    category = Column(String(50))
    keywords = Column(ARRAY(String))
    is_breaking = Column(Boolean, default=False) # Marked True if triggered by Velocity Monitor
    triggered_reactions = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    source = relationship("OfficialSource", back_populates="feed_items")
