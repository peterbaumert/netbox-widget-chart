"""Tests for ChartWidget render logic and data aggregation."""

from unittest.mock import MagicMock, patch

import pytest

from netbox_widget_chart.widgets import DATA_SOURCES, ChartWidget, _format_label


# ---------------------------------------------------------------------------
# _format_label
# ---------------------------------------------------------------------------


class TestFormatLabel:
    def test_none_returns_unset(self):
        assert _format_label(None) == "(Unset)"

    def test_underscores_replaced_and_titlecased(self):
        assert _format_label("active_standby") == "Active Standby"

    def test_label_map_lookup(self):
        assert _format_label("ff0000", {"ff0000": "Red"}) == "Red"

    def test_label_map_missing_key_falls_back_to_value(self):
        assert _format_label("unknown", {"ff0000": "Red"}) == "unknown"


# ---------------------------------------------------------------------------
# DATA_SOURCES integrity
# ---------------------------------------------------------------------------


class TestDataSources:
    def test_all_sources_have_required_fields(self):
        for key, ds in DATA_SOURCES.items():
            assert ds.label, f"{key}: missing label"
            assert ds.app_label, f"{key}: missing app_label"
            assert ds.model_name, f"{key}: missing model_name"
            assert ds.group_field, f"{key}: missing group_field"

    def test_sources_with_url_also_have_param(self):
        for key, ds in DATA_SOURCES.items():
            if ds.list_url:
                assert ds.filter_param, f"{key}: has list_url but no filter_param"

    def test_cable_color_has_label_map(self):
        assert DATA_SOURCES["cable_color"].label_map is not None
        assert DATA_SOURCES["cable_color"].color_from_value is True


# ---------------------------------------------------------------------------
# ChartWidget.render
# ---------------------------------------------------------------------------


def _make_widget(source="device_status", chart_type="pie", max_slices=10):
    widget = ChartWidget.__new__(ChartWidget)
    widget.config = {"data_source": source, "chart_type": chart_type, "max_slices": max_slices}
    return widget


def _make_rows(field, values_and_counts):
    return [{field: v, "count": c} for v, c in values_and_counts]


@pytest.fixture()
def mock_request():
    return MagicMock()


class TestChartWidgetRender:
    def test_invalid_source_returns_error(self, mock_request):
        widget = _make_widget(source="nonexistent")
        result = widget.render(mock_request)
        assert "Invalid data source" in result

    def test_empty_queryset_returns_no_data_message(self, mock_request):
        widget = _make_widget()
        mock_model = MagicMock()
        mock_model.objects.values.return_value.annotate.return_value.order_by.return_value = []
        with patch("netbox_widget_chart.widgets.apps.get_model", return_value=mock_model):
            with patch("netbox_widget_chart.widgets.settings") as mock_settings:
                mock_settings.PLUGINS_CONFIG = {}
                result = widget.render(mock_request)
        assert "No data available" in result

    def test_renders_chart_html(self, mock_request):
        widget = _make_widget()
        rows = _make_rows("status", [("active", 5), ("planned", 3)])
        mock_model = MagicMock()
        mock_model.objects.values.return_value.annotate.return_value.order_by.return_value = rows
        with patch("netbox_widget_chart.widgets.apps.get_model", return_value=mock_model):
            with patch("netbox_widget_chart.widgets.render_to_string", return_value="<html>") as mock_render:
                with patch("netbox_widget_chart.widgets.settings") as mock_settings:
                    mock_settings.PLUGINS_CONFIG = {}
                    result = widget.render(mock_request)
        mock_render.assert_called_once()
        ctx = mock_render.call_args[0][1]
        assert ctx["total"] == 8
        assert "Active" in ctx["chart_labels_json"]
        assert result == "<html>"

    def test_max_slices_merges_tail_into_other(self, mock_request):
        widget = _make_widget(max_slices=3)
        rows = _make_rows("status", [("a", 10), ("b", 8), ("c", 5), ("d", 3), ("e", 1)])
        mock_model = MagicMock()
        mock_model.objects.values.return_value.annotate.return_value.order_by.return_value = rows
        with patch("netbox_widget_chart.widgets.apps.get_model", return_value=mock_model):
            with patch("netbox_widget_chart.widgets.render_to_string", return_value="") as mock_render:
                with patch("netbox_widget_chart.widgets.settings") as mock_settings:
                    mock_settings.PLUGINS_CONFIG = {}
                    widget.render(mock_request)
        ctx = mock_render.call_args[0][1]
        labels = eval(ctx["chart_labels_json"])  # noqa: S307
        assert len(labels) == 3
        assert labels[-1] == "Other"
        assert ctx["total"] == 27

    def test_query_error_returns_error_message(self, mock_request):
        widget = _make_widget()
        with patch("netbox_widget_chart.widgets.apps.get_model", side_effect=Exception("db error")):
            result = widget.render(mock_request)
        assert "Query error" in result

    def test_horizontal_bar_sets_flag(self, mock_request):
        widget = _make_widget(chart_type="bar_horizontal")
        rows = _make_rows("status", [("active", 5)])
        mock_model = MagicMock()
        mock_model.objects.values.return_value.annotate.return_value.order_by.return_value = rows
        with patch("netbox_widget_chart.widgets.apps.get_model", return_value=mock_model):
            with patch("netbox_widget_chart.widgets.render_to_string", return_value="") as mock_render:
                with patch("netbox_widget_chart.widgets.settings") as mock_settings:
                    mock_settings.PLUGINS_CONFIG = {}
                    widget.render(mock_request)
        ctx = mock_render.call_args[0][1]
        assert ctx["chart_type"] == "bar"
        assert ctx["horizontal"] == "true"

    def test_slice_urls_built_for_supported_source(self, mock_request):
        widget = _make_widget(source="device_status")
        rows = _make_rows("status", [("active", 5), ("planned", 2)])
        mock_model = MagicMock()
        mock_model.objects.values.return_value.annotate.return_value.order_by.return_value = rows
        with patch("netbox_widget_chart.widgets.apps.get_model", return_value=mock_model):
            with patch("netbox_widget_chart.widgets.render_to_string", return_value="") as mock_render:
                with patch("netbox_widget_chart.widgets.settings") as mock_settings:
                    mock_settings.PLUGINS_CONFIG = {}
                    widget.render(mock_request)
        ctx = mock_render.call_args[0][1]
        import json

        urls = json.loads(ctx["slice_urls_json"])
        assert urls[0] == "/dcim/devices/?status=active"
        assert urls[1] == "/dcim/devices/?status=planned"
