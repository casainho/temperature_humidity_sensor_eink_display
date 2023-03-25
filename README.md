# DIY Temperature and Humidity sensor using EInk display

[<img src=doc/prototype_02-2023.03.20.jpg width=300>](doc/prototype_02-2023.03.20.jpg)
[<img src=doc/prototype_01-2023.03.20.jpg width=173>](doc/prototype_01-2023.03.20)

This is a simple DIY Temperature and Humidity sensor, with a small EInk display and (future) integration with Home Assistant.

**Features:**
  * shows the numeric value of temperature and relative humidity (measured at every 10 minutes)
  * shows two graphs with the temperature and relative humidity (measured at every 10 minutes), from the last 24h
  * PLANNED: [Send temperature and relative humidity to HomeAssistant](https://learn.adafruit.com/temperature-and-humidity-sensing-in-home-assistant-with-circuitpython)

**Main characteristics:** 
* Easy DIY, OpenSource and easy repairable
* Uses the factory calibrated temperature and humidity sensor AHT21
* The display is a 1.54 inches EInk display
* The microcontroller board is the ESP32-S2, running Pyhton (CircuitPython) firmware
* The systemn runs from a USB-C cable or from some other power supply source like 3xAAA NiMh batteries, as there is a DC-DC boost converter that supports input voltage from 1V up to 5V, and outputs a fixed 5V

All the components were bought on Aliexpress.

## Pictures

Pictures from prototype on 2023.02.22.

Showing the temperature and humidity values:<br>
[<img src=doc/prototype_01-2023.02.24.jpg width=300>](doc/prototype_01-2023.02.24.jpg)

Details of the 3D printed enclosure:<br>
[<img src=doc/prototype_02-2023.02.24.jpg width=322>](doc/prototype_02-2023.02.24.jpg) [<img src=doc/prototype_03-2023.02.24.jpg height=200>](doc/prototype_03-2023.02.24.jpg)

Details of the DIY electronics:<br>
[<img src=doc/prototype_01-2023.02.22.jpg width=300>](doc/prototype_01-2023.02.22.jpg)

Details of the DIY build. Black board is the 1.54 inches EInk display, the purple board is the ESP32-S2 board (Lolin S2 Mini), the blue board is the AHT21 sensor and the green board is a DC-DC boost converter module that transforms the 2.4V from the NiMH batteries to 5V to power the ESP32-S2 board and all other components:<br>
[<img src=doc/prototype_02-2023.02.22.jpg width=300>](doc/prototype_02-2023.02.22.jpg)

## Tecnhical information
* the 3D printed enclosure was designed in [FreeCAD](https://www.freecad.org/)
* the firmware is developed in [CircuitPython](https://circuitpython.org/)
* the graphs are implemented using the [uplot library](https://github.com/jposada202020/CircuitPython_uplot)

