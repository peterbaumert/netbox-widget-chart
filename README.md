# netbox-widget-chart

A configurable chart dashboard widget for [NetBox](https://github.com/netbox-community/netbox).

## Features

- Pie, doughnut, bar, and polar area chart types
- 11 built-in data sources across DCIM, virtualization, IPAM, and circuits
- Configurable maximum number of slices (excess grouped as "Other")
- Powered by Chart.js (loaded lazily from CDN)

## Compatibility

| Plugin Version | NetBox Version |
|----------------|----------------|
| 0.1.0          | 4.5            |

## Installation

```bash
pip install netbox-widget-chart
```

Add the plugin to `PLUGINS` in your NetBox `configuration.py`:

```python
PLUGINS = [
    'netbox_widget_chart',
]
```

Restart NetBox after installing.

## Configuration

Optional settings in `configuration.py`:

```python
PLUGINS_CONFIG = {
    "netbox_widget_chart": {
        # Chart.js source URL. Options:
        # - CDN URL (default)
        # - Local static path e.g. "/static/netbox_widget_chart/chart.js"
        # - None to skip loading (if Chart.js is already provided globally)
        "CHARTJS_URL": "https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js",
    }
}
```

## Usage

1. Navigate to the NetBox dashboard
2. Click **Add Widget**
3. Select **Chart**
4. Configure the data source, chart type, and max slices

## Available Data Sources

| Key                | Description               |
|--------------------|---------------------------|
| `device_status`    | Devices by Status         |
| `device_role`      | Devices by Role           |
| `device_site`      | Devices by Site           |
| `device_platform`  | Devices by Platform       |
| `device_type`      | Devices by Type           |
| `vm_status`        | VMs by Status             |
| `vm_cluster`       | VMs by Cluster            |
| `prefix_status`    | Prefixes by Status        |
| `ipaddress_status` | IP Addresses by Status    |
| `circuit_status`   | Circuits by Status        |
| `circuit_type`     | Circuits by Type          |
| `cable_type`       | Cables by Type            |
| `cable_color`      | Cables by Color           |
| `cable_status`     | Cables by Status          |
| `cable_tenant`     | Cables by Tenant          |

## License

Apache 2.0

## Development

This plugin was coded entirely with [Claude](https://claude.ai) (Anthropic).
