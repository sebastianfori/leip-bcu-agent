from copy import deepcopy
import mongomock
import pytest
from leip.agent import reference_extraction, build_agent
from leip.source import read_table, capture
from leip.storage import persist
from leip.validation import validate

HTML = '''<table><tr><th colspan="3">EXPECTATIVAS DE INFLACIÓN Setiembre de 2026</th></tr>
<tr><th></th><th>Setiembre 2026 – Agosto 2027 (próximos 12 meses)</th><th>Setiembre 2026 – Agosto 2028 (próximos 24 meses)</th></tr>
<tr><td>Mediana</td><td>4,60</td><td>4,55</td></tr></table>'''.encode()


def test_values_and_distinct_target_periods():
    table = read_table(HTML)
    result = reference_extraction(table)
    validate(result, table)
    assert [o.value for o in result.observations] == [4.6, 4.55]
    assert result.observations[0].survey_month == "2026-09"
    assert result.observations[1].target_end == "2028-08"


@pytest.mark.parametrize("field,value", [("value", 9.9), ("target_end", "2029-08"), ("raw_value", "4,99")])
def test_reject_invented_value_or_period(field, value):
    table = read_table(HTML)
    result = reference_extraction(table)
    setattr(result.observations[0], field, value)
    with pytest.raises(ValueError):
        validate(result, table)


def test_duplicate_observations_rejected():
    table = read_table(HTML)
    result = reference_extraction(table)
    result.observations[1] = result.observations[0].model_copy()
    with pytest.raises(ValueError):
        validate(result, table)


def test_missing_and_ambiguous_tables_rejected():
    for raw in (b"<html>No hay datos</html>", HTML + HTML, HTML.replace(b"4,60", b"--")):
        with pytest.raises(ValueError):
            read_table(raw)


def test_external_url_rejected_before_network(tmp_path):
    with pytest.raises(ValueError):
        capture("https://example.com/", tmp_path)


def test_mongo_preserves_runs_without_overwriting():
    client = mongomock.MongoClient()
    run = {"_id": "first", "status": "candidate_for_review", "artifact": {"sha256": "abc"}, "created_at": "2026-09-01"}
    persist(run, "unused", "leip", client)
    second = deepcopy(run)
    second["_id"] = "second"
    persist(second, "unused", "leip", client)
    assert client.leip.extraction_runs.count_documents({}) == 2
    assert "_id" in run


def test_reject_mislabelled_horizon():
    with pytest.raises(ValueError):
        read_table(HTML.replace(b"Agosto 2028", b"Agosto 2029"))


def test_agent_graph_builds_without_api_request(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-placeholder-not-a-real-key")
    agent = build_agent(read_table(HTML))
    assert "tools" in agent.get_graph().nodes
