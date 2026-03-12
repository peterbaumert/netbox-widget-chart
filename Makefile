.PHONY: fix lint

fix:
	.venv/bin/ruff check --fix netbox_widget_chart/
	.venv/bin/black netbox_widget_chart/

lint:
	.venv/bin/ruff check netbox_widget_chart/
	.venv/bin/black --check netbox_widget_chart/
