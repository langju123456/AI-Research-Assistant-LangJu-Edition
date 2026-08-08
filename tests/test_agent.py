from app import agent_core


class FakeVectorStore:
    def similarity_search(self, query, k):
        return [{"text": "deterministic test context"}]


class FakeModel:
    def chat(self, messages):
        return "deterministic test response"


def test_basic_response(monkeypatch):
    monkeypatch.setattr(agent_core, "get_vstore", lambda: FakeVectorStore())
    monkeypatch.setattr(agent_core, "ModelWrapper", lambda backend: FakeModel())

    out = agent_core.get_response("Hello, who are you?", backend="openai")

    assert out == "deterministic test response"
