import json
import uuid
from dataclasses import dataclass

from django import forms
from django.apps import apps
from django.conf import settings
from django.db.models import Count
from django.template.loader import render_to_string
from extras.dashboard.utils import register_widget
from extras.dashboard.widgets import DashboardWidget, WidgetConfigForm

try:
    from netbox.choices import ColorChoices
except ImportError:
    from utilities.choices import ColorChoices

# Build hex → name map and chart palette from NetBox's own ColorChoices
CABLE_COLOR_NAMES = {value: str(label) for value, label in ColorChoices}
CHART_COLORS = ["#" + value for value, _ in ColorChoices]


@dataclass
class DataSource:
    label: str
    app_label: str
    model_name: str
    group_field: str
    label_map: dict | None = None
    color_from_value: bool = False


DATA_SOURCES: dict[str, DataSource] = {
    "device_status": DataSource("Devices by Status", "dcim", "Device", "status"),
    "device_role": DataSource("Devices by Role", "dcim", "Device", "role__name"),
    "device_site": DataSource("Devices by Site", "dcim", "Device", "site__name"),
    "device_platform": DataSource("Devices by Platform", "dcim", "Device", "platform__name"),
    "device_type": DataSource("Devices by Type", "dcim", "Device", "device_type__model"),
    "vm_status": DataSource("VMs by Status", "virtualization", "VirtualMachine", "status"),
    "vm_cluster": DataSource("VMs by Cluster", "virtualization", "VirtualMachine", "cluster__name"),
    "prefix_status": DataSource("Prefixes by Status", "ipam", "Prefix", "status"),
    "ipaddress_status": DataSource("IP Addresses by Status", "ipam", "IPAddress", "status"),
    "circuit_status": DataSource("Circuits by Status", "circuits", "Circuit", "status"),
    "circuit_type": DataSource("Circuits by Type", "circuits", "Circuit", "type__name"),
    "cable_type": DataSource("Cables by Type", "dcim", "Cable", "type"),
    "cable_color": DataSource("Cables by Color", "dcim", "Cable", "color", CABLE_COLOR_NAMES, color_from_value=True),
    "cable_status": DataSource("Cables by Status", "dcim", "Cable", "status"),
    "cable_tenant": DataSource("Cables by Tenant", "dcim", "Cable", "tenant__name"),
}


def _format_label(value, label_map=None):
    """Turn raw DB values like 'active' or None into readable labels."""
    if value is None:
        return "(Unset)"
    if label_map:
        return label_map.get(str(value), str(value))
    return str(value).replace("_", " ").title()


@register_widget
class ChartWidget(DashboardWidget):
    default_title = "Chart"
    description = "Display object counts as a pie or doughnut chart, grouped by a selected field"
    default_config = {
        "data_source": "device_status",
        "chart_type": "pie",
        "max_slices": 10,
    }
    width = 4
    height = 4

    class ConfigForm(WidgetConfigForm):
        data_source = forms.ChoiceField(
            choices=[(k, v.label) for k, v in DATA_SOURCES.items()],
            label="Data Source",
        )
        chart_type = forms.ChoiceField(
            choices=[("pie", "Pie"), ("doughnut", "Doughnut"), ("bar", "Bar"), ("polarArea", "Polar Area")],
            label="Chart Type",
        )
        max_slices = forms.IntegerField(
            min_value=2,
            max_value=20,
            initial=10,
            label="Max Slices",
            help_text='Maximum segments to show — remaining items are grouped as "Other"',
        )

    def render(self, request):
        source_key = self.config.get("data_source", "device_status")
        chart_type = self.config.get("chart_type", "pie")
        max_slices = int(self.config.get("max_slices", 10))

        if source_key not in DATA_SOURCES:
            return '<p class="text-danger">Invalid data source selected.</p>'

        source = DATA_SOURCES[source_key]

        try:
            model = apps.get_model(source.app_label, source.model_name)
            rows = list(model.objects.values(source.group_field).annotate(count=Count("pk")).order_by("-count"))
        except Exception as exc:
            return f'<p class="text-danger">Query error: {exc}</p>'

        if not rows:
            return '<p class="text-muted text-center my-4">No data available for this source.</p>'

        # Merge tail rows into "Other" when result set exceeds max_slices
        if len(rows) > max_slices:
            top = rows[: max_slices - 1]
            other_count = sum(r["count"] for r in rows[max_slices - 1 :])
            top.append({source.group_field: None, "count": other_count, "_other": True})
            rows = top

        labels = []
        data = []
        raw_values = []
        for row in rows:
            if row.get("_other"):
                labels.append("Other")
                raw_values.append(None)
            else:
                raw_values.append(row.get(source.group_field))
                labels.append(_format_label(row.get(source.group_field), source.label_map))
            data.append(row["count"])

        if source.color_from_value:
            palette = ["#" + v if v else "#aaaaaa" for v in raw_values]
        else:
            palette = (CHART_COLORS * ((len(labels) // len(CHART_COLORS)) + 1))[: len(labels)]

        plugin_settings = settings.PLUGINS_CONFIG.get("netbox_widget_chart", {})
        chartjs_url = plugin_settings.get(
            "CHARTJS_URL",
            "https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js",
        )

        return render_to_string(
            "netbox_widget_chart/chart_widget.html",
            {
                "chart_id": uuid.uuid4().hex,
                "chart_type": chart_type,
                "chart_title": source.label,
                "chart_labels_json": json.dumps(labels),
                "chart_data_json": json.dumps(data),
                "chart_colors_json": json.dumps(palette),
                "total": sum(data),
                "rows": list(zip(labels, data, palette)),
                "chartjs_url": chartjs_url,
            },
            request=request,
        )
