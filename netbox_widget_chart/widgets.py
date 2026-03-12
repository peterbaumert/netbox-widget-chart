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
    list_url: str | None = None  # e.g. "/dcim/devices/"
    filter_param: str | None = None  # e.g. "status"


def _ds(label, app, model, field, lmap=None, color_from=False, url=None, param=None):
    return DataSource(label, app, model, field, lmap, color_from, url, param)


_VMS = "/virtualization/virtual-machines/"

DATA_SOURCES: dict[str, DataSource] = {
    # Devices
    "device_status": _ds("Devices by Status", "dcim", "Device", "status", url="/dcim/devices/", param="status"),
    "device_role": _ds("Devices by Role", "dcim", "Device", "role__name", url="/dcim/devices/", param="role"),
    "device_site": _ds("Devices by Site", "dcim", "Device", "site__name", url="/dcim/devices/", param="site"),
    "device_platform": _ds("Devices by Platform", "dcim", "Device", "platform__name", url="/dcim/devices/", param="platform"),
    "device_type": _ds("Devices by Type", "dcim", "Device", "device_type__model", url="/dcim/devices/", param="device_type"),
    # Virtual Machines
    "vm_status": _ds("VMs by Status", "virtualization", "VirtualMachine", "status", url=_VMS, param="status"),
    "vm_cluster": _ds("VMs by Cluster", "virtualization", "VirtualMachine", "cluster__name", url=_VMS, param="cluster"),
    "vm_platform": _ds("VMs by Platform", "virtualization", "VirtualMachine", "platform__name", url=_VMS, param="platform"),
    "vm_site": _ds("VMs by Site", "virtualization", "VirtualMachine", "site__name", url=_VMS, param="site"),
    # Prefixes
    "prefix_status": _ds("Prefixes by Status", "ipam", "Prefix", "status", url="/ipam/prefixes/", param="status"),
    "prefix_vrf": _ds("Prefixes by VRF", "ipam", "Prefix", "vrf__name", url="/ipam/prefixes/", param="vrf"),
    "prefix_role": _ds("Prefixes by Role", "ipam", "Prefix", "role__name", url="/ipam/prefixes/", param="role"),
    # IP Addresses
    "ipaddress_status": _ds("IP Addresses by Status", "ipam", "IPAddress", "status", url="/ipam/ip-addresses/", param="status"),
    "ipaddress_role": _ds("IP Addresses by Role", "ipam", "IPAddress", "role", url="/ipam/ip-addresses/", param="role"),
    "ipaddress_dns": _ds("IP Addresses by DNS Name", "ipam", "IPAddress", "dns_name", url="/ipam/ip-addresses/", param="dns_name"),
    # VLANs
    "vlan_status": _ds("VLANs by Status", "ipam", "VLAN", "status", url="/ipam/vlans/", param="status"),
    "vlan_role": _ds("VLANs by Role", "ipam", "VLAN", "role__name", url="/ipam/vlans/", param="role"),
    # Circuits
    "circuit_status": _ds("Circuits by Status", "circuits", "Circuit", "status", url="/circuits/circuits/", param="status"),
    "circuit_type": _ds("Circuits by Type", "circuits", "Circuit", "type__name", url="/circuits/circuits/", param="type"),
    # Cables
    "cable_type": _ds("Cables by Type", "dcim", "Cable", "type", url="/dcim/cables/", param="type"),
    "cable_color": _ds("Cables by Color", "dcim", "Cable", "color", CABLE_COLOR_NAMES, True, url="/dcim/cables/", param="color"),
    "cable_status": _ds("Cables by Status", "dcim", "Cable", "status", url="/dcim/cables/", param="status"),
    "cable_tenant": _ds("Cables by Tenant", "dcim", "Cable", "tenant__name", url="/dcim/cables/", param="tenant"),
    # Racks
    "rack_site": _ds("Racks by Site", "dcim", "Rack", "site__name", url="/dcim/racks/", param="site"),
    "rack_status": _ds("Racks by Status", "dcim", "Rack", "status", url="/dcim/racks/", param="status"),
    "rack_role": _ds("Racks by Role", "dcim", "Rack", "role__name", url="/dcim/racks/", param="role"),
    # Tenancy
    "tenant_group": _ds("Tenants by Group", "tenancy", "Tenant", "group__name", url="/tenancy/tenants/", param="group"),
    "contact_role": _ds("Contacts by Role", "tenancy", "ContactAssignment", "role__name"),
    # Power
    "powerfeed_status": _ds("Power Feeds by Status", "dcim", "PowerFeed", "status", url="/dcim/power-feeds/", param="status"),
    "powerfeed_type": _ds("Power Feeds by Type", "dcim", "PowerFeed", "type", url="/dcim/power-feeds/", param="type"),
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
            choices=[
                ("pie", "Pie"),
                ("doughnut", "Doughnut"),
                ("bar", "Bar (Vertical)"),
                ("bar_horizontal", "Bar (Horizontal)"),
                ("polarArea", "Polar Area"),
            ],
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

        horizontal = chart_type == "bar_horizontal"
        js_chart_type = "bar" if horizontal else chart_type

        # Build per-slice filter URLs if the source supports it
        slice_urls = []
        for i, row in enumerate(rows):
            if source.list_url and source.filter_param and not row.get("_other"):
                raw = raw_values[i]
                if raw is not None:
                    slice_urls.append(f"{source.list_url}?{source.filter_param}={raw}")
                else:
                    slice_urls.append(None)
            else:
                slice_urls.append(None)

        return render_to_string(
            "netbox_widget_chart/chart_widget.html",
            {
                "chart_id": uuid.uuid4().hex,
                "chart_type": js_chart_type,
                "horizontal": json.dumps(horizontal),
                "chart_title": source.label,
                "chart_labels_json": json.dumps(labels),
                "chart_data_json": json.dumps(data),
                "chart_colors_json": json.dumps(palette),
                "slice_urls_json": json.dumps(slice_urls),
                "total": sum(data),
                "rows": list(zip(labels, data, palette)),
                "chartjs_url": chartjs_url,
            },
            request=request,
        )
