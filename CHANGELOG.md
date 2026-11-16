# Changelog

## 1.1.0
- Graph prototypes per probe: temperature (°C) and relative humidity (%).
- Validation script checks graph prototypes (LLD macro in the name, template host, existing item keys, colors).

## 1.0.0
- Initial public release.
- SNMP LLD over `rPDU2SensorTempHumidityStatusTable`, filtered by sensor type (1, 2).
- Items: temperature, humidity, PDU temperature/humidity status, communication status.
- Warning/critical triggers for high/low temperature and humidity, communication-lost and no-data triggers.
- All thresholds exposed as macros.
