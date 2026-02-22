# src/brain/models.py
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, ForeignKey, DateTime, Boolean, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import declarative_base
import uuid

Base = declarative_base()

class LLMRequest(Base):
    """
    Log of every LLM interaction for audit and cost tracking.
    """
    __tablename__ = 'llm_requests'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nation_id = Column(String(50))
    request_type = Column(String(50))   # 'generate_post', 'reply'
    model_used = Column(String(50))     # 'gemini-1.5-flash'
    prompt_tokens = Column(Integer)
    completion_tokens = Column(Integer)
    total_cost_usd = Column(Float)
    latency_ms = Column(Integer)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

class PromptTemplate(Base):
    """
    Versioned prompts for nations.
    """
    __tablename__ = 'prompt_templates'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True)
    version = Column(Integer, default=1)
    template = Column(Text, nullable=False)
    variables = Column(JSONB)
    model_preference = Column(String(50))
    is_active = Column(Boolean, default=True)

class NationGoldenExample(Base):
    """
    The 'Few-Shot' examples injected to prevent drift.
    """
    __tablename__ = 'nation_golden_examples'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nation_id = Column(String(50))
    content = Column(Text, nullable=False)
    style_category = Column(String(50)) # 'sarcastic', 'diplomatic'

class CostTracker(Base):
    """
    Daily budget enforcement.
    """
    __tablename__ = 'cost_tracker'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    date = Column(String(10)) # YYYY-MM-DD
    total_cost_usd = Column(Float, default=0.0)
    budget_limit_usd = Column(Float, default=10.0) # Safety stop
    
    __table_args__ = (UniqueConstraint('date', name='uniq_daily_cost'),)
