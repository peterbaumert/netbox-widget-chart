"""Mock NetBox modules so tests run without a NetBox installation."""

import sys
from types import ModuleType
from unittest.mock import MagicMock


def _mock_module(*parts):
    """Register a chain of nested mock modules in sys.modules."""
    for i in range(1, len(parts) + 1):
        name = ".".join(parts[:i])
        if name not in sys.modules:
            sys.modules[name] = ModuleType(name)


# Top-level stubs
for _mod in ("netbox", "extras", "utilities", "django", "circuits", "dcim", "ipam", "virtualization", "tenancy"):
    _mock_module(_mod)

# netbox.plugins
_mock_module("netbox", "plugins")
sys.modules["netbox.plugins"].PluginConfig = object

# netbox.choices / utilities.choices — provide a minimal ColorChoices
_mock_module("netbox", "choices")
_mock_module("utilities", "choices")


class _FakeColorChoices:
    def __iter__(self):
        yield ("ff0000", "Red")
        yield ("00ff00", "Green")
        yield ("0000ff", "Blue")


_color_instance = _FakeColorChoices()
sys.modules["netbox.choices"].ColorChoices = _color_instance
sys.modules["utilities.choices"].ColorChoices = _color_instance

# extras.dashboard.*
_mock_module("extras", "dashboard")
_mock_module("extras", "dashboard", "utils")
_mock_module("extras", "dashboard", "widgets")


def _register_widget(cls):
    return cls


sys.modules["extras.dashboard.utils"].register_widget = _register_widget
sys.modules["extras.dashboard.widgets"].DashboardWidget = object
sys.modules["extras.dashboard.widgets"].WidgetConfigForm = object

# django stubs
_mock_module("django", "apps")
_mock_module("django", "conf")
_mock_module("django", "db")
_mock_module("django", "db", "models")
_mock_module("django", "forms")
_mock_module("django", "template")
_mock_module("django", "template", "loader")

sys.modules["django.apps"].apps = MagicMock()
sys.modules["django.conf"].settings = MagicMock()
sys.modules["django.db.models"].Count = MagicMock()
sys.modules["django.template.loader"].render_to_string = MagicMock()
sys.modules["django.forms"].ChoiceField = MagicMock
sys.modules["django.forms"].IntegerField = MagicMock
sys.modules["django.forms"].Form = object
