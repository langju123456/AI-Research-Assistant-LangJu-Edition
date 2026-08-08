import inspect

import pytest

from app import agent_core


class FakeVectorStore:
    def __init__(self, records=None):
        self.records = records or []
        self.calls = []

    def similarity_search(self, query, k):
        self.calls.append((query, k))
        return self.records


class FakeModel:
    def __init__(self, answer="deterministic test response"):
        self.answer = answer
        self.calls = []

    def chat(self, messages):
        self.calls.append(messages)
        return self.answer


class FakeMemory:
    def __init__(self):
        self.calls = []

    def add(self, item):
        self.calls.append(item)


def install_fakes(monkeypatch, records=None, answer="deterministic test response"):
    store = FakeVectorStore(records)
    model = FakeModel(answer)
    fake_memory = FakeMemory()
    backends = []
    web_calls = []

    def model_factory(backend):
        backends.append(backend)
        return model

    def fake_web_search(query):
        web_calls.append(query)
        return "unverified web snippet"

    monkeypatch.setattr(agent_core, "get_vstore", lambda: store)
    monkeypatch.setattr(agent_core, "ModelWrapper", model_factory)
    monkeypatch.setattr(agent_core, "memory", fake_memory)
    monkeypatch.setattr(agent_core, "web_search_tool", fake_web_search)
    return store, model, fake_memory, backends, web_calls


def valid_record(text="deterministic test context", source="note.txt", chunk=0):
    return {"text": text, "source": source, "chunk": chunk}


def prompt_from(model):
    return model.calls[0][1]["content"]


def test_basic_response(monkeypatch):
    install_fakes(monkeypatch, [valid_record()])

    out = agent_core.get_response("Hello, who are you?", backend="openai")

    assert out == "deterministic test response"


def test_get_response_exact_signature_and_default():
    signature = inspect.signature(agent_core.get_response)

    assert list(signature.parameters) == ["query", "backend"]
    assert signature.parameters["backend"].default == "openai"
    assert signature.return_annotation is str


def test_get_structured_response_exact_signature_and_default():
    signature = inspect.signature(agent_core.get_structured_response)

    assert list(signature.parameters) == ["query", "backend"]
    assert signature.parameters["backend"].default == "openai"
    assert signature.return_annotation is agent_core.ResearchResponse


def test_legacy_return_is_string(monkeypatch):
    install_fakes(monkeypatch, [valid_record()])

    response = agent_core.get_response("question")

    assert isinstance(response, str)


def test_openai_backend_forwarded(monkeypatch):
    _, _, _, backends, _ = install_fakes(monkeypatch, [valid_record()])

    agent_core.get_structured_response("question", backend="openai")

    assert backends == ["openai"]


def test_ollama_backend_forwarded(monkeypatch):
    _, _, _, backends, _ = install_fakes(monkeypatch, [valid_record()])

    agent_core.get_structured_response("question", backend="ollama")

    assert backends == ["ollama"]


@pytest.mark.parametrize("backend", ["openai", "ollama"])
def test_legacy_backend_forwarding_openai_and_ollama(monkeypatch, backend):
    _, _, _, backends, _ = install_fakes(monkeypatch, [valid_record()])

    agent_core.get_response("question", backend=backend)

    assert backends == [backend]


def test_valid_sources_match_grounded_prompt(monkeypatch):
    records = [
        valid_record("first evidence", "first.pdf", 0),
        valid_record("second evidence", "second.pdf", 1),
    ]
    _, model, _, _, _ = install_fakes(monkeypatch, records)

    response = agent_core.get_structured_response("question")
    prompt = prompt_from(model)

    assert prompt.index("first evidence") < prompt.index("second evidence")
    assert response["sources"] == [
        {"source": "first.pdf", "chunk": 0},
        {"source": "second.pdf", "chunk": 1},
    ]


def test_unusable_only_records_yield_no_verified_sources(monkeypatch):
    install_fakes(monkeypatch, [{"text": "  "}, None])

    response = agent_core.get_structured_response("question")

    assert response["sources"] == []
    assert response["grounding_status"] == "no_verified_sources"
    assert agent_core.NO_VERIFIED_SOURCES_WARNING in response["warnings"]


def test_missing_provenance_yields_incomplete_lineage(monkeypatch):
    _, model, _, _, _ = install_fakes(
        monkeypatch,
        [{"text": "must not ground", "chunk": 0}],
    )

    response = agent_core.get_structured_response("question")

    assert "must not ground" not in prompt_from(model)
    assert response["sources"] == []
    assert response["grounding_status"] == "incomplete_lineage"


def test_identity_collision_excludes_all_colliding_context(monkeypatch):
    records = [
        valid_record("collision alpha", "same.pdf", 0),
        valid_record("collision beta", "same.pdf", 0),
    ]
    _, model, _, _, _ = install_fakes(monkeypatch, records)

    response = agent_core.get_structured_response("question")
    prompt = prompt_from(model)

    assert "collision alpha" not in prompt
    assert "collision beta" not in prompt
    assert response["sources"] == []


def test_identity_collision_warning_is_explicit(monkeypatch):
    records = [valid_record("alpha"), valid_record("beta")]
    install_fakes(monkeypatch, records)

    response = agent_core.get_structured_response("question")

    assert agent_core.IDENTITY_COLLISION_WARNING in response["warnings"]


def test_incomplete_status_overrides_remaining_verified_sources(monkeypatch):
    records = [
        valid_record("verified", "good.pdf", 0),
        {"text": "orphan", "chunk": 1},
    ]
    install_fakes(monkeypatch, records)

    response = agent_core.get_structured_response("question")

    assert response["sources"] == [{"source": "good.pdf", "chunk": 0}]
    assert response["grounding_status"] == "incomplete_lineage"


def test_search_space_trigger(monkeypatch):
    _, _, _, _, web_calls = install_fakes(monkeypatch)

    agent_core.get_structured_response("please search this")

    assert web_calls == ["please search this"]


def test_google_trigger(monkeypatch):
    _, _, _, _, web_calls = install_fakes(monkeypatch)

    agent_core.get_structured_response("Ask Google about this")

    assert web_calls == ["Ask Google about this"]


def test_non_trigger_query(monkeypatch):
    _, _, _, _, web_calls = install_fakes(monkeypatch)

    agent_core.get_structured_response("investigate this")

    assert web_calls == []


def test_search_query_forwarded_unchanged(monkeypatch):
    _, _, _, _, web_calls = install_fakes(monkeypatch)
    query = "Please SEARCH this Exact Query"

    agent_core.get_structured_response(query)

    assert web_calls == [query]


def test_search_context_reaches_prompt(monkeypatch):
    _, model, _, _, _ = install_fakes(monkeypatch)

    agent_core.get_structured_response("search this")

    assert "[WEB_SEARCH]\nunverified web snippet" in prompt_from(model)


def test_mocked_search_never_becomes_source(monkeypatch):
    install_fakes(monkeypatch)

    response = agent_core.get_structured_response("search this")

    assert response["sources"] == []


def test_mocked_search_always_sets_incomplete_lineage(monkeypatch):
    install_fakes(monkeypatch, [valid_record()])

    response = agent_core.get_structured_response("google this")

    assert response["grounding_status"] == "incomplete_lineage"
    assert agent_core.WEB_CONTEXT_WARNING in response["warnings"]


def test_web_only_response_has_empty_sources(monkeypatch):
    install_fakes(monkeypatch)

    response = agent_core.get_structured_response("search this")

    assert response["sources"] == []
    assert response["grounding_status"] == "incomplete_lineage"


def test_model_called_exactly_once_structured(monkeypatch):
    store, model, _, _, _ = install_fakes(monkeypatch, [valid_record()])

    agent_core.get_structured_response("question")

    assert len(store.calls) == 1
    assert len(model.calls) == 1


def test_memory_written_exactly_once_structured(monkeypatch):
    _, _, fake_memory, _, _ = install_fakes(monkeypatch, [valid_record()])

    agent_core.get_structured_response("question")

    assert fake_memory.calls == [
        {"user": "question", "assistant": "deterministic test response"}
    ]


def test_search_called_exactly_once_when_triggered(monkeypatch):
    _, _, _, _, web_calls = install_fakes(monkeypatch)

    agent_core.get_structured_response("google and search this")

    assert web_calls == ["google and search this"]


def test_legacy_delegation_does_not_duplicate_model_or_memory(monkeypatch):
    store, model, fake_memory, _, _ = install_fakes(monkeypatch, [valid_record()])

    agent_core.get_response("question")

    assert len(store.calls) == 1
    assert len(model.calls) == 1
    assert fake_memory.calls == [
        {"user": "question", "assistant": "deterministic test response"}
    ]


def test_legacy_trigger_does_not_duplicate_web_search(monkeypatch):
    _, _, _, _, web_calls = install_fakes(monkeypatch)

    agent_core.get_response("search this")

    assert web_calls == ["search this"]


def test_generated_answer_may_quote_context_without_metadata_leak(monkeypatch):
    answer = "The answer may quote private retrieved text."
    install_fakes(
        monkeypatch,
        [valid_record("private retrieved text", "/private/report.pdf", 0)],
        answer=answer,
    )

    response = agent_core.get_structured_response("question")

    assert response["answer"] == answer
    assert response["sources"] == [{"source": "report.pdf", "chunk": 0}]
    assert "private retrieved text" not in repr(response["sources"])


def test_model_cannot_invent_source_fields(monkeypatch):
    answer = "Source: invented.pdf, URL: https://invented.test"
    install_fakes(monkeypatch, [valid_record()], answer=answer)

    response = agent_core.get_structured_response("question")

    assert response["answer"] == answer
    assert response["sources"] == [{"source": "note.txt", "chunk": 0}]
    assert set(response["sources"][0]) == {"source", "chunk"}
