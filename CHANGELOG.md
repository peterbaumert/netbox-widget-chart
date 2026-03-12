# Changelog

## [0.2.0](https://github.com/peterbaumert/netbox-widget-chart/compare/v0.1.4...v0.2.0) (2026-03-12)


### Features

* add 19 new data sources across racks, VLANs, tenancy, and power ([94960fc](https://github.com/peterbaumert/netbox-widget-chart/commit/94960fc4644fd7ca0f34a19a07d667ba1e4e6c1e))
* add horizontal bar chart type ([3e0a480](https://github.com/peterbaumert/netbox-widget-chart/commit/3e0a480c0dab969de8cc965df77526def53fad6a))
* add NetBox integration CI workflow ([cc33df2](https://github.com/peterbaumert/netbox-widget-chart/commit/cc33df2fefec685245bb58d5cc5b4bba8c6ae31f))
* add unit tests for widget render logic and data sources ([6a7483e](https://github.com/peterbaumert/netbox-widget-chart/commit/6a7483ee2f60abde552e0ac96d320f07e95791b7))
* auto-update COMPATIBILITY.md on release ([03820a3](https://github.com/peterbaumert/netbox-widget-chart/commit/03820a3d8aa68618724a91d91c1cd96b71261c69))
* click chart segments to navigate to filtered NetBox list view ([2185d75](https://github.com/peterbaumert/netbox-widget-chart/commit/2185d755944a70d537d6a1b3f9b997210ca155d5))
* respect NetBox dark/light mode for chart text and border colors ([b5600b0](https://github.com/peterbaumert/netbox-widget-chart/commit/b5600b0e7568be1a7686aab47fdf809b2d996b3c))
* show empty state message when data source has no results ([ab85034](https://github.com/peterbaumert/netbox-widget-chart/commit/ab85034f11a84ab73d170df5f799b94a2fc63ec1))


### Bug Fixes

* expose postgres and redis ports in integration CI service containers ([e8d81e6](https://github.com/peterbaumert/netbox-widget-chart/commit/e8d81e6fb3bf04a1130a41fe21f03d1cda9698af))
* update COMPATIBILITY.md in release PR so it's included in the tag ([4f4d851](https://github.com/peterbaumert/netbox-widget-chart/commit/4f4d85158d7f867c65965838bbbf5309f2ddd040))
* use SECRET_KEY of sufficient length for NetBox CI ([88e06ec](https://github.com/peterbaumert/netbox-widget-chart/commit/88e06ec1337fb7c4c830a200044409a126c6a2b0))
* write NetBox configuration.py to correct package directory ([56308e1](https://github.com/peterbaumert/netbox-widget-chart/commit/56308e1951aaf63b9e15e11dc8e3e681828233f4))


### Documentation

* replace inline compatibility table with link to COMPATIBILITY.md ([b6f30e6](https://github.com/peterbaumert/netbox-widget-chart/commit/b6f30e6fc048231e252e7548a1713ec56b1b3a00))
* update COMPATIBILITY.md with versions 0.1.1 through 0.1.3 ([325e893](https://github.com/peterbaumert/netbox-widget-chart/commit/325e89316f3b783294a28b4335f12aeeee7245d4))

## [0.1.4](https://github.com/peterbaumert/netbox-widget-chart/compare/v0.1.3...v0.1.4) (2026-03-12)


### Bug Fixes

* cast ColorChoices labels to str to fix JSON serialization error ([7f33061](https://github.com/peterbaumert/netbox-widget-chart/commit/7f330612a47095d856d08272abcf40274f20ef5c))

## [0.1.3](https://github.com/peterbaumert/netbox-widget-chart/compare/v0.1.2...v0.1.3) (2026-03-12)


### Bug Fixes

* use PAT in release-please to allow triggering release workflow ([5c193cf](https://github.com/peterbaumert/netbox-widget-chart/commit/5c193cfd3047fa475fed9d9cd2792de529f283fc))

## [0.1.2](https://github.com/peterbaumert/netbox-widget-chart/compare/v0.1.1...v0.1.2) (2026-03-12)


### Bug Fixes

* update README description to reflect all chart types ([4e8a547](https://github.com/peterbaumert/netbox-widget-chart/commit/4e8a5470c010f729683ed08ba83e0ff75b925394))
