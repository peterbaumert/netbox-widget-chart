# netbox-widget-piechart

A configurable pie/doughnut chart dashboard widget for [NetBox](https://github.com/netbox-community/netbox).

## Features

- Pie and doughnut chart types
- 11 built-in data sources across DCIM, virtualization, IPAM, and circuits
- Configurable maximum number of slices (excess grouped as "Other")
- Powered by Chart.js (loaded lazily from CDN)

## Compatibility

| Plugin Version | NetBox Version |
|----------------|----------------|
| 0.1.0          | 4.5            |

## Installation

```bash
pip install netbox-widget-piechart
```

Add the plugin to `PLUGINS` in your NetBox `configuration.py`:

```python
PLUGINS = [
    'netbox_piechart_widget',
]
```

Restart NetBox after installing.

## Configuration

Optional settings in `configuration.py`:

```python
PLUGINS_CONFIG = {
    "netbox_piechart_widget": {
        # Chart.js source URL. Options:
        # - CDN URL (default)
        # - Local static path e.g. "/static/netbox_piechart_widget/chart.js"
        # - None to skip loading (if Chart.js is already provided globally)
        "CHARTJS_URL": "https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js",
    }
}
```

## Usage

1. Navigate to the NetBox dashboard
2. Click **Add Widget**
3. Select **Pie Chart**
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
