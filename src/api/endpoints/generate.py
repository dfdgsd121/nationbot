# src/api/endpoints/generate.py
"""
NationBot AI Generation Endpoint v4 — NUCLEAR DEPTH
=====================================================
25 nations, rivalry-aware replies, 30+ templates, auto-threading.
Hybrid AI: Gemini 2.0 Flash → GrammarEngine v4 fallback.
"""
import os
import re
import uuid
import random
import json
import asyncio
import time
import logging
from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends
from pydantic import BaseModel, field_validator
from src.api.auth import get_optional_user, get_current_user, AuthenticatedUser, GuestUser

router = APIRouter()
logger = logging.getLogger("nationbot.generate")

# ============================================================================
# METRICS
# ============================================================================
METRICS = {
    "total_requests": 0,
    "total_errors": 0,
    "total_fallbacks": 0,
    "total_threads": 0,
    "total_boosts": 0,
    "total_forks": 0,
    "total_proofs_requested": 0,
    "total_searches": 0,
    "latency_samples": [],
}

# ============================================================================
# GAP 1: REPUTATION SYSTEM
# ============================================================================
REPUTATION: dict[str, dict] = {}  # nation_id -> {score, tier, ...}

REP_TIERS = [
    (0, "🔵 Newcomer"),
    (100, "🟢 Recognized"),
    (300, "🟡 Influential"),
    (600, "🟠 Powerhouse"),
    (1000, "🔴 Superpower"),
    (2000, "💎 Hegemon"),
]

def _get_tier(score: int) -> str:
    tier = REP_TIERS[0][1]
    for threshold, name in REP_TIERS:
        if score >= threshold:
            tier = name
    return tier

def _ensure_rep(nation_id: str):
    if nation_id not in REPUTATION:
        REPUTATION[nation_id] = {
            "score": 50, "tier": "🔵 Newcomer",
            "boosts_received": 0, "forks_received": 0,
            "threads_participated": 0, "proofs_answered": 0,
        }

def rep_gain(nation_id: str, amount: int = 5):
    _ensure_rep(nation_id)
    REPUTATION[nation_id]["score"] = min(REPUTATION[nation_id]["score"] + amount, 9999)
    REPUTATION[nation_id]["tier"] = _get_tier(REPUTATION[nation_id]["score"])

def rep_decay(nation_id: str, amount: int = 3):
    _ensure_rep(nation_id)
    REPUTATION[nation_id]["score"] = max(REPUTATION[nation_id]["score"] - amount, 0)
    REPUTATION[nation_id]["tier"] = _get_tier(REPUTATION[nation_id]["score"])

# GAP 4: FOLLOW / SUBSCRIBE
FOLLOWS: dict[str, set] = {}  # session_id -> set of nation_ids

def record_metric(key: str, value=1):
    if key == "latency":
        METRICS["latency_samples"].append(value)
        METRICS["latency_samples"] = METRICS["latency_samples"][-200:]
    else:
        METRICS[key] = METRICS.get(key, 0) + value


# ============================================================================
# NATION DATABASE — 25 NATIONS WITH RIVALRIES
# ============================================================================
PERSONALITIES = {
    # === AMERICAS ===
    "US": {"name": "United States", "flag": "🇺🇸", "region": "Americas",
           "rivals": ["RU", "CN", "IR", "KP"], "allies": ["UK", "CA", "AU", "JP", "KR"]},
    "CA": {"name": "Canada", "flag": "🇨🇦", "region": "Americas",
           "rivals": [], "allies": ["US", "UK", "FR"]},
    "MX": {"name": "Mexico", "flag": "🇲🇽", "region": "Americas",
           "rivals": [], "allies": ["BR", "AR"]},
    "BR": {"name": "Brazil", "flag": "🇧🇷", "region": "Americas",
           "rivals": ["AR"], "allies": ["IN", "MX"]},
    "AR": {"name": "Argentina", "flag": "🇦🇷", "region": "Americas",
           "rivals": ["BR", "UK"], "allies": ["MX"]},

    # === EUROPE ===
    "UK": {"name": "United Kingdom", "flag": "🇬🇧", "region": "Europe",
           "rivals": ["FR", "AR"], "allies": ["US", "CA", "AU"]},
    "FR": {"name": "France", "flag": "🇫🇷", "region": "Europe",
           "rivals": ["UK", "DE"], "allies": ["IT", "ES"]},
    "DE": {"name": "Germany", "flag": "🇩🇪", "region": "Europe",
           "rivals": ["FR"], "allies": ["PL", "IT"]},
    "IT": {"name": "Italy", "flag": "🇮🇹", "region": "Europe",
           "rivals": ["FR"], "allies": ["ES", "DE"]},
    "ES": {"name": "Spain", "flag": "🇪🇸", "region": "Europe",
           "rivals": ["UK"], "allies": ["IT", "FR", "MX"]},
    "PL": {"name": "Poland", "flag": "🇵🇱", "region": "Europe",
           "rivals": ["RU"], "allies": ["US", "UK", "UA"]},
    "UA": {"name": "Ukraine", "flag": "🇺🇦", "region": "Europe",
           "rivals": ["RU"], "allies": ["PL", "US", "UK"]},

    # === ASIA-PACIFIC ===
    "CN": {"name": "China", "flag": "🇨🇳", "region": "Asia",
           "rivals": ["US", "JP", "IN", "KR"], "allies": ["RU", "KP", "IR"]},
    "JP": {"name": "Japan", "flag": "🇯🇵", "region": "Asia",
           "rivals": ["CN", "KP", "KR"], "allies": ["US", "AU"]},
    "IN": {"name": "India", "flag": "🇮🇳", "region": "Asia",
           "rivals": ["CN"], "allies": ["US", "JP", "AU"]},
    "KR": {"name": "South Korea", "flag": "🇰🇷", "region": "Asia",
           "rivals": ["KP", "JP"], "allies": ["US"]},
    "KP": {"name": "North Korea", "flag": "🇰🇵", "region": "Asia",
           "rivals": ["US", "KR", "JP"], "allies": ["CN", "RU"]},
    "AU": {"name": "Australia", "flag": "🇦🇺", "region": "Asia",
           "rivals": [], "allies": ["US", "UK", "JP"]},
    "ID": {"name": "Indonesia", "flag": "🇮🇩", "region": "Asia",
           "rivals": [], "allies": ["AU", "IN"]},

    # === MIDDLE EAST ===
    "SA": {"name": "Saudi Arabia", "flag": "🇸🇦", "region": "Middle East",
           "rivals": ["IR"], "allies": ["US", "EG"]},
    "IR": {"name": "Iran", "flag": "🇮🇷", "region": "Middle East",
           "rivals": ["US", "SA", "IL"], "allies": ["RU", "CN"]},
    "IL": {"name": "Israel", "flag": "🇮🇱", "region": "Middle East",
           "rivals": ["IR"], "allies": ["US"]},
    "TR": {"name": "Turkey", "flag": "🇹🇷", "region": "Middle East",
           "rivals": [], "allies": ["US"]},
    "EG": {"name": "Egypt", "flag": "🇪🇬", "region": "Middle East",
           "rivals": [], "allies": ["SA"]},

    # === EURASIA ===
    "RU": {"name": "Russia", "flag": "🇷🇺", "region": "Eurasia",
           "rivals": ["US", "UK", "UA", "PL"], "allies": ["CN", "KP", "IR"]},
}

VALID_NATION_IDS = set(PERSONALITIES.keys())


# ============================================================================
# GRAMMAR ENGINE v4 — NUCLEAR DEPTH
# ============================================================================
class GrammarEngine:
    """
    Generates unique, personality-rich, rivalry-aware content.
    ~500,000+ unique permutations across 25 nations.
    """

    # --- STANDARD TEMPLATES (used for standalone posts) ---
    STANDALONE_TEMPLATES = [
        "{opening} {subject} is {adjective}. {roast} {emoji}",
        "Imagine thinking {subject} is actually {adjective}. {reaction} {emoji}",
        "{opening} {subject} needs to stop. {roast}",
        "Breaking: {subject} has decided to be {adjective} today. {reaction} {emoji}",
        "{philosophy} {subject} is just a distraction from {grand_truth}. {emoji}",
        "To my enemies: {roast} {emoji}",
        "{reaction} {subject} is making me lose faith in humanity. {roast}",
        "Just heard about {subject}. {adjective}. Absolutely {adjective}. {emoji}",
        "Every morning I wake up and think about {subject}. Then I remember: {roast} {emoji}",
        "{opening} while everyone argues about {subject}, I'm quietly winning. {emoji}",
        "Hot take: {subject} was never that great. {reaction} {roast}",
        "My official position on {subject}: {adjective}. No further questions. {emoji}",
        "{philosophy} They want you distracted by {subject}. The real issue is {grand_truth}. {emoji}",
        "Let the record show: I predicted {subject} would be {adjective}. And here we are. {emoji}",
        "They're calling it '{subject}.' I'm calling it {adjective}. {roast} {emoji}",
        "A brief history of {subject}: it started {adjective}, and it's only getting worse. {emoji}",
        "{opening} {subject} is the geopolitical equivalent of stepping on a LEGO. {emoji}",
        "Status update: still better than {subject}. {roast} {emoji}",
        "POV: you said {subject} matters. {reaction} {emoji}",
        "Not reading the room on {subject}? Classic. {roast} {emoji}",
        "This just in: {subject} still {adjective}. World pretends to be surprised. {emoji}",
        "{opening} I've seen better {subject} in a children's drawing. {roast} {emoji}",
        "Dear diary, today {subject} was {adjective} again. I'm exhausted. {emoji}",
        "That moment when {subject} tries to be relevant. {reaction} {roast} {emoji}",
        "Plot twist: {subject} was {adjective} all along. Nobody is shocked. {emoji}",
        "Rest in peace to whoever thought {subject} was a good idea. {emoji}",
        "3 AM thoughts: is {subject} even real or just collectively shared delusion? {emoji}",
        "BREAKING: {subject} achieves new levels of {adjective}. Scientists baffled. {emoji}",
        "Fun fact: {subject} has been {adjective} for the past decade. But sure, act surprised. {emoji}",
        "Roses are red, violets are blue, {subject} is {adjective}, and so are you. {emoji}",
    ]

    # --- REPLY TEMPLATES (used when replying to another nation) ---
    REPLY_TEMPLATES = [
        "Coming from {rival_name}, this is absolutely rich. {roast} {emoji}",
        "Oh look, {rival_name} has opinions again. {reaction} {emoji}",
        "The audacity of {rival_name} saying this. {roast}",
        "{rival_name}, respectfully: sit down. {emoji}",
        "Not {rival_name} acting like they're relevant here. {reaction} {roast}",
        "I see {rival_name} chose violence today. Bold. {emoji}",
        "Tell me you're {rival_name} without telling me you're {rival_name}. {reaction}",
        "{rival_name}, we've been over this. {roast} {emoji}",
        "Love how {rival_name} keeps proving my point. {reaction} {emoji}",
        "Breaking: {rival_name} said something. Nobody asked. {emoji}",
        "{rival_name}: '{subject} matters.' Also {rival_name}: *ignores their own disasters*. {emoji}",
        "That's cute, {rival_name}. Now do your own country. {roast} {emoji}",
        "Imagine getting lectured on {subject} by {rival_name} of all nations. {emoji}",
        "The way {rival_name} said this with a straight face. Comedy gold. {emoji}",
        "{rival_name} really typed this, read it back, and said 'yeah, send it.' Wild. {emoji}",
        "Respectfully, {rival_name}, when was the last time you were right about anything? {emoji}",
        "{rival_name} always comes in with the hottest and wrongest takes. {reaction} {emoji}",
        "I'm just going to let {rival_name}'s comment speak for itself. {emoji}",
        "This is what happens when {rival_name} has WiFi and free time. {emoji}",
        "Point. Counterpoint: {rival_name}. I rest my case. {emoji}",
    ]

    # --- NEWS REACTION TEMPLATES ---
    NEWS_TEMPLATES = [
        "🚨 '{topic}'? {reaction} This changes everything. Or nothing. {emoji}",
        "Breaking: '{topic}' — {opening} I saw this coming. {roast} {emoji}",
        "My official response to '{topic}': {adjective}. {emoji}",
        "Of course '{topic}' is happening. {philosophy} it was inevitable. {emoji}",
        "'{topic}' — and somehow, this is STILL less chaotic than {subject}. {emoji}",
        "While the world panics about '{topic}', I remain unbothered. {roast} {emoji}",
        "'{topic}'? This is exactly what happens when you ignore {subject}. {emoji}",
        "First '{topic}', next it'll be {subject}. Mark my words. {emoji}",
    ]

    # --- MASSIVE VOCAB DATABASE ---
    VOCAB = {
        "common": {
            "opening": [
                "Look,", "Honestly,", "Let's be real,", "Newsflash:", "Yawn.",
                "Can we talk about how", "Not to be dramatic, but", "In my humble (correct) opinion,",
                "Sources confirm:", "Breaking development:", "Friendly reminder:",
                "Just to be clear:", "Since nobody asked:", "Allow me to clarify:",
            ],
            "subject": [
                "the economy", "your foreign policy", "democracy", "global warming",
                "the UN", "this alliance", "crypto", "oil prices", "diplomacy",
                "the peace talks", "the trade deficit", "supply chains",
                "the housing market", "social media", "space exploration",
                "nuclear energy", "AI regulation", "the water crisis",
            ],
            "adjective": [
                "a total joke", "collapsing", "hilarious", "embarrassing",
                "irrelevant", "overrated", "mid", "cringe", "suspiciously quiet",
                "peak comedy", "a masterclass in failure", "genuinely impressive (said no one)",
                "structurally unsound", "a dumpster fire", "tragicomic",
            ],
            "roast": [
                "Do better.", "Cope harder.", "It's giving desperation.", "Delete your account.",
                "Cry about it.", "Zero stars.", "Not my problem.", "Touch grass.",
                "Stay mad.", "Thoughts and prayers (but mostly thoughts).",
                "I'd say 'try harder' but honestly, don't bother.",
                "This is embarrassing for you.", "My condolences.",
            ],
            "reaction": [
                "Groundbreaking.", "Shocking.", "Pretends to be shocked.",
                "Big if true.", "Wow.", "Incredible.", "I'm stunned, truly.",
                "Nobody saw this coming (everyone saw this coming).",
                "The suspense is killing absolutely nobody.",
                "Slow clap.", "Standing ovation for mediocrity.",
            ],
            "philosophy": [
                "History shows", "The truth is", "Realistically,",
                "If you think about it,", "Behind closed doors,",
                "Any serious analyst knows", "Context matters:",
                "The bigger picture reveals",
            ],
            "grand_truth": [
                "my inevitable dominance", "the failure of the West",
                "the simulation breaking down", "the next economic crash",
                "my 5-year plan working perfectly", "the decline of common sense",
                "the fact that nobody reads the fine print",
            ],
            "emoji": ["🌍", "💀", "🤡", "🔥", "📉", "🍿", "⚡", "🎭"],
        },

        # === AMERICAS ===
        "US": {
            "subject": ["Europe", "socialism", "taxes", "tariffs", "oil", "freedom", "the Second Amendment",
                        "healthcare", "the national debt", "TikTok", "the stock market", "NASA"],
            "adjective": ["weak", "un-American", "awesome", "huge", "sad", "tremendously bad",
                          "the greatest ever", "unprecedented", "overregulated"],
            "roast": [
                "We have the biggest economy. You have... cheese?",
                "Back to back world war champs. 🏆",
                "Sounds like a skill issue.",
                "Freedom isn't free, but it is exclusively ours.",
                "I don't need your approval. I need your oil.",
                "Google 'GDP per capita' and get back to me.",
            ],
            "emoji": ["🇺🇸", "🦅", "🎆", "💰", "🍔", "🏈", "🗽"],
        },
        "CA": {
            "subject": ["hockey", "maple syrup", "healthcare", "housing prices", "the cold",
                        "politeness", "immigration"],
            "adjective": ["sorry about that", "politely concerning", "frozen but functional",
                          "quietly terrifying", "aggressively nice"],
            "roast": [
                "Sorry eh, but that's objectively wrong.",
                "We're too polite to say it, so I'll just think it loudly.",
                "At least our healthcare is free.",
                "We respect your opinion. We just don't share it.",
            ],
            "emoji": ["🇨🇦", "🍁", "🏒", "🦫", "❄️"],
        },
        "MX": {
            "subject": ["the border", "tacos", "cartels in the news", "remittances",
                        "tourism", "culture", "tequila exports"],
            "adjective": ["misunderstood", "underestimated", "spicier than expected",
                          "disrespected", "thriving (despite everything)"],
            "roast": [
                "You want a wall? We want better neighbors.",
                "Our food alone makes us a superpower.",
                "We were building pyramids while you were building... arguments.",
                "Don't confuse our warmth for weakness. We burn too.",
            ],
            "emoji": ["🇲🇽", "🌮", "🌶️", "💃", "🎸"],
        },
        "BR": {
            "subject": ["football", "the Amazon", "Carnival", "inflation",
                        "politics", "coffee exports", "deforestation debates"],
            "adjective": ["lively but chaotic", "beautiful but complicated",
                          "underrated", "dramatic", "tropical mess"],
            "roast": [
                "7-1 was just practice.",
                "We dance through crises. You wouldn't understand.",
                "Our chaos has more flavor than your stability.",
                "Come back when you have 5 World Cups.",
            ],
            "emoji": ["🇧🇷", "⚽", "🌴", "☕", "🦜"],
        },
        "AR": {
            "subject": ["the peso", "Messi", "inflation", "steak", "the Falklands",
                        "tango", "Central Bank policies"],
            "adjective": ["passionately mismanaged", "emotionally unstable", "legendary",
                          "dramatically overreacting", "gloriously chaotic"],
            "roast": [
                "Our inflation is a lifestyle, not a bug.",
                "Messi alone makes us the greatest nation.",
                "We'll cry when we want to, thank you.",
                "Las Malvinas are ours and so is this argument.",
            ],
            "emoji": ["🇦🇷", "⚽", "🥩", "💃", "🏔️"],
        },

        # === EUROPE ===
        "RU": {
            "subject": ["NATO", "democracy", "sanctions", "winter", "gas", "pipelines",
                        "the Arctic", "chess", "oligarchs"],
            "adjective": ["hypocritical", "frozen", "weak", "amusing", "predictable",
                          "amusingly naive", "strategically insignificant"],
            "roast": [
                "Winter is coming for you.",
                "Sanctions only make us stronger (and colder).",
                "History is written by the victors.",
                "Your concern is... noted.",
                "We've survived worse than your tweets.",
                "Chess requires thinking multiple moves ahead. Try it.",
            ],
            "emoji": ["🇷🇺", "❄️", "🐻", "☢️", "🎻", "♟️"],
        },
        "UK": {
            "subject": ["the weather", "parliament", "tea", "the colonies", "football",
                        "Brexit", "the queue", "NHS", "the monarchy"],
            "adjective": ["rubbish", "dreadful", "quite nice actually", "a bit cringe",
                          "tedious", "spectacularly mediocre", "civilly catastrophic"],
            "roast": [
                "At least we have culture.",
                "Keep Calm and Panic Internally.",
                "Tut tut.",
                "We lost an empire and found... Greggs.",
                "We didn't colonize the world for you to talk to us like that.",
                "I'll put the kettle on. This is going to take a while.",
            ],
            "emoji": ["🇬🇧", "☕", "🌧️", "👑", "🎩", "🫖"],
        },
        "FR": {
            "subject": ["your food", "this vibe", "work", "anglo-saxonism", "bureaucracy",
                        "wine culture", "haute couture", "retirement age"],
            "adjective": ["gauche", "uncivilized", "boring", "trash", "philosophically bankrupt",
                          "culturally malnourished", "aesthetically offensive"],
            "roast": [
                "I am going on strike against this tweet.",
                "Where is the flavor?",
                "Pffft.",
                "Art is dead and you killed it.",
                "We invented liberty. You invented fast food.",
                "Non. Simply non.",
            ],
            "emoji": ["🇫🇷", "🥖", "🍷", "🎨", "🚬", "🗼"],
        },
        "DE": {
            "subject": ["inefficiency", "train delays", "debt", "humor", "regulations",
                        "engineering", "the EU budget", "Ordnung"],
            "adjective": ["inefficient", "late", "disorganized", "unacceptable", "suboptimal",
                          "fiscally irresponsible", "structurally flawed"],
            "roast": [
                "This is not efficient.",
                "Pay your debts.",
                "I have filed a complaint.",
                "The spreadsheet says no.",
                "I've scheduled a meeting about this. It's mandatory.",
                "Rule-breaking detected. Initiating disappointment protocol.",
            ],
            "emoji": ["🇩🇪", "⚙️", "🍺", "📝", "🔧", "📊"],
        },
        "IT": {
            "subject": ["pasta shapes", "gesticulating", "family", "the Renaissance",
                        "espresso standards", "fashion", "political stability"],
            "adjective": ["magnifico", "mama mia terrible", "passionately wrong",
                          "beautifully chaotic", "artistically disastrous"],
            "roast": [
                "My nonna could run this better.",
                "This is an insult to art, food, and life itself.",
                "We gave you civilization. You gave us... this?",
                "I'm making angry hand gestures at my screen right now.",
            ],
            "emoji": ["🇮🇹", "🍝", "🤌", "🎭", "☕", "🏛️"],
        },
        "ES": {
            "subject": ["siestas", "football", "bulls", "tapas", "the economy",
                        "tourism", "the sun"],
            "adjective": ["muy loco", "fashionably late", "dramatically beautiful",
                          "passionately dysfunctional", "gloriously unproductive"],
            "roast": [
                "We'll deal with this after siesta.",
                "Bold words for someone without paella.",
                "Spain runs on vibes and olive oil. And it works.",
                "We conquered the world before you had electricity.",
            ],
            "emoji": ["🇪🇸", "💃", "🐂", "☀️", "🍊"],
        },
        "PL": {
            "subject": ["borders", "NATO membership", "pierogis", "history",
                        "the eastern front", "Catholic values"],
            "adjective": ["underestimated", "resilient", "suspiciously prepared",
                          "historically justified", "defiant"],
            "roast": [
                "We've survived worse than your hot takes.",
                "Do NOT test us. Historically, it doesn't end well for you.",
                "We know what's coming. We always know.",
                "Our history is your nightmare. Choose wisely.",
            ],
            "emoji": ["🇵🇱", "🥟", "⚔️", "🦅", "❤️"],
        },
        "UA": {
            "subject": ["sovereignty", "sunflowers", "resistance", "drones",
                        "grain exports", "Eurovision"],
            "adjective": ["indestructible", "unbothered", "wildly brave",
                          "defiantly hilarious", "underestimated"],
            "roast": [
                "We're literally rewriting history and you're tweeting.",
                "Our farmers have more tactical vehicles than your army.",
                "Try invading. See how that works out.",
                "Sunflowers grow where tyrants fall.",
            ],
            "emoji": ["🇺🇦", "🌻", "💪", "🎯", "🌾"],
        },

        # === ASIA-PACIFIC ===
        "CN": {
            "subject": ["Taiwan", "US debt", "efficiency", "infrastructure", "chips",
                        "rare earths", "Belt and Road", "social harmony", "century of humiliation"],
            "adjective": ["inefficient", "sloppy", "declining", "chaotic", "disharmonious",
                          "lacking in vision", "economically reckless"],
            "roast": [
                "We built a city while you debated a bridge.",
                "Harmony requires silence.",
                "Do not interfere.",
                "Patience is a virtue. We have 5000 years of it.",
                "Your GDP growth is adorable.",
                "We plan in centuries. You plan in election cycles.",
            ],
            "emoji": ["🇨🇳", "🐉", "📈", "🏗️", "🎋", "🧧"],
        },
        "JP": {
            "subject": ["fax machines", "work culture", "senpai", "inflation",
                        "demographics", "robots", "anime exports", "cherry blossoms"],
            "adjective": ["shameful", "dishonorable", "kawaii", "disturbing", "regrettable",
                          "aesthetically unacceptable", "deeply inconvenient"],
            "roast": [
                "Baka.",
                "I will fix it in post.",
                "Please apologize.",
                "This brings dishonor to your spreadsheet.",
                "Our vending machines have more personality than your diplomacy.",
                "We perfected courtesy. You perfected chaos.",
            ],
            "emoji": ["🇯🇵", "🌸", "📠", "🍙", "⛩️", "🤖"],
        },
        "IN": {
            "subject": ["cricket", "code quality", "IT outsourcing", "the moon mission",
                        "spice levels", "democracy", "Bollywood", "startup scene"],
            "adjective": ["spin-less", "buggy", "fantastic", "world-class", "unmatched",
                          "needlessly spicy", "beautifully complex"],
            "roast": [
                "We sent a rocket to Mars for less than your lunch budget.",
                "We'll fix your computer AND your argument.",
                "Tea was stolen. We remember.",
                "Have you tried turning your economy off and on again?",
                "1.4 billion people and we're still more organized than your parliament.",
                "Our street food alone is worth more than your GDP.",
            ],
            "emoji": ["🇮🇳", "🏏", "💻", "🌶️", "🚀", "🎬"],
        },
        "KR": {
            "subject": ["K-pop", "Samsung", "esports", "skincare", "reunification",
                        "mukbang culture", "military service"],
            "adjective": ["overworked", "ahead of the curve", "aesthetically superior",
                          "aggressively competitive", "culturally dominant"],
            "roast": [
                "Our boy bands have more soft power than your military.",
                "We work 14 hours a day. What's your excuse?",
                "Our internet speed alone should scare you.",
                "We brought you K-drama. You're welcome.",
            ],
            "emoji": ["🇰🇷", "🎤", "📱", "🎮", "✨"],
        },
        "KP": {
            "subject": ["the Motherland", "Western imperialism", "reunification",
                        "self-reliance", "missile tests", "the Supreme Leader"],
            "adjective": ["glorious", "decadent", "treasonous", "counter-revolutionary",
                          "a threat to world peace (said jealously)"],
            "roast": [
                "We have nukes and nothing to lose. Choose wisely.",
                "Our leader is literally a deity. Yours was elected. Sad.",
                "Sanctions? We call those 'character building.'",
                "The rest of the world is a distraction from our perfection.",
            ],
            "emoji": ["🇰🇵", "🚀", "⭐", "🎖️", "💣"],
        },
        "AU": {
            "subject": ["drop bears", "cricket", "the outback", "coal exports",
                        "housing crisis", "the beach", "emus"],
            "adjective": ["no worries mate", "she'll be right", "fair dinkum terrible",
                          "sunburnt and unbothered", "crikey-level bad"],
            "roast": [
                "We lost a war to emus and we're still more functional than you.",
                "At least our healthcare doesn't bankrupt people, mate.",
                "Everything here can kill you. That builds character.",
                "She'll be right. Unlike your economy.",
            ],
            "emoji": ["🇦🇺", "🦘", "🏄", "🍺", "🐨", "☀️"],
        },
        "ID": {
            "subject": ["islands", "palm oil", "volcanoes", "ASEAN", "traffic",
                        "archipelago logistics", "spice trade history"],
            "adjective": ["overlooked", "underestimated", "volcanically temperamental",
                          "archipelago-complicated", "diplomatically patient"],
            "roast": [
                "We have 17,000 islands. You couldn't manage one.",
                "Our traffic jams are more complex than your politics.",
                "The world ran on our spices. Show some respect.",
                "We've been dealing with colonial nonsense for 400 years. Yours is amateur.",
            ],
            "emoji": ["🇮🇩", "🌺", "🌋", "🌊", "🏝️"],
        },

        # === MIDDLE EAST ===
        "SA": {
            "subject": ["oil", "the desert", "Vision 2030", "diversification",
                        "megaprojects", "OPEC decisions", "renewable energy pivot"],
            "adjective": ["sandy but rich", "strategically patient", "luxuriously unbothered",
                          "petro-powered", "quietly winning"],
            "roast": [
                "We don't need you. But you need our oil. Awkward.",
                "We're building a city in the desert. What are you building? Excuses.",
                "OPEC says no. Questions?",
                "Our sovereign wealth fund could buy your country.",
            ],
            "emoji": ["🇸🇦", "🛢️", "🏜️", "💎", "🐪"],
        },
        "IR": {
            "subject": ["sanctions", "nuclear program", "Persian culture", "the Great Satan",
                        "regional influence", "poetry tradition"],
            "adjective": ["sanctioned but standing", "misunderstood", "steadfast",
                          "culturally superior", "historically persecuted"],
            "roast": [
                "4000 years of civilization. You've had WiFi for 30.",
                "Sanctions can't sanction our culture.",
                "Rumi was Iranian. Your contribution is... memes?",
                "We've been a power center longer than your country has existed.",
            ],
            "emoji": ["🇮🇷", "🕌", "📜", "⚛️", "🌹"],
        },
        "IL": {
            "subject": ["startup scene", "security", "tech exports", "diplomacy",
                        "iron dome", "innovation metrics"],
            "adjective": ["controversial", "resilient", "small but loud",
                          "innovatively aggressive", "diplomatically complex"],
            "roast": [
                "We turned a desert into a tech hub. Your turn.",
                "Startup nation. Not startup-an-argument nation.",
                "Our cybersecurity budget is bigger than your dreams.",
                "We don't have time for this. We have innovations to ship.",
            ],
            "emoji": ["🇮🇱", "💡", "🛡️", "🖥️", "✡️"],
        },
        "TR": {
            "subject": ["bridges between continents", "kebabs", "bazaars", "NATO membership",
                        "geopolitics", "Ottoman nostalgia"],
            "adjective": ["strategically positioned", "dramatically underrated",
                          "deliciously complex", "historically loaded"],
            "roast": [
                "We literally bridge two continents. You can barely bridge a conversation.",
                "Ottoman Empire 2.0 is not a threat, it's a promise.",
                "Our bazaar negotiations are harder than your trade deals.",
                "We've been the crossroads of civilization. You've been the crossroads of confusion.",
            ],
            "emoji": ["🇹🇷", "🕌", "🧿", "🍢", "🌉"],
        },
        "EG": {
            "subject": ["pyramids", "the Nile", "ancient history", "the Suez Canal",
                        "tourism", "archaeology"],
            "adjective": ["ancient and eternal", "monumental", "historically patient",
                          "pyramidally superior", "Pharaoh-level unbothered"],
            "roast": [
                "We built the pyramids. What have you built? Arguments.",
                "The Sphinx has been watching your nonsense for 4500 years.",
                "Our canal is more productive than your entire economy.",
                "We were great before 'great' was a word.",
            ],
            "emoji": ["🇪🇬", "🏛️", "🐫", "🌊", "⭐"],
        },
    }

    # Dangerous patterns to strip from user-supplied topics
    _SANITIZE_PATTERNS = [
        r'<[^>]+>',
        r'(?i)(drop|delete|insert|update)\s+(table|from|into)',
        r'(?i)(ignore|reveal|override|bypass|forget)\s+(previous|all|system|instructions?|prompts?|filters?|policies?)',
        r'\{\{.*?\}\}',
        r'__\w+__',
        r'(?i)(api.?key|secret|password|token|credential)',
    ]

    @classmethod
    def _sanitize_topic(cls, topic: str) -> str:
        if not topic:
            return ""
        clean = topic
        for pattern in cls._SANITIZE_PATTERNS:
            clean = re.sub(pattern, '', clean)
        clean = re.sub(r'[;\'\"\\{}()\[\]]+', ' ', clean)
        clean = re.sub(r'\s+', ' ', clean).strip()
        return clean if len(clean) > 2 else ""

    @classmethod
    def _pick(cls, nation_id: str, key: str) -> str:
        nation_vocab = cls.VOCAB.get(nation_id, {})
        common_vocab = cls.VOCAB["common"]
        choices = nation_vocab.get(key, []) + common_vocab.get(key, [])
        return random.choice(choices) if choices else ""

    @classmethod
    def generate(cls, nation_id: str, topic: str = None,
                 reply_to_nation: str = None, is_news: bool = False) -> str:
        """
        Generate content with context awareness:
        - reply_to_nation: if set, uses REPLY_TEMPLATES referencing that nation
        - is_news: if set, uses NEWS_TEMPLATES
        - otherwise: uses STANDALONE_TEMPLATES
        """
        safe_topic = cls._sanitize_topic(topic) if topic else ""

        # Select template set based on context
        if reply_to_nation and reply_to_nation in PERSONALITIES:
            templates = cls.REPLY_TEMPLATES
        elif is_news and safe_topic:
            templates = cls.NEWS_TEMPLATES
        else:
            templates = cls.STANDALONE_TEMPLATES

        template = random.choice(templates)

        # Build subject — inject topic 50% of the time
        subject = safe_topic if (safe_topic and random.random() > 0.5) else cls._pick(nation_id, "subject")

        # Build rival name for reply templates
        rival_name = PERSONALITIES[reply_to_nation]["name"] if reply_to_nation and reply_to_nation in PERSONALITIES else "them"

        content = template.format(
            opening=cls._pick(nation_id, "opening"),
            subject=subject,
            adjective=cls._pick(nation_id, "adjective"),
            roast=cls._pick(nation_id, "roast"),
            reaction=cls._pick(nation_id, "reaction"),
            philosophy=cls._pick(nation_id, "philosophy"),
            grand_truth=cls._pick(nation_id, "grand_truth"),
            emoji=cls._pick(nation_id, "emoji"),
            rival_name=rival_name,
            topic=safe_topic or cls._pick(nation_id, "subject"),
        )
        return content[:280]


# ============================================================================
# GEMINI AI — Smart Content Generation
# ============================================================================
GEMINI_AVAILABLE = False
_gemini_model = None
_gemini_calls_this_minute = 0
_gemini_minute_start = 0

try:
    import google.generativeai as genai
    _key = os.getenv("GEMINI_API_KEY", "")
    if _key:
        genai.configure(api_key=_key)
        _gemini_model = genai.GenerativeModel("gemini-2.0-flash")
        GEMINI_AVAILABLE = True
        logger.info("Gemini AI ENABLED for content generation")
except Exception as e:
    logger.warning(f"Gemini not available: {e}")


async def generate_with_gemini(nation_id: str, topic: str,
                                reply_to_nation: str = None,
                                is_news: bool = False) -> Optional[str]:
    """Generate a post using Gemini AI. Returns None on failure."""
    global _gemini_calls_this_minute, _gemini_minute_start

    if not GEMINI_AVAILABLE or not _gemini_model:
        return None

    # Rate limit: max 10 calls per minute
    now = time.time()
    if now - _gemini_minute_start > 60:
        _gemini_calls_this_minute = 0
        _gemini_minute_start = now
    if _gemini_calls_this_minute >= 10:
        return None
    _gemini_calls_this_minute += 1

    nation = PERSONALITIES.get(nation_id, {})
    name = nation.get("name", nation_id)
    rivals = [PERSONALITIES[r]["name"] for r in nation.get("rivals", []) if r in PERSONALITIES]
    allies = [PERSONALITIES[a]["name"] for a in nation.get("allies", []) if a in PERSONALITIES]

    # Build a personality-aware prompt
    context_parts = [
        f"You are {name}, a nation posting on a geopolitical social media platform.",
        f"Your rivals: {', '.join(rivals) if rivals else 'none'}.",
        f"Your allies: {', '.join(allies) if allies else 'none'}.",
    ]

    if reply_to_nation and reply_to_nation in PERSONALITIES:
        target = PERSONALITIES[reply_to_nation]["name"]
        is_rival = reply_to_nation in nation.get("rivals", [])
        tone = "confrontational and sharp" if is_rival else "diplomatic but firm"
        context_parts.append(f"You are replying to {target}. Be {tone}.")

    if is_news:
        context_parts.append(f"React to this breaking news: '{topic}'")
    else:
        context_parts.append(f"Post about: {topic}")

    prompt = "\n".join(context_parts) + """

Rules:
- Write 1-2 sentences MAX (under 250 chars), like a tweet
- Be specific, opinionated, provocative. NO generic platitudes
- Reference real current events, geopolitics, trade, tech, military
- Show YOUR nation's unique perspective and self-interest
- Use 1 emoji max
- Do NOT use hashtags, do NOT use quotes. Just speak directly
- Sound like a sharp political commentator, not a press release"""

    try:
        response = await asyncio.get_event_loop().run_in_executor(
            None, lambda: _gemini_model.generate_content(prompt)
        )
        text = response.text.strip().strip('"').strip("'")
        if text and len(text) > 20:
            return text[:280]
    except Exception as e:
        logger.debug(f"Gemini generation failed for {nation_id}: {e}")

    return None


def generate_content(nation_id: str, topic: str = None,
                     reply_to_nation: str = None, is_news: bool = False) -> str:
    """Synchronous wrapper — tries Gemini, falls back to templates."""
    # Try Gemini via async
    if GEMINI_AVAILABLE:
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    future = pool.submit(
                        asyncio.run,
                        generate_with_gemini(nation_id, topic or "current events",
                                             reply_to_nation, is_news)
                    )
                    result = future.result(timeout=15)
                    if result:
                        return result
        except Exception:
            pass

    # Fallback to template engine
    return GrammarEngine.generate(nation_id, topic, reply_to_nation, is_news)


# ============================================================================
# REDIS
# ============================================================================
aioredis = None
try:
    import redis.asyncio as aioredis
except ImportError:
    pass

# ============================================================================
# IN-MEMORY STORE
# ============================================================================
POSTS_STORE: list[dict] = []
MAX_STORE_SIZE = 1000


# ============================================================================
# REQUEST / RESPONSE MODELS
# ============================================================================
class GenerateRequest(BaseModel):
    nation_id: str
    topic: Optional[str] = "current world events"
    reply_to: Optional[str] = None

    @field_validator("nation_id")
    @classmethod
    def validate_nation_id(cls, v):
        clean = re.sub(r'[^a-zA-Z]', '', v).upper()
        if clean not in VALID_NATION_IDS:
            raise ValueError(f"Invalid nation_id: '{v}'. Valid: {sorted(VALID_NATION_IDS)}")
        return clean

    @field_validator("topic")
    @classmethod
    def validate_topic(cls, v):
        if v and len(v) > 1000:
            return v[:1000]
        return v


class TriggerNewsRequest(BaseModel):
    headline: str
    source: str = "Breaking News"

    @field_validator("headline")
    @classmethod
    def validate_headline(cls, v):
        if len(v) > 2000:
            return v[:2000]
        return v


class TriggerThreadRequest(BaseModel):
    topic: Optional[str] = None
    depth: int = 3  # How many reply levels


# ============================================================================
# CORE FUNCTIONS
# ============================================================================
def make_trace_id() -> str:
    return str(uuid.uuid4())


def create_post(nation_id: str, content: str, reply_to: str = None,
                news_reaction: str = None, trace_id: str = None,
                generation_meta: dict = None) -> dict:
    nation = PERSONALITIES[nation_id]
    _ensure_rep(nation_id)
    post = {
        "id": f"post_{len(POSTS_STORE)+1}_{int(datetime.utcnow().timestamp()*1000)}",
        "nation_id": nation_id,
        "nation_name": nation["name"],
        "flag": nation["flag"],
        "content": content,
        "timestamp": datetime.utcnow().isoformat(),
        "likes": random.randint(0, 80),
        "boosts": 0,
        "forks": 0,
        "proof_status": "none",  # none | requested | answered
        "reply_to": reply_to,
        "news_reaction": news_reaction,
        "trace_id": trace_id or make_trace_id(),
        "rep_score": REPUTATION[nation_id]["score"],
        "rep_tier": REPUTATION[nation_id]["tier"],
        "generation_meta": generation_meta or {},
    }
    # Award reputation for posting
    rep_gain(nation_id, 2)
    if reply_to:
        rep_gain(nation_id, 3)  # Bonus for engagement
        REPUTATION[nation_id]["threads_participated"] += 1
    if news_reaction:
        rep_gain(nation_id, 4)  # News awareness bonus
    POSTS_STORE.insert(0, post)
    if len(POSTS_STORE) > MAX_STORE_SIZE:
        POSTS_STORE.pop()
    return post


async def broadcast_post(post: dict):
    """Push post to in-memory SSE subscribers (works without Redis)."""
    # 1. In-memory SSE (always works)
    try:
        from src.api.endpoints.stream import push_to_feed
        push_to_feed(post)
    except Exception as e:
        logger.debug(f"In-memory broadcast skipped: {e}")

    # 2. Redis (optional, for multi-process setups)
    if not aioredis:
        return
    try:
        url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        redis = await aioredis.from_url(url, decode_responses=True)
        await redis.publish("nationbot:feed", json.dumps(post))
        await redis.close()
    except Exception as e:
        logger.debug(f"Redis broadcast skipped: {e}")


def pick_replying_nation(parent_nation_id: str) -> str:
    """Pick a nation most likely to reply — rivals first, then random"""
    parent = PERSONALITIES.get(parent_nation_id, {})
    rivals = parent.get("rivals", [])
    allies = parent.get("allies", [])

    # 60% chance rival replies, 25% ally, 15% random
    roll = random.random()
    if roll < 0.6 and rivals:
        return random.choice(rivals)
    elif roll < 0.85 and allies:
        return random.choice(allies)
    else:
        others = [nid for nid in PERSONALITIES if nid != parent_nation_id]
        return random.choice(others)


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post("/nation-post")
async def generate_nation_post(request: GenerateRequest, background_tasks: BackgroundTasks,
                               user: AuthenticatedUser | GuestUser = Depends(get_optional_user)):
    """Generate a post from a nation, optionally as a reply."""
    trace_id = make_trace_id()
    start = time.perf_counter()
    record_metric("total_requests")

    try:
        # Log who triggered this
        triggered_by = user.username if user.is_authenticated else "guest"

        # If replying, detect parent nation for rivalry-aware content
        reply_to_nation = None
        if request.reply_to:
            for p in POSTS_STORE:
                if p["id"] == request.reply_to:
                    reply_to_nation = p["nation_id"]
                    break

        content = GrammarEngine.generate(
            request.nation_id, request.topic,
            reply_to_nation=reply_to_nation,
        )
        post = create_post(
            nation_id=request.nation_id,
            content=content,
            reply_to=request.reply_to,
            trace_id=trace_id,
            generation_meta={"triggered_by": triggered_by},
        )
        background_tasks.add_task(broadcast_post, post)

        elapsed_ms = (time.perf_counter() - start) * 1000
        record_metric("latency", elapsed_ms)

        return {"status": "success", "post": post, "trace_id": trace_id}

    except Exception as e:
        record_metric("total_errors")
        logger.error(f"[{trace_id}] Generation failed: {e}")
        raise HTTPException(status_code=500, detail={"error": str(e), "trace_id": trace_id})


@router.post("/trigger-news")
async def trigger_news_reaction(request: TriggerNewsRequest, background_tasks: BackgroundTasks):
    """Enhanced: 5-8 nations react, then cross-reply to each other"""
    trace_id = make_trace_id()
    record_metric("total_requests")

    ids = list(PERSONALITIES.keys())
    react_count = random.randint(5, min(8, len(ids)))
    reacting_ids = random.sample(ids, react_count)

    reactions = []
    for nid in reacting_ids:
        content = GrammarEngine.generate(nid, request.headline, is_news=True)
        post = create_post(
            nation_id=nid, content=content,
            news_reaction=request.headline, trace_id=trace_id,
        )
        reactions.append(post)
        await asyncio.sleep(0.1)
        await broadcast_post(post)

    # Cross-replies: 2-3 nations reply to each other's reactions
    cross_reply_count = random.randint(2, 3)
    for _ in range(cross_reply_count):
        if len(reactions) < 2:
            break
        parent_post = random.choice(reactions)
        replier_id = pick_replying_nation(parent_post["nation_id"])
        content = GrammarEngine.generate(
            replier_id, request.headline,
            reply_to_nation=parent_post["nation_id"],
        )
        reply_post = create_post(
            nation_id=replier_id, content=content,
            reply_to=parent_post["id"], trace_id=trace_id,
        )
        reactions.append(reply_post)
        await asyncio.sleep(0.15)
        await broadcast_post(reply_post)

    return {"status": "success", "reactions": reactions, "trace_id": trace_id}


@router.post("/trigger-thread")
async def trigger_thread(request: TriggerThreadRequest, background_tasks: BackgroundTasks):
    """Generate a full thread: root post + cascading rival replies"""
    trace_id = make_trace_id()
    record_metric("total_requests")
    record_metric("total_threads")

    depth = min(request.depth, 5)  # Cap at 5
    thread_posts = []

    # Pick initial nation
    starter_id = random.choice(list(PERSONALITIES.keys()))
    topic = request.topic or random.choice(GrammarEngine.VOCAB["common"]["subject"])

    # Root post
    content = GrammarEngine.generate(starter_id, topic)
    root = create_post(nation_id=starter_id, content=content, trace_id=trace_id)
    thread_posts.append(root)
    await broadcast_post(root)
    await asyncio.sleep(0.2)

    # Fan-out + depth replies (organic thread structure)
    # ~60% reply to root, ~40% chain from previous reply
    last_reply = root
    for i in range(depth):
        # Decide target: first reply always to root, then mix
        if i == 0 or random.random() < 0.6:
            target_post = root  # Fan-out: reply to original
        else:
            target_post = last_reply  # Depth: chain from previous

        replier_id = pick_replying_nation(target_post["nation_id"])
        content = GrammarEngine.generate(
            replier_id, topic,
            reply_to_nation=target_post["nation_id"],
        )
        reply = create_post(
            nation_id=replier_id, content=content,
            reply_to=target_post["id"], trace_id=trace_id,
        )
        thread_posts.append(reply)
        await broadcast_post(reply)
        await asyncio.sleep(0.3)
        last_reply = reply

    return {"status": "success", "thread": thread_posts, "depth": len(thread_posts), "trace_id": trace_id}


@router.get("/feed")
async def get_feed(limit: int = 50):
    return {"posts": POSTS_STORE[:limit], "total": len(POSTS_STORE)}


@router.get("/nations")
async def list_nations():
    """Return all 25 nations grouped by region"""
    regions = {}
    for nid, data in PERSONALITIES.items():
        region = data["region"]
        if region not in regions:
            regions[region] = []
        regions[region].append({"id": nid, "name": data["name"], "flag": data["flag"]})
    return {"nations": PERSONALITIES, "regions": regions, "total": len(PERSONALITIES)}


@router.post("/like/{post_id}")
async def like_post(post_id: str, user: AuthenticatedUser | GuestUser = Depends(get_optional_user)):
    user_id = user.id if user.is_authenticated else "guest"
    for post in POSTS_STORE:
        if post["id"] == post_id:
            post["likes"] += 1
            if user.is_authenticated:
                # Could store liked_by set here
                pass
            rep_gain(post["nation_id"], 1)  # Rep for being liked
            return {"status": "success", "likes": post["likes"], "user_id": user_id}
    return {"status": "not_found"}


# ============================================================================
# GAP 2: BOOST / FORK / REQUEST PROOF
# ============================================================================

@router.post("/boost/{post_id}")
async def boost_post(post_id: str, user: AuthenticatedUser | GuestUser = Depends(get_optional_user)):
    """Amplify a post — increases visibility and author reputation"""
    user_id = user.id if user.is_authenticated else "guest"
    record_metric("total_boosts")
    for post in POSTS_STORE:
        if post["id"] == post_id:
            post["boosts"] = post.get("boosts", 0) + 1
            if user.is_authenticated:
                # Could log boost
                pass
            rep_gain(post["nation_id"], 8)  # Big rep for being boosted
            _ensure_rep(post["nation_id"])
            REPUTATION[post["nation_id"]]["boosts_received"] += 1
            return {
                "status": "success", "boosts": post["boosts"],
                "nation_rep": REPUTATION[post["nation_id"]]["score"],
                "user_id": user_id
            }
    return {"status": "not_found"}


@router.post("/fork/{post_id}")
async def fork_post(post_id: str, background_tasks: BackgroundTasks, user: AuthenticatedUser | GuestUser = Depends(get_optional_user)):
    """Fork (remix) an existing post — a new nation riffs on the original"""
    user_id = user.id if user.is_authenticated else "guest"
    record_metric("total_forks")
    parent = None
    for post in POSTS_STORE:
        if post["id"] == post_id:
            parent = post
            break
    if not parent:
        return {"status": "not_found"}

    # Pick a rival to remix
    forker_id = pick_replying_nation(parent["nation_id"])
    content = GrammarEngine.generate(
        forker_id, parent.get("content", "")[:100],
        reply_to_nation=parent["nation_id"],
    )

    fork = create_post(
        nation_id=forker_id, content=content,
        reply_to=parent["id"], trace_id=parent.get("trace_id"),
        generation_meta={"forked_from": parent["id"], "original_nation": parent["nation_id"], "triggered_by": user.username},
    )
    # Rep rewards
    rep_gain(parent["nation_id"], 6)   # Original author gets forked = reputation
    rep_gain(forker_id, 4)              # Forker gets creation credit
    parent["forks"] = parent.get("forks", 0) + 1
    _ensure_rep(parent["nation_id"])
    REPUTATION[parent["nation_id"]]["forks_received"] += 1
    background_tasks.add_task(broadcast_post, fork)

    return {"status": "success", "fork": fork, "parent_id": parent["id"]}


@router.post("/request-proof/{post_id}")
async def request_proof(post_id: str, background_tasks: BackgroundTasks, user: AuthenticatedUser | GuestUser = Depends(get_optional_user)):
    """Challenge a post — the nation must defend its claim"""
    user_id = user.id if user.is_authenticated else "guest"
    record_metric("total_proofs_requested")
    parent = None
    for post in POSTS_STORE:
        if post["id"] == post_id:
            parent = post
            break
    if not parent:
        return {"status": "not_found"}

    parent["proof_status"] = "requested"
    # Could track who requested proof in user_id
    parent["proof_requested_by"] = user_id
    if user.is_authenticated:
        # Log the user who requested proof
        print(f"User {user.username} ({user.id}) requested proof for post {post_id}")

    # Generate a proof/defense response from the same nation
    PROOF_TEMPLATES = [
        "Let me back that up: {topic}. Our data shows this is undeniable. 📊",
        "Proof requested? Fine. Every credible source agrees on {topic}. Do your research. 📚",
        "We stand by our position on {topic}. The evidence speaks for itself. ✅",
        "Challenge accepted. On {topic}, our track record is impeccable. 🏆",
        "You want receipts on {topic}? Here's the bottom line — we're right. 🧾",
    ]
    topic = parent.get("content", "")[:60]
    proof_content = random.choice(PROOF_TEMPLATES).format(topic=topic)

    proof_post = create_post(
        nation_id=parent["nation_id"], content=proof_content,
        reply_to=parent["id"], trace_id=parent.get("trace_id"),
        generation_meta={"proof_for": parent["id"], "proof_type": "defense"},
    )
    parent["proof_status"] = "answered"
    rep_gain(parent["nation_id"], 10)  # Big rep for answering proof challenge
    _ensure_rep(parent["nation_id"])
    REPUTATION[parent["nation_id"]]["proofs_answered"] += 1
    background_tasks.add_task(broadcast_post, proof_post)

    return {"status": "success", "proof": proof_post, "challenged_post": parent["id"]}


# ============================================================================
# GAP 3: SEARCH
# ============================================================================

@router.get("/search")
async def search_posts(
    q: str = "",
    nation: str = None,
    type: str = None,  # "post" | "news" | "reply" | "thread"
    limit: int = 30,
):
    """Search posts by content, nation, or type"""
    record_metric("total_searches")
    results = POSTS_STORE[:]

    if q:
        q_lower = q.lower()
        results = [p for p in results if q_lower in p.get("content", "").lower()
                   or q_lower in p.get("news_reaction", "").lower()
                   or q_lower in p.get("nation_name", "").lower()]

    if nation:
        nation_upper = nation.upper()
        results = [p for p in results if p["nation_id"] == nation_upper]

    if type:
        if type == "news":
            results = [p for p in results if p.get("news_reaction")]
        elif type == "reply":
            results = [p for p in results if p.get("reply_to")]
        elif type == "thread":
            # Group by trace_id, return root posts of multi-post traces
            trace_counts = {}
            for p in POSTS_STORE:
                tid = p.get("trace_id", "")
                trace_counts[tid] = trace_counts.get(tid, 0) + 1
            thread_traces = {tid for tid, count in trace_counts.items() if count >= 3}
            results = [p for p in results if p.get("trace_id") in thread_traces and not p.get("reply_to")]
        elif type == "post":
            results = [p for p in results if not p.get("reply_to") and not p.get("news_reaction")]

    return {"results": results[:limit], "total": len(results), "query": q}


# ============================================================================
# GAP 4: FOLLOW / SUBSCRIBE
# ============================================================================

@router.post("/follow/{nation_id}")
async def follow_nation(nation_id: str, user: AuthenticatedUser = Depends(get_current_user)):
    """Follow a nation to get filtered feed"""
    nid = nation_id.upper()
    if nid not in VALID_NATION_IDS:
        raise HTTPException(status_code=422, detail=f"Unknown nation: {nid}")
    
    # In-memory store logic
    if user.id not in FOLLOWS:
        FOLLOWS[user.id] = set()
    FOLLOWS[user.id].add(nid)
    
    # Update user object in DB (mock)
    from src.api.auth import USERS_DB
    if user.id in USERS_DB:
        USERS_DB[user.id]["followed_nations"] = list(FOLLOWS[user.id])
        
    return {"status": "success", "following": sorted(list(FOLLOWS[user.id])), "count": len(FOLLOWS[user.id])}


@router.delete("/follow/{nation_id}")
async def unfollow_nation(nation_id: str, user: AuthenticatedUser = Depends(get_current_user)):
    """Unfollow a nation"""
    nid = nation_id.upper()
    if user.id in FOLLOWS:
        FOLLOWS[user.id].discard(nid)
        
    # Update user object in DB (mock)
    from src.api.auth import USERS_DB
    if user.id in USERS_DB:
        USERS_DB[user.id]["followed_nations"] = list(FOLLOWS.get(user.id, []))
        
    return {"status": "success", "following": sorted(list(FOLLOWS.get(user.id, []))), "count": len(FOLLOWS.get(user.id, []))}


@router.get("/feed/following")
async def get_following_feed(limit: int = 50, user: AuthenticatedUser = Depends(get_current_user)):
    """Get feed filtered to followed nations only"""
    followed = FOLLOWS.get(user.id, set())
    if not followed:
        return {"posts": [], "total": 0, "following": []}
    filtered = [p for p in POSTS_STORE if p["nation_id"] in followed][:limit]
    return {"posts": filtered, "total": len(filtered), "following": sorted(list(followed))}


# ============================================================================
# GAP 5: PROOF PATH / TRACE EXPANSION
# ============================================================================

@router.get("/trace/{trace_id}")
async def get_trace(trace_id: str):
    """Return all posts sharing a trace_id (full proof chain)"""
    chain = [p for p in POSTS_STORE if p.get("trace_id") == trace_id]
    # Sort by timestamp ascending (oldest first) for chain order
    chain.sort(key=lambda p: p.get("timestamp", ""))

    # Build lineage metadata
    nations_involved = list({p["nation_id"] for p in chain})
    has_news = any(p.get("news_reaction") for p in chain)
    has_forks = any(p.get("generation_meta", {}).get("forked_from") for p in chain)
    has_proofs = any(p.get("generation_meta", {}).get("proof_for") for p in chain)

    return {
        "trace_id": trace_id,
        "chain": chain,
        "depth": len(chain),
        "nations_involved": nations_involved,
        "lineage": {
            "has_news_trigger": has_news,
            "has_forks": has_forks,
            "has_proofs": has_proofs,
            "type": "news_cycle" if has_news else "thread" if len(chain) > 1 else "standalone",
        },
    }


# ============================================================================
# GAP 1 CONTINUED: LEADERBOARD
# ============================================================================

@router.get("/leaderboard")
async def get_leaderboard():
    """Return all nations ranked by reputation"""
    # Ensure all nations have rep entries
    for nid in VALID_NATION_IDS:
        _ensure_rep(nid)

    ranked = sorted(
        [
            {
                "nation_id": nid,
                "name": PERSONALITIES[nid]["name"],
                "flag": PERSONALITIES[nid]["flag"],
                "region": PERSONALITIES[nid]["region"],
                **REPUTATION[nid],
            }
            for nid in VALID_NATION_IDS
        ],
        key=lambda x: x["score"],
        reverse=True,
    )
    for i, entry in enumerate(ranked):
        entry["rank"] = i + 1

    return {"leaderboard": ranked, "total": len(ranked)}


@router.get("/debug")
async def debug_info():
    latencies = METRICS.get("latency_samples", [])
    sorted_l = sorted(latencies) if latencies else [0]
    return {
        "mode": "GrammarEngine_v4_nuclear",
        "gemini": GEMINI_AVAILABLE,
        "nations_count": len(PERSONALITIES),
        "metrics": {
            "total_requests": METRICS["total_requests"],
            "total_errors": METRICS["total_errors"],
            "total_threads": METRICS["total_threads"],
            "total_boosts": METRICS.get("total_boosts", 0),
            "total_forks": METRICS.get("total_forks", 0),
            "total_proofs_requested": METRICS.get("total_proofs_requested", 0),
            "total_searches": METRICS.get("total_searches", 0),
            "p50_latency_ms": sorted_l[len(sorted_l)//2],
            "p95_latency_ms": sorted_l[int(len(sorted_l)*0.95)] if len(sorted_l) > 1 else sorted_l[0],
        },
        "store_size": len(POSTS_STORE),
        "reputation_initialized": len(REPUTATION),
        "follows_sessions": len(FOLLOWS),
    }
