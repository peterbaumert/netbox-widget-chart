from netbox.plugins import PluginConfig


class ChartWidgetConfig(PluginConfig):
    name = "netbox_widget_chart"
    verbose_name = "NetBox Chart Widget"
    description = "A configurable pie/doughnut chart dashboard widget for NetBox"
    version = "0.1.0"
    author = "Pete"
    author_email = ""
    base_url = "chart-widget"
    min_version = "4.0.0"
    required_settings = []
    default_settings = {
        "CHARTJS_URL": "https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js",
    }

    def ready(self):
        super().ready()
        from . import widgets  # noqa: F401 — triggers widget registration


config = ChartWidgetConfig
