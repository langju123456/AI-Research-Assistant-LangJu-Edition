from app import main


class Context:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False


class SessionState(dict):
    def __getattr__(self, name):
        return self[name]

    def __setattr__(self, name, value):
        self[name] = value


class FakeStreamlit:
    def __init__(self, backend="openai", prompt=None):
        self.backend = backend
        self.prompt = prompt
        self.sidebar = Context()
        self.session_state = SessionState()
        self.roles = []
        self.writes = []
        self.texts = []

    def set_page_config(self, **kwargs):
        pass

    def title(self, value):
        pass

    def caption(self, value):
        pass

    def header(self, value):
        pass

    def file_uploader(self, *args, **kwargs):
        return None

    def divider(self):
        pass

    def selectbox(self, label, options):
        return self.backend

    def chat_input(self, label):
        return self.prompt

    def spinner(self, label):
        return Context()

    def chat_message(self, role):
        self.roles.append(role)
        return Context()

    def write(self, value):
        self.writes.append(value)

    def text(self, value):
        self.texts.append(value)


def response(sources=None, warnings=None):
    return {
        "answer": "structured answer",
        "sources": sources or [],
        "grounding_status": "verified_sources" if sources else "no_verified_sources",
        "warnings": warnings or [],
    }


def install_response(monkeypatch, expected_backend):
    calls = []
    structured = response([{"source": "report.pdf", "chunk": 0}])

    def fake_get_structured_response(query, backend):
        calls.append((query, backend))
        return structured

    monkeypatch.setattr(main, "get_structured_response", fake_get_structured_response)
    history = []
    result = main.submit_query(history, "question", expected_backend)
    return calls, history, result


def test_main_passes_selected_openai_backend(monkeypatch):
    calls = []
    st = FakeStreamlit(backend="openai", prompt="question")
    monkeypatch.setattr(
        main,
        "get_structured_response",
        lambda query, backend: calls.append((query, backend)) or response(),
    )

    main.run_app(st)

    assert calls == [("question", "openai")]


def test_main_passes_selected_ollama_backend(monkeypatch):
    calls = []
    st = FakeStreamlit(backend="ollama", prompt="question")
    monkeypatch.setattr(
        main,
        "get_structured_response",
        lambda query, backend: calls.append((query, backend)) or response(),
    )

    main.run_app(st)

    assert calls == [("question", "ollama")]


def test_user_entry_is_exact_two_tuple(monkeypatch):
    _, history, _ = install_response(monkeypatch, "openai")

    assert history[0] == ("user", "question")
    assert isinstance(history[0], tuple)
    assert len(history[0]) == 2


def test_structured_assistant_entry_is_exact_two_tuple(monkeypatch):
    _, history, structured = install_response(monkeypatch, "openai")

    assert history[1] == ("assistant", structured)
    assert isinstance(history[1], tuple)
    assert len(history[1]) == 2


def test_all_string_legacy_history_renders():
    st = FakeStreamlit()
    history = [("user", "old question"), ("assistant", "old answer")]

    main.render_history(st, history)

    assert st.roles == ["user", "assistant"]
    assert st.writes == ["old question", "old answer"]


def test_structured_tuple_history_renders():
    st = FakeStreamlit()
    structured = response(
        [{"source": "report.pdf", "chunk": 0}],
        ["lineage warning"],
    )

    main.render_history(st, [("assistant", structured)])

    assert st.writes == ["structured answer"]
    assert "Grounding status: verified_sources" in st.texts
    assert "- report.pdf (chunk 0)" in st.texts
    assert "Warning: lineage warning" in st.texts


def test_mixed_tuple_history_renders_and_rerenders():
    history = [
        ("assistant", "legacy answer"),
        ("assistant", response([{"source": "new.pdf", "chunk": 1}])),
    ]
    first_render = FakeStreamlit()
    second_render = FakeStreamlit()

    main.render_history(first_render, history)
    main.render_history(second_render, history)

    assert first_render.writes == ["legacy answer", "structured answer"]
    assert second_render.writes == first_render.writes
    assert second_render.texts == first_render.texts


def test_answer_uses_existing_write_behavior():
    st = FakeStreamlit()

    main.render_payload(st, "assistant", response())

    assert st.writes == ["structured answer"]


def test_sources_use_st_text_or_equivalent():
    st = FakeStreamlit()

    main.render_payload(
        st,
        "assistant",
        response([{"source": "safe.pdf", "chunk": 0}]),
    )

    assert "- safe.pdf (chunk 0)" in st.texts
    assert st.writes == ["structured answer"]


def test_warnings_use_st_text_or_equivalent():
    st = FakeStreamlit()

    main.render_payload(st, "assistant", response(warnings=["plain warning"]))

    assert "Warning: plain warning" in st.texts


def test_status_renders_separately_as_plain_text():
    st = FakeStreamlit()

    main.render_payload(st, "assistant", response())

    assert "Grounding status: no_verified_sources" in st.texts
    assert all("Grounding status" not in str(value) for value in st.writes)


def test_unexpected_payload_falls_back_without_sources():
    st = FakeStreamlit()
    unexpected = {
        "answer": "unsafe",
        "sources": [{"source": "/private/path.pdf", "chunk": 0}],
    }

    main.render_payload(st, "assistant", unexpected)

    assert st.writes == []
    assert st.texts == ["Unsupported message payload."]
    assert "path.pdf" not in " ".join(st.texts)


def test_ui_hides_paths_and_retrieved_text():
    st = FakeStreamlit()
    structured = response([{"source": "/private/report.pdf", "chunk": 0}])

    main.render_payload(st, "assistant", structured)
    rendered = " ".join([*(str(value) for value in st.writes), *st.texts])

    assert "/private/" not in rendered
    assert "raw retrieved evidence" not in rendered
    assert st.texts == ["Unsupported message payload."]


def test_empty_sources_create_no_placeholder_citation():
    st = FakeStreamlit()

    main.render_payload(st, "assistant", response())

    assert all("Sources made available" not in line for line in st.texts)
    assert all("chunk" not in line for line in st.texts)
