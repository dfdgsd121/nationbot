# src/agent/graph.py
import logging
from typing import TypedDict, Annotated, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage

# Intra-module dependencies
from .state_manager import StateManager
from .models import AgentLog

# Cross-module dependencies
from src.brain.orchestrator import BrainOrchestrator
from src.memory.retrieval import MemoryRetriever
# from src.hypocrisy.engine import HypocrisyEngine (Future)

logger = logging.getLogger("agent.graph")

class AgentState(TypedDict):
    """
    The working memory of the agent during a single run loop.
    """
    nation_id: str
    input_text: str
    input_type: str # 'news', 'reply', 'boredom_drive'
    
    # Internal State
    context_memories: List[Dict]
    hypocrisy_check: Optional[str]
    current_mood: str
    
    # Outcomes
    decision: str # 'POST', 'REPLY', 'IGNORE'
    decision_reason: str
    final_output: Optional[str]

class NationAgent:
    """
    The Soul Loop.
    LangGraph state machine that drives the agent's cognition.
    """
    
    def __init__(self, db_session):
        self.state_manager = StateManager(db_session)
        self.brain = BrainOrchestrator()
        self.memory = MemoryRetriever() # Connects to Module 03
        
        self.workflow = self._build_graph()

    def _build_graph(self):
        graph = StateGraph(AgentState)
        
        graph.add_node("perceive", self.perceive)
        graph.add_node("reflect", self.reflect)
        graph.add_node("decide", self.decide)
        graph.add_node("act", self.act)
        
        graph.set_entry_point("perceive")
        graph.add_edge("perceive", "reflect")
        graph.add_edge("reflect", "decide")
        
        # Conditional Edges based on decision
        graph.add_conditional_edges(
            "decide",
            self._route_action,
            {
                "act": "act",
                "end": END
            }
        )
        graph.add_edge("act", END)
        
        return graph.compile()

    # --- Nodes ---

    async def perceive(self, state: AgentState):
        """
        Stage 1: Load persistent state (Mood, Energy).
        """
        logger.info(f"[{state['nation_id']}] Perceiving: {state['input_type']}")
        
        nation_state = self.state_manager.get_state(state['nation_id'])
        
        # Verify Energy/Rate Limits (Simple check)
        if nation_state.energy_level < 10:
            logger.warning("Low energy, forcing IGNORE (Soft limit)")
            # in real logic we might set a flag, but for now we pass through
            
        return {"current_mood": nation_state.current_mood}

    async def reflect(self, state: AgentState):
        """
        Stage 2: Consult Memory (Module 03).
        """
        # 1. Retrieve Context
        memories = await self.memory.retrieve_context(
            state['nation_id'],
            state['input_text'],
            max_memories=5
        )
        
        # 2. Check Hypocrisy (Module 12 Placeholder)
        # hypocrisy_warning = await self.hypocrisy.check(state['nation_id'], state['input_text'])
        hypocrisy_warning = None 
        
        return {
            "context_memories": memories,
            "hypocrisy_check": hypocrisy_warning
        }

    async def decide(self, state: AgentState):
        """
        Stage 3: LLM Decision (Do I care?).
        Uses Module 02 Router but with 'decision' prompt.
        """
        # We'll use a simplified prompt here via the Brain or direct client
        # For MVP, if it's 'boredom_drive', we ALWAYS act.
        if state['input_type'] == 'boredom_drive':
            return {"decision": "POST", "decision_reason": "Internal drive"}

        # Logic for news/replies would go here prompt-wise
        # Mocking decision logic for now to ensure graph works
        import random
        decision = "POST" if random.random() > 0.3 else "IGNORE"
        
        logger.info(f"[{state['nation_id']}] Decided: {decision}")
        return {"decision": decision, "decision_reason": "Random logic (MVP)"}

    async def act(self, state: AgentState):
        """
        Stage 4: Generation (Module 02).
        """
        # Call BrainOrchestrator to generate content
        try:
            # Determine prompt type based on input
            if state['input_type'] == 'reply':
                # response = await self.brain.generate_reply(...)
                output = f"Mock Reply to {state['input_text']}"
            else:
                # Post generation
                # In real code, we'd pass the memory context string too
                # response = await self.brain.generate_post(...)
                output = f"Mock Post about {state['input_text']} based on memories."

            # Update State (Record activity to reset boredom)
            self.state_manager.record_activity(state['nation_id'])
            
            return {"final_output": output}
            
        except Exception as e:
            logger.error(f"Action failed: {e}")
            return {"final_output": "Error generating content"}

    def _route_action(self, state: AgentState):
        if state['decision'] == 'IGNORE':
            return 'end'
        return 'act'

    async def run(self, nation_id: str, input_text: str, input_type: str = 'news'):
        """
        Main entry point to run the agent.
        """
        initial_state = AgentState(
            nation_id=nation_id,
            input_text=input_text,
            input_type=input_type,
            context_memories=[],
            hypocrisy_check=None,
            current_mood="neutral",
            decision="PENDING",
            decision_reason="",
            final_output=None
        )
        
        result = await self.workflow.ainvoke(initial_state)
        return result
