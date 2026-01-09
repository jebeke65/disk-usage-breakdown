# Disk Usage Breakdown (Home Assistant custom integration)

Creates sensors that show disk space usage split into categories (paths) plus an automatically computed **Other** category.

## Features
- UI config via Config Flow (Settings → Devices & services → Add Integration)
- Sensors for each category in **MB** (directory/file sizes)
- Sensors for disk total/used/free on a mount point
- **Other** = used - sum(categories), clamped to 0 (so you can later split "Other" into more categories)

## Notes
- Directory sizes are measured using `du` on the Home Assistant host/container.
- For best results on Home Assistant OS / Supervised, keep all category paths on the same filesystem as the mount point (default `/`).

## Installation (HACS)
1. Add this repository to HACS as a **custom repository** (Integration).
2. Install **Disk Usage Breakdown**.
3. Restart Home Assistant.
4. Add the integration via UI.

## Default categories
- DB: `/config/home-assistant_v2.db`
- Backups: `/backup`
- Media: `/media`
- Share: `/share`
- Add-ons: `/addons`

You can change/disable categories in the integration **Options**.

## Pie chart example (ApexCharts Card)
```yaml
type: custom:apexcharts-card
chart_type: pie
header:
  show: true
  title: Diskruimte (split)
series:
  - name: DB
    data: "{{ states('sensor.disk_usage_db_mb') | float(0) }}"
  - name: Backups
    data: "{{ states('sensor.disk_usage_backups_mb') | float(0) }}"
  - name: Media
    data: "{{ states('sensor.disk_usage_media_mb') | float(0) }}"
  - name: Share
    data: "{{ states('sensor.disk_usage_share_mb') | float(0) }}"
  - name: Add-ons
    data: "{{ states('sensor.disk_usage_add_ons_mb') | float(0) }}"
  - name: Other
    data: "{{ states('sensor.disk_usage_other_mb') | float(0) }}"
apex_config:
  legend:
    position: bottom
  tooltip:
    y:
      formatter: |
        EVAL:function(val){ return `${val.toFixed(0)} MB`; }
```
