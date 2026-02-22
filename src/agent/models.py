# src/agent/models.py
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, Float, ARRAY
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import declarative_base
import uuid

Base = declarative_base()

class NationState(Base):
    """
    Persistent state of a Nation Agent.
    Tracks mood, energy, and critical 'Boredom' metrics for internal drive.
    """
    __tablename__ = 'nation_states'

    nation_id = Column(String(50), primary_key=True) # e.g. 'USA'
    current_mood = Column(String(50), default='neutral') # aggressive, diplomatic, happy
    energy_level = Column(Integer, default=100) # 0-100, limits posting freq
    last_active_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Boredom Engine Stats
    boredom_score = Column(Integer, default=0)       # Increases over time
    boredom_threshold = Column(Integer, default=70) # Trigger point for self-expression

    active_conversations = Column(ARRAY(UUID(as_uuid=True))) # Tracking reply threads to avoid infinite loops
    public_metrics = Column(JSONB) # {'gdp': 23000, 'stability': 85}
    private_goals = Column(ARRAY(Text)) # ['Pass trade deal', 'Provoke France']
    
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class AgentLog(Base):
    """
    Audit log of the 'Soul Loop'. 
    Records what the agent perceived, thought, and did.
    """
    __tablename__ = 'agent_logs'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nation_id = Column(String(50))
    event_type = Column(String(50)) # 'decision_made', 'boredom_trigger', 'post_generated'
    input_context = Column(Text)
    thought_process = Column(Text)
    action_taken = Column(Text)
    execution_time_ms = Column(Integer)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
