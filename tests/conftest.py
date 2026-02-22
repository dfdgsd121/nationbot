# tests/conftest.py
"""
Shared fixtures for NationBot Nuclear Validation Suite
"""
import pytest
import httpx
import asyncio
import time
import json
from typing import Generator

API_BASE = "http://localhost:8000"


@pytest.fixture(scope="session")
def api_url():
    return API_BASE


@pytest.fixture(scope="session")
def client():
    """Synchronous httpx client for API calls"""
    with httpx.Client(base_url=API_BASE, timeout=10.0) as c:
        yield c


@pytest.fixture(scope="session")
def async_client():
    """Async httpx client for concurrency tests"""
    return httpx.AsyncClient(base_url=API_BASE, timeout=10.0)


@pytest.fixture
def timer():
    """Context manager to measure latency"""
    class Timer:
        def __init__(self):
            self.elapsed_ms = 0
        def __enter__(self):
            self._start = time.perf_counter()
            return self
        def __exit__(self, *args):
            self.elapsed_ms = (time.perf_counter() - self._start) * 1000
    return Timer


@pytest.fixture
def nation_ids():
    return ["US", "RU", "CN", "UK", "FR", "DE", "JP", "IN"]


@pytest.fixture
def valid_post_keys():
    """Required keys in a valid post response"""
    return {"id", "nation_id", "nation_name", "flag", "content", "timestamp", "likes"}
