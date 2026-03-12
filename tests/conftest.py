"""Shared pytest fixtures for Lausch tests."""

import pytest

from lausch.config import AppConfig


@pytest.fixture
def app_config() -> AppConfig:
    return AppConfig()
