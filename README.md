# rpi-alarm-clock
Code for creating an alarm clock dedicated to NPR

## Hardware Setup
### I2S Audio Amplifyer MAX98357A
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

I followed [Adafruit's Tutorial](https://learn.adafruit.com/adafruit-max98357-i2s-class-d-mono-amp/raspberry-pi-usage) to configure the software.  I'm starting with a fresh Raspian Image and followed both the standard setup, the 'reduce popping' section and the software audio control section.  Everything worked immediately.

### ILI9341 Display
The time and temperature will be displayed on the [2.2" 18bit color TFT LCD Display](https://www.adafruit.com/product/1480).  The display is controled over SPI and will need three jumpers to be soldered in order to be in SPI mode permanately.  See [this page](https://learn.adafruit.com/user-space-spi-tft-python-library-ili9341-2-8/wiring) for making the connection to the RPi.

```
Display - RPi
-----------
Vin     - 5V
GND     - GND
BL      - None
SCK     - BCM 11 (pin 23)
MISO    - None
MOSI    - BCM 10 (pin 19)
CS      - BCM 08 (pin 24)
SDCS    - None
RST     - BCM 23 (pin 16)
D/C     - BCM 18 (pin 12)
```

## Software Overview
Run ```sudo raspi-config``` to perform some basic setup.  Make sure to turn on ```spi```.  Then install required software: 

```
# install dependencies
sudo apt-get update
sudo apt-get install -y build-essential git python-dev python-setuptools python-pip python-smbus python-imaging python-numpy
sudo apt-get install -y vlc

# install ILI9341 Python Library
git clone https://github.com/adafruit/Adafruit_Python_ILI9341.git
cd Adafruit_Python_ILI9341/
sudo python setup.py install
cd ../
sudo rm -rf Adafruit_Python_ILI9341/

# install python libraries
sudo pip install tornado 
sudo pip install python-vlc
sudo pip install python-crontab
sudo pip install npr
sudo pip install supervisor

# Install Radio software
git clone https://github.com/nejohnson2/rpi-alarm-clock.git
cd rpi-alarm-clock/

```

In order to auto boot at startup:
```
# Autolaunch supervisord first
sudo cp /home/pi/rpi-alarm-clock/supervisord /etc/init.d/supervisord
sudo chmod +x /etc/init.d/supervisord
sudo update-rc.d supervisord defaults

# Add conf file for the app
sudo mkdir /etc/supervisor
sudo cp /home/pi/rpi-alarm-clock/supervisord.conf /etc/supervisor/supervisord.conf 
```

About font sizes [here](http://www.geeks3d.com/20100930/tutorial-first-steps-with-pil-python-imaging-library/#p06)

### NPR One Setup
there is a [python library](https://github.com/perrydc/npr) for using the NPR One API.  Once connected, you can use:

```python
import npr
npr.login()
station = npr.Station('WNYC')
station.live()
```
The ```station.live()``` command will return a live stream link.  I should be able to then send this into another application on the RPi.

### Static IP on Rpi
This information was obtained from [this stack overflow discussion](https://raspberrypi.stackexchange.com/questions/37920/how-do-i-set-up-networking-wifi-static-ip-address/74428#74428)

First you need to get the **default gateway IP** address of your router.  This is usually something like 192.168.0.1.  You then need to get the IP address of your **domain name server** (DNS server).  View the routing table with ```route -ne``` or the default gateway with:

```
# view the routing table to obtain default gateway IP
$ ip route | grep default | awk '{print $3}'

# view DNS server IP information information
$ cat /etc/resolv.conf
```
Finally, edit the ```/etc/dhcpcd.conf``` file by adding:

```
interface wlan0
static ip_address=<rpi_ip_address>
static routers=<default_gateway_ip>
static domain_name_servers=<server_1> <server_2>
```
Then reboot!
