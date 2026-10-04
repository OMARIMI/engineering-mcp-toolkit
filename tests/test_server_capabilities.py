import asyncio

from src import server


def run(coro):
    return asyncio.run(coro)


def test_mcp_server_exposes_expected_tools_resource_and_prompt():
    tools = run(server.mcp.list_tools())
    resources = run(server.mcp.list_resources())
    prompts = run(server.mcp.list_prompts())

    assert {tool.name for tool in tools} == {
        "calculate_current",
        "calculate_power",
        "lookup_component",
        "save_draft_note",
    }
    assert {str(resource.uri) for resource in resources} == {
        "engineering://notes"
    }
    assert {prompt.name for prompt in prompts} == {"compare_components"}


def test_mcp_tools_work_through_server_interface(tmp_path, monkeypatch):
    monkeypatch.setattr(server, "DRAFTS_DIR", tmp_path)

    current = run(
        server.mcp.call_tool(
            "calculate_current",
            {"voltage": 12, "resistance": 6},
        )
    )
    draft = run(
        server.mcp.call_tool(
            "save_draft_note",
            {
                "file_name": "test-note.md",
                "content": "Plain draft content only.",
            },
        )
    )

    assert current.structured_content == {
        "result": (
            "The current is 2 amps. Using Ohm's law: "
            "12 V / 6 ohms = 2 A."
        )
    }
    assert draft.structured_content == {
        "result": "Saved draft note to drafts/test-note.md."
    }
    assert (tmp_path / "test-note.md").read_text(encoding="utf-8") == (
        "Plain draft content only.\n"
    )


def test_read_only_notes_resource_and_compare_prompt():
    resource_contents = run(server.mcp.read_resource("engineering://notes"))
    prompt = run(
        server.mcp.get_prompt(
            "compare_components",
            {
                "component_a": "Test Temperature Sensor",
                "component_b": "Metal Film Resistor Model 2",
                "project_goal": "5V prototype",
            },
        )
    )

    assert "Engineering MCP Toolkit" in resource_contents[0].content
    assert "Component A: Test Temperature Sensor" in (
        prompt.messages[0].content.text
    )
    assert "Component B: Metal Film Resistor Model 2" in (
        prompt.messages[0].content.text
    )


def test_lookup_component_uses_real_dataset():
    records = server.load_components()
    result = server.lookup_component(
        query="temperature sensor",
        category="sensor",
        max_cost=2,
        required_voltage=5,
        limit=3,
    )

    assert len(records) == 121
    assert "Test Temperature Sensor" in result
    assert "COMP-0121" in result


def test_lookup_component_reports_no_results():
    result = server.lookup_component(
        query="unobtainium quantum flux",
        category="sensor",
    )

    assert result == "No components matched your search and filters."
