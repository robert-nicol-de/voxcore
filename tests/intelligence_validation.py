import pytest

def test_schema_grounding(response, schema):
    valid_tables = [t["name"] for t in schema["tables"]]
    for t in response["audit"]["selectedTables"]:
        assert t in valid_tables

def test_audit_exists(response):
    assert "audit" in response
    assert len(response["audit"]["reasoning"]) > 0

def test_confidence_valid(response):
    assert 0 <= response["audit"]["confidence"] <= 1

def test_schema_trust_present(response):
    assert "schema_trust" in response

def test_no_generic_response(response):
    assert response["audit"]["schemaUsed"] is True
