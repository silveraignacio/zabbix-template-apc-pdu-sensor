# Changelog

## 1.0.0
- Initial public release.
- SNMP LLD over `rPDU2SensorTempHumidityStatusTable`, filtered by sensor type (1, 2).
- Items: temperature, humidity, PDU temperature/humidity status, communication status.
- Warning/critical triggers for high/low temperature and humidity, communication-lost and no-data triggers.
- All thresholds exposed as macros.
