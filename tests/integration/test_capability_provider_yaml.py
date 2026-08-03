"""Integration — Phase 2: YamlCapabilityProvider(ICapabilityProvider).

목적:
1. 실제 uv workspace에 설치된 hqs/*의 entry point를 통해 development-hq /
   investment-hq의 capabilities.yaml이 실제로 파싱되는지 확인한다(하드코딩된
   값과 비교하지 않고, 오직 실제 파일 로드 결과만 확인한다 — ADR-0002 Known Gap 해소 증명).
2. 구조적으로 무효한 항목(스키마 필드 누락, owner 불일치)이 조용히 무시되지
   않고 반환 목록에서 제외되며 사유가 self.errors에 남는지 확인한다
   (No Silent Failure, ADR-0004 결정 4의 Provider 쪽 몫).

실행: uv run pytest tests/integration/test_capability_provider_yaml.py
"""
import unittest
from unittest.mock import patch

from jarvis_adapter_capability_provider_yaml.provider import YamlCapabilityProvider


class TestYamlCapabilityProviderRealDiscovery(unittest.TestCase):
    """실제 uv workspace에 설치된 development-hq/investment-hq를 대상으로 한다."""

    def test_loads_capabilities_from_real_hq_packages(self):
        provider = YamlCapabilityProvider()
        capabilities = provider.load()

        owners = {c.owner for c in capabilities}
        self.assertIn("development-hq", owners)
        self.assertIn("investment-hq", owners)
        self.assertEqual(provider.errors, [])

        dev = next(c for c in capabilities if c.owner == "development-hq")
        self.assertEqual(dev.capability_id, "dev-hq.code-task.v1")
        self.assertEqual(dev.required_permission, "standard")

        invest = next(c for c in capabilities if c.owner == "investment-hq")
        self.assertEqual(invest.capability_id, "invest-hq.market-task.v1")
        self.assertEqual(invest.required_permission, "restricted")


class TestYamlCapabilityProviderStructuralValidation(unittest.TestCase):
    """구조적으로 무효한 capabilities.yaml이 조용히 무시되지 않는지 확인한다."""

    def _load_with_fake_yaml(self, yaml_text: str):
        provider = YamlCapabilityProvider()
        with patch(
            "jarvis_adapter_capability_provider_yaml.provider.resources.files"
        ) as mock_files:
            mock_files.return_value.joinpath.return_value.read_text.return_value = yaml_text
            capability = provider._load_one("fake-hq", "fake_module")
        return provider, capability

    def test_missing_required_field_is_rejected_not_silently_dropped(self):
        yaml_text = (
            "capability_id: fake.v1\n"
            "domain: fake.general\n"
            "owner: fake-hq\n"
            # description/input_profile/output_profile 누락
        )
        provider, capability = self._load_with_fake_yaml(yaml_text)

        self.assertIsNone(capability)
        self.assertEqual(len(provider.errors), 1)
        hq_id, reason = provider.errors[0]
        self.assertEqual(hq_id, "fake-hq")
        self.assertIn("필수 필드 누락", reason)

    def test_owner_mismatch_is_rejected_not_silently_dropped(self):
        yaml_text = (
            "capability_id: fake.v1\n"
            "domain: fake.general\n"
            "description: d\n"
            "input_profile: i\n"
            "output_profile: o\n"
            "owner: some-other-hq\n"  # entry point name(fake-hq)과 불일치
        )
        provider, capability = self._load_with_fake_yaml(yaml_text)

        self.assertIsNone(capability)
        self.assertEqual(len(provider.errors), 1)
        hq_id, reason = provider.errors[0]
        self.assertEqual(hq_id, "fake-hq")
        self.assertIn("owner 불일치", reason)

    def test_valid_yaml_is_accepted(self):
        yaml_text = (
            "capability_id: fake.v1\n"
            "domain: fake.general\n"
            "description: d\n"
            "input_profile: i\n"
            "output_profile: o\n"
            "owner: fake-hq\n"
        )
        provider, capability = self._load_with_fake_yaml(yaml_text)

        self.assertIsNotNone(capability)
        self.assertEqual(capability.capability_id, "fake.v1")
        self.assertEqual(provider.errors, [])


if __name__ == "__main__":
    unittest.main()
