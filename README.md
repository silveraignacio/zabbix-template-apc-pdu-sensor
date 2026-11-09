# Zabbix template: APC PDU temperature & humidity sensor (SNMP)

A Zabbix template that monitors the **temperature and humidity probes** (APC AP9335TH / AP9335T) attached to APC **rPDU2** PDUs (e.g. AP8858EU3, AP8xxx), using SNMP low-level discovery (LLD).

It discovers only the ports that really have a probe, so you can safely link it to PDUs with or without sensors without getting "unsupported item" noise.

## Why this template

Templates that hardcode the sensor table index (for example `...26.10.2.2.1.8.2`) and a fixed humidity column break on most PDUs: the index differs, the port may be empty, or the column is wrong. This template instead:

- Discovers rows of `rPDU2SensorTempHumidityStatusTable` and **filters by sensor type** (1 = temperature, 2 = temperature + humidity). Ports with no probe (type 4, all values `-1`) are ignored.
- Tolerates PDUs that do not implement the table (the rule just becomes unsupported and creates nothing).
- Converts temperature from tenths of a degree to °C and discards the `-1` "no reading" value.
- Ships warning and critical triggers for high/low temperature and humidity, plus a communication-lost trigger. **All thresholds are user macros.**

## Requirements

- Zabbix **7.0 or newer** (export format 7.0; tested by import on Zabbix 7.2.6).
- SNMP (v1/v2c/v3) reachability to the PDU, with an SNMP interface on the host.
- APC PowerNet-MIB `rPDU2` support (PDU firmware with the `rPDU2SensorTempHumidityStatusTable`).

## Installation

1. In Zabbix go to **Data collection → Templates → Import** and select `template/template_apc_pdu_sensor_temp_humidity.yaml`.
2. Link **APC PDU Temperature-Humidity Sensor by SNMP** to the PDUs that have a probe connected.
3. Make sure each host has an SNMP interface and the `{$SNMP_COMMUNITY}`/SNMPv3 settings it needs.
4. Optionally override the macros below per host, host group or template.

Tip: after linking, run the discovery rule once with *Execute now*; otherwise the first run can take up to an hour (discovery interval).

## How to know if a PDU has a probe

```bash
snmpwalk -v2c -c <community> <pdu-ip> .1.3.6.1.4.1.318.1.1.26.10.2.2.1.5
```

| Value of `...2.2.1.5` (type) | Meaning |
|---|---|
| 1 | Temperature-only probe |
| 2 | Temperature + humidity probe |
| 4 | Port without probe (not installed) |
| no such object / empty | PDU has no sensor table or no probes |

The communication column (`...2.2.1.6`) is `1` notInstalled, `2` commsOK, `3` commsLost.

## Macros

| Macro | Default | Description |
|---|---|---|
| `{$PDU.TEMP.HIGH.WARN}` | `27` | Temperature warning threshold, high (°C) |
| `{$PDU.TEMP.HIGH.CRIT}` | `32` | Temperature critical threshold, high (°C) |
| `{$PDU.TEMP.LOW.WARN}` | `18` | Temperature warning threshold, low (°C) |
| `{$PDU.TEMP.LOW.CRIT}` | `15` | Temperature critical threshold, low (°C) |
| `{$PDU.HUM.HIGH.WARN}` | `60` | Humidity warning threshold, high (%) |
| `{$PDU.HUM.HIGH.CRIT}` | `80` | Humidity critical threshold, high (%) |
| `{$PDU.HUM.LOW.WARN}` | `25` | Humidity warning threshold, low (%) |
| `{$PDU.HUM.LOW.CRIT}` | `20` | Humidity critical threshold, low (%) |
| `{$PDU.EVAL.WINDOW}` | `5m` | Evaluation window of the temperature/humidity triggers |
| `{$PDU.NODATA.TIME}` | `15m` | Time without data before alerting |

Defaults follow **ASHRAE TC 9.9** guidance for data centers: recommended 18–27 °C and relative humidity up to 60 %; allowable class A1 15–32 °C and 20–80 % RH. Adjust to your environment and keep the warning thresholds inside the critical ones (high: WARN < CRIT; low: WARN > CRIT).

## Discovered items (per probe)

| Item | OID | Notes |
|---|---|---|
| Temperature | `.1.3.6.1.4.1.318.1.1.26.10.2.2.1.8.<idx>` | tenths of °C → °C, `-1` discarded |
| Relative humidity | `.1.3.6.1.4.1.318.1.1.26.10.2.2.1.10.<idx>` | %, values outside 0–100 discarded |
| Temperature status (PDU) | `...2.2.1.9.<idx>` | PDU's own threshold state (value map) |
| Humidity status (PDU) | `...2.2.1.11.<idx>` | PDU's own threshold state (value map) |
| Communication status | `...2.2.1.6.<idx>` | 1 notInstalled / 2 commsOK / 3 commsLost |

Status values: 1 notPresent, 2 belowMin, 3 belowLow, 4 normal, 5 aboveHigh, 6 aboveMax. They reflect the thresholds configured on the PDU, independently of the Zabbix macros.

## Triggers (per probe)

| Trigger | Severity |
|---|---|
| Temperature HIGH (warning) | Warning |
| Temperature HIGH (critical) | High |
| Temperature LOW (warning) | Warning |
| Temperature LOW (critical) | High |
| Humidity HIGH (warning) | Warning |
| Humidity HIGH (critical) | High |
| Humidity LOW (warning) | Warning |
| Humidity LOW (critical) | High |
| Probe communication lost (CommStatus ≠ 2) | Average |
| No temperature data for `{$PDU.NODATA.TIME}` | Warning |

Warning triggers fire only while the value is between the WARN and CRIT thresholds, so they do not overlap with the critical ones. Triggers evaluate `min()` (high) or `max()` (low) over `{$PDU.EVAL.WINDOW}` to avoid flapping.

A faulty probe that reports absurd values (e.g. −55 °C) will raise the *temperature LOW (critical)* trigger, which is intended.

All items and triggers carry the tag `Application: Sensors`.

## Repository layout

```
template/   the importable Zabbix template (YAML)
scripts/    validation helper used by CI
.github/    CI workflow
```

## Contributing

Issues and pull requests are welcome, especially firmware/model reports (which PDUs and probes work or not). If you change the template, run `python3 scripts/validate_template.py` before opening a PR.

## References

- APC PowerNet-MIB, `rPDU2SensorTempHumidityStatusTable` (`.1.3.6.1.4.1.318.1.1.26.10.2.2`).
- ASHRAE TC 9.9, *Thermal Guidelines for Data Processing Environments*.
- [Zabbix template guidelines](https://www.zabbix.com/documentation/current/en/manual/config/templates/template).

## License

MIT, see [LICENSE](LICENSE).
