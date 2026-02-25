import json
import pytest

@pytest.fixture(scope="session")
def load_rules():
    with open("rules/rules.json") as f:
        return json.load(f)