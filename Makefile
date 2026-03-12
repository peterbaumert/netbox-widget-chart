.PHONY: fix lint

fix:
	.venv/bin/ruff check --fix netbox_piechart_widget/
	.venv/bin/black netbox_piechart_widget/

lint:
	.venv/bin/ruff check netbox_piechart_widget/
	.venv/bin/black --check netbox_piechart_widget/
