from netbox.plugins import PluginConfig


class PieChartWidgetConfig(PluginConfig):
    name = "netbox_piechart_widget"
    verbose_name = "NetBox Pie Chart Widget"
    description = "A configurable pie/doughnut chart dashboard widget for NetBox"
    version = "0.1.0"
    author = "Pete"
    author_email = ""
    base_url = "piechart-widget"
    min_version = "4.0.0"
    required_settings = []
    default_settings = {
        "CHARTJS_URL": "https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js",
    }

    def ready(self):
        super().ready()
        from . import widgets  # noqa: F401 — triggers widget registration


config = PieChartWidgetConfig
