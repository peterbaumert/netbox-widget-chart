.PHONY: fix lint

fix:
	.venv/bin/ruff check --fix netbox_chart_widget/
	.venv/bin/black netbox_chart_widget/

lint:
	.venv/bin/ruff check netbox_chart_widget/
	.venv/bin/black --check netbox_chart_widget/
