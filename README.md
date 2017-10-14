# rpi-alarm-clock
Code for creating an alarm clock dedicated to NPR

## NPR One Setup
there is a [python library](https://github.com/perrydc/npr) for using the NPR One API.  Once connected, you can use:

```python
import npr
npr.login()
station = npr.Station('WNYC')
station.live()
```
The ```station.live()``` command will return a live stream link.  I should be able to then send this into another application on the RPi.

## I2S Hardware
The audio will be sent out of the I2S pins into the [I2S Class D Amplifyer MAX98357A](https://www.adafruit.com/product/3006).  The breakout board needs three I2S connections to the RPi as well as +5v and Gnd.

```
Amp   - RPi
-----------
Vin   - 5V
GND   - GND
BCLK  - BCM 18 (pin 12)
LRCLK - BCM 19 (pin 35)
DIN   - BCM 21 (pin 40)
```
