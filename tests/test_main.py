import sys
from unittest.mock import MagicMock

import backend.main as main_module


def test_main_registers_all_services_and_dispatches(monkeypatch):
    registry = MagicMock()
    monkeypatch.setattr(main_module, "ServiceRegistry", lambda: registry)
    monkeypatch.setattr(sys, "argv", ["datappy", "api"])

    main_module.main()

    # api, populate, producer, consumer, diagram
    assert registry.register.call_count == 5
    registry.run.assert_called_once_with("api")
