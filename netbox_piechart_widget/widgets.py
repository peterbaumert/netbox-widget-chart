import json
import uuid

from django import forms
from django.apps import apps
from django.db.models import Count
from django.template.loader import render_to_string

from extras.dashboard.utils import register_widget
from extras.dashboard.widgets import DashboardWidget, WidgetConfigForm

# NetBox cable color hex → human-readable name
CABLE_COLOR_NAMES = {
    "aa1409": "Dark Red",
    "f44336": "Red",
    "e91e63": "Pink",
    "ffe4e1": "Rose",
    "ff66ff": "Fuchsia",
    "9c27b0": "Purple",
    "673ab7": "Dark Purple",
    "3f51b5": "Indigo",
    "2196f3": "Blue",
    "03a9f4": "Light Blue",
    "00bcd4": "Cyan",
    "009688": "Teal",
    "00ffff": "Aqua",
    "2f6a31": "Dark Green",
    "4caf50": "Green",
    "8bc34a": "Light Green",
    "cddc39": "Lime",
    "ffeb3b": "Yellow",
    "ffc107": "Amber",
    "ff9800": "Orange",
    "ff5722": "Dark Orange",
    "795548": "Brown",
    "c0c0c0": "Light Grey",
    "9e9e9e": "Grey",
    "607d8b": "Dark Grey",
    "111111": "Black",
    "ffffff": "White",
}

# (label, app_label, model_name, group_by_field, label_map|None)
# group_by_field supports Django ORM double-underscore traversal for related fields
# label_map is an optional dict mapping raw DB values to display names
DATA_SOURCES = {
    "device_status": ("Devices by Status", "dcim", "Device", "status", None),
    "device_role": ("Devices by Role", "dcim", "Device", "role__name", None),
    "device_site": ("Devices by Site", "dcim", "Device", "site__name", None),
    "device_platform": ("Devices by Platform", "dcim", "Device", "platform__name", None),
    "device_type": ("Devices by Type", "dcim", "Device", "device_type__model", None),
    "vm_status": ("VMs by Status", "virtualization", "VirtualMachine", "status", None),
    "vm_cluster": ("VMs by Cluster", "virtualization", "VirtualMachine", "cluster__name", None),
    "prefix_status": ("Prefixes by Status", "ipam", "Prefix", "status", None),
    "ipaddress_status": ("IP Addresses by Status", "ipam", "IPAddress", "status", None),
    "circuit_status": ("Circuits by Status", "circuits", "Circuit", "status", None),
    "circuit_type": ("Circuits by Type", "circuits", "Circuit", "type__name", None),
    "cable_type": ("Cables by Type", "dcim", "Cable", "type", None),
    "cable_color": ("Cables by Color", "dcim", "Cable", "color", CABLE_COLOR_NAMES),
    "cable_status": ("Cables by Status", "dcim", "Cable", "status", None),
    "cable_tenant": ("Cables by Tenant", "dcim", "Cable", "tenant__name", None),
}

# Colour palette — cycles if there are more slices than colours
CHART_COLORS = [
    "#4dc9f6",
    "#f67019",
    "#f53794",
    "#537bc4",
    "#acc236",
    "#166a8f",
    "#00a950",
    "#58595b",
    "#8549ba",
    "#e8c03b",
    "#ff6384",
    "#36a2eb",
    "#ffce56",
    "#4bc0c0",
    "#9966ff",
    "#ff9f40",
    "#c9cbcf",
    "#7fc97f",
    "#beaed4",
    "#fdc086",
]


def _format_label(value, label_map=None):
    """Turn raw DB values like 'active' or None into readable labels."""
    if value is None:
        return "(Unset)"
    if label_map:
        return label_map.get(str(value), str(value))
    return str(value).replace("_", " ").title()


@register_widget
class PieChartWidget(DashboardWidget):
    default_title = "Pie Chart"
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
            choices=[(k, v[0]) for k, v in DATA_SOURCES.items()],
            label="Data Source",
        )
        chart_type = forms.ChoiceField(
            choices=[("pie", "Pie"), ("doughnut", "Doughnut")],
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

        label, app_label, model_name, group_field, label_map = DATA_SOURCES[source_key]

        try:
            model = apps.get_model(app_label, model_name)
            rows = list(model.objects.values(group_field).annotate(count=Count("pk")).order_by("-count"))
        except Exception as exc:
            return f'<p class="text-danger">Query error: {exc}</p>'

        # Merge tail rows into "Other" when result set exceeds max_slices
        if len(rows) > max_slices:
            top = rows[: max_slices - 1]
            other_count = sum(r["count"] for r in rows[max_slices - 1 :])
            top.append({group_field: None, "count": other_count, "_other": True})
            rows = top

        labels = []
        data = []
        for row in rows:
            if row.get("_other"):
                labels.append("Other")
            else:
                labels.append(_format_label(row.get(group_field), label_map))
            data.append(row["count"])

        palette = (CHART_COLORS * ((len(labels) // len(CHART_COLORS)) + 1))[: len(labels)]

        return render_to_string(
            "netbox_piechart_widget/piechart_widget.html",
            {
                "chart_id": uuid.uuid4().hex,
                "chart_type": chart_type,
                "chart_title": label,
                "chart_labels_json": json.dumps(labels),
                "chart_data_json": json.dumps(data),
                "chart_colors_json": json.dumps(palette),
                "total": sum(data),
                "rows": list(zip(labels, data, palette)),
            },
            request=request,
        )
