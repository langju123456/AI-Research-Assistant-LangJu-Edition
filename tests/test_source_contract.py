import json

import pytest

from app import agent_core


class FakeVectorStore:
    def __init__(self, records):
        self.records = records

    def similarity_search(self, query, k):
        return self.records


class FakeModel:
    def chat(self, messages):
        return "answer"


class FakeMemory:
    def add(self, item):
        pass


def response_for(monkeypatch, records):
    monkeypatch.setattr(agent_core, "get_vstore", lambda: FakeVectorStore(records))
    monkeypatch.setattr(agent_core, "ModelWrapper", lambda backend: FakeModel())
    monkeypatch.setattr(agent_core, "memory", FakeMemory())
    return agent_core.get_structured_response("question")


def valid_record(text="alpha", source="report.pdf", chunk=0):
    return {"text": text, "source": source, "chunk": chunk}


def test_valid_records_preserve_stable_order():
    records = [
        valid_record("first", "one.pdf", 0),
        valid_record("second", "two.pdf", 1),
    ]

    evidence, warnings, incomplete = agent_core._normalize_retrieval_records(records)

    assert [item["text"] for item in evidence] == ["first", "second"]
    assert warnings == []
    assert incomplete is False


def test_normalized_text_is_strip_for_prompt_and_identity():
    records = [
        valid_record("  alpha  "),
        valid_record("alpha"),
    ]

    evidence, _, _ = agent_core._normalize_retrieval_records(records)

    assert evidence == [{"text": "alpha", "source": "report.pdf", "chunk": 0}]


def test_non_mapping_records_are_unusable(monkeypatch):
    response = response_for(monkeypatch, [None, "text", 7])

    assert response["sources"] == []
    assert response["grounding_status"] == "no_verified_sources"
    assert response["warnings"] == [agent_core.NO_VERIFIED_SOURCES_WARNING]


def test_non_string_and_empty_text_are_unusable(monkeypatch):
    records = [
        valid_record(None),
        valid_record("  "),
        valid_record(7),
    ]

    response = response_for(monkeypatch, records)

    assert response["sources"] == []
    assert response["grounding_status"] == "no_verified_sources"


def test_usable_text_with_missing_source_is_incomplete(monkeypatch):
    response = response_for(monkeypatch, [{"text": "usable", "chunk": 0}])

    assert response["sources"] == []
    assert response["grounding_status"] == "incomplete_lineage"
    assert agent_core.INVALID_LINEAGE_WARNING in response["warnings"]


def test_usable_text_with_invalid_chunk_is_incomplete(monkeypatch):
    response = response_for(
        monkeypatch,
        [{"text": "usable", "source": "report.pdf", "chunk": None}],
    )

    assert response["sources"] == []
    assert response["grounding_status"] == "incomplete_lineage"


def test_chunk_zero_is_valid(monkeypatch):
    response = response_for(monkeypatch, [valid_record(chunk=0)])

    assert response["sources"] == [{"source": "report.pdf", "chunk": 0}]
    assert response["grounding_status"] == "verified_sources"


@pytest.mark.parametrize("chunk", [True, False, -1, "1", 1.0])
def test_bool_negative_string_float_chunks_are_invalid(monkeypatch, chunk):
    response = response_for(monkeypatch, [valid_record(chunk=chunk)])

    assert response["sources"] == []
    assert response["grounding_status"] == "incomplete_lineage"


def test_exact_duplicate_evidence_is_deduplicated(monkeypatch):
    record = valid_record()
    response = response_for(monkeypatch, [record, dict(record)])

    assert response["sources"] == [{"source": "report.pdf", "chunk": 0}]


def test_same_public_key_different_text_is_collision(monkeypatch):
    records = [valid_record("alpha"), valid_record("beta")]

    response = response_for(monkeypatch, records)

    assert response["sources"] == []
    assert response["grounding_status"] == "incomplete_lineage"
    assert agent_core.IDENTITY_COLLISION_WARNING in response["warnings"]


def test_collision_overrides_other_verified_sources(monkeypatch):
    records = [
        valid_record("alpha", "ambiguous.pdf", 0),
        valid_record("beta", "ambiguous.pdf", 0),
        valid_record("verified", "good.pdf", 1),
    ]

    response = response_for(monkeypatch, records)

    assert response["sources"] == [{"source": "good.pdf", "chunk": 1}]
    assert response["grounding_status"] == "incomplete_lineage"


def test_no_duplicate_indistinguishable_source_refs(monkeypatch):
    response = response_for(
        monkeypatch,
        [valid_record("alpha"), valid_record("alpha")],
    )

    refs = [(source["source"], source["chunk"]) for source in response["sources"]]
    assert len(refs) == len(set(refs))


def test_incomplete_lineage_overrides_verified_sources(monkeypatch):
    records = [valid_record(), {"text": "orphan", "source": None, "chunk": 1}]

    response = response_for(monkeypatch, records)

    assert response["sources"] == [{"source": "report.pdf", "chunk": 0}]
    assert response["grounding_status"] == "incomplete_lineage"


def test_no_valid_records_without_incomplete_condition(monkeypatch):
    response = response_for(monkeypatch, [])

    assert response == {
        "answer": "answer",
        "sources": [],
        "grounding_status": "no_verified_sources",
        "warnings": [agent_core.NO_VERIFIED_SOURCES_WARNING],
    }


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        (r"C:\private\report.pdf", "report.pdf"),
        ("/private/docs/report.pdf", "report.pdf"),
    ],
)
def test_windows_and_posix_paths_become_basename(source, expected):
    assert agent_core._normalize_source_name(source) == expected


def test_c0_c1_and_cf_characters_are_removed():
    source = "/private/\x00safe\x85\u202e\u200freport.pdf"

    assert agent_core._normalize_source_name(source) == "safereport.pdf"


def test_whitespace_collapses_before_length_bound():
    source = "/private/  quarterly    report   .pdf  "

    assert agent_core._normalize_source_name(source) == "quarterly report .pdf"


def test_long_source_is_bounded():
    normalized = agent_core._normalize_source_name("a" * 200)

    assert normalized is not None
    assert len(normalized) == 120


def test_empty_sanitized_source_is_incomplete_for_usable_text(monkeypatch):
    response = response_for(
        monkeypatch,
        [valid_record(source="/private/\x00\u202e")],
    )

    assert response["sources"] == []
    assert response["grounding_status"] == "incomplete_lineage"


def test_source_contract_has_only_source_and_chunk(monkeypatch):
    record = {
        "text": "private retrieved text",
        "source": "/private/report.pdf",
        "chunk": 0,
        "id": "secret-id",
        "url": "https://example.test",
        "score": 0.9,
        "title": "Private title",
    }

    response = response_for(monkeypatch, [record])

    assert response["sources"] == [{"source": "report.pdf", "chunk": 0}]
    assert set(response["sources"][0]) == {"source", "chunk"}


def test_response_exact_keys_and_json_serialization(monkeypatch):
    response = response_for(monkeypatch, [valid_record()])

    assert set(response) == {
        "answer",
        "sources",
        "grounding_status",
        "warnings",
    }
    assert json.loads(json.dumps(response)) == response
