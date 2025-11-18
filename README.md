# rd60xx_python

Control RuiDeng rd60xx via python.

## Installation Requirements

```bash
pip install -r requirements.txt
```

## Example

```python
from rd60xx import RD60XX

rd60xx = RD60XX(port='COM12', baudrate=115200, device_id=1)
rd60xx.connect()

model = rd60xx.read_product_model()
logger.info(f"{"product_model:       "} {model}")

rd60xx.set_voltage(12.000)
voltage = rd60xx.read_voltage_setting()
logger.info(f"{"voltage_setting:       "} {voltage:06.3f}V")

rd60xx.set_current(0.100)
current = rd60xx.read_current_setting()
logger.info(f"{"current_setting:       "} {current:06.3f}A")

rd60xx.on()

rd60xx.disconnect()
```
