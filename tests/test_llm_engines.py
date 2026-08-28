import json
from types import SimpleNamespace

from semantic_reconstruction.config import ReconstructionConfig
from semantic_reconstruction.llm_client import DeepSeekClient, parse_json_content
from semantic_reconstruction.llm_engine import HybridEngine, LLMEngine, _anchor
from llm_fixtures import make_units


class FakeCompletions:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=response))],
            usage=SimpleNamespace(prompt_tokens=10, completion_tokens=20, total_tokens=30),
        )


class FakeChat:
    def __init__(self, completions):
        self.completions = completions


class FakeClient:
    def __init__(self, responses):
        self.chat = FakeChat(FakeCompletions(responses))

class RetryableError(Exception):
    status_code = 429


def make_config(**kwargs):
    values = {"mode": "hybrid", "api_key": "test-key", "llm_batch_size": 25, "max_retries": 1}
    values.update(kwargs)
    return ReconstructionConfig(**values)


def payload_for_units(units, expression_only=True):
    if expression_only:
        value = {"units": [{"unit_id": unit.unit_id, "self_explanation": unit.self_explanation} for unit in units]}
    else:
        value = {"units": [_anchor(unit) for unit in units]}
        for item, unit in zip(value["units"], units):
            item["self_explanation"] = unit.self_explanation
    return json.dumps(value, ensure_ascii=False)


def test_parse_json_content_strips_thinking_and_fence():
    raw = "<think>x</think>```json\n{\"object\":\"测试\"}\n```"
    assert parse_json_content(raw) == ({"object": "测试"}, "")


def test_hybrid_accepts_constrained_batch():
    units = make_units()
    client = DeepSeekClient(make_config(), FakeClient([payload_for_units(units, True)]))
    output, usage = HybridEngine(client).reconstruct(units)
    assert usage and usage[0]["batch_size"] == len(units)
    assert all(unit.generation_mode == "hybrid" for unit in output)
    assert not any(finding.get("check") == "LLM" and finding["status"] != "pass" for unit in output for finding in unit.validation_findings)


def test_hybrid_rejects_expression_and_falls_back():
    units = make_units()
    bad = json.dumps({"units": [{"unit_id": unit.unit_id, "self_explanation": "合同有效即可。"} for unit in units]}, ensure_ascii=False)
    client = DeepSeekClient(make_config(), FakeClient([bad]))
    output, _ = HybridEngine(client).reconstruct(units)
    assert [item.self_explanation for item in output] == [item.self_explanation for item in units]
    assert any(finding.get("check") == "LLM" and finding["status"] == "warning" for unit in output for finding in unit.validation_findings)


def test_llm_mode_accepts_structured_anchor_and_requires_review():
    units = make_units()
    client = DeepSeekClient(make_config(mode="llm"), FakeClient([payload_for_units(units, False)]))
    output, _ = LLMEngine(client).reconstruct(units)
    assert all(unit.generation_mode == "llm" for unit in output)
    assert all(unit.review_status == "pending_business_review" for unit in output)


def test_llm_mode_blocks_changed_conclusion():
    units = make_units()
    payload = json.loads(payload_for_units(units, False))
    payload["units"][0]["action_or_conclusion"] = "必须由总经理审批。"
    client = DeepSeekClient(make_config(mode="llm"), FakeClient([json.dumps(payload, ensure_ascii=False)]))
    output, _ = LLMEngine(client).reconstruct(units)
    assert output[0].review_status == "blocked"
    assert any(finding.get("check") == "LLM" and finding["status"] == "error" for finding in output[0].validation_findings)
    assert output[0].action_or_conclusion == units[0].action_or_conclusion


def test_transient_error_is_retried():
    units = make_units()
    fake = FakeClient([RetryableError("rate limit"), payload_for_units(units, True)])
    client = DeepSeekClient(make_config(), fake)
    output, usage = HybridEngine(client).reconstruct(units)
    assert len(fake.chat.completions.calls) == 2
    assert usage[0]["attempt"] == 2
    assert output


def test_invalid_json_falls_back_in_hybrid():
    units = make_units()
    client = DeepSeekClient(make_config(), FakeClient(["not-json"]))
    output, _ = HybridEngine(client).reconstruct(units)
    assert [item.self_explanation for item in output] == [item.self_explanation for item in units]


