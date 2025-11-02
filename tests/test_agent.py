from app.agent_core import get_response


def test_basic_response():
    out = get_response("Hello, who are you?", backend="openai")
    assert isinstance(out, str)
