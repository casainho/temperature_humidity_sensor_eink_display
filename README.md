# DIY Temperature and Humidity sensor using EInk display

**CURRENT STATE**: testing to see for how long a 3xAAA NiMh batteries can run the system.

[<img src=prototype_02-2023.03.20.jpg width=300>](prototype_01-2023.02.24.jpg)
[<img src=prototype_01-2023.03.20.jpg width=173>](prototype_01-2023.02.24.jpg)

This is a simple DIY Temperature and Humidity sensor, with a small EInk display and integration with Home Assistant.

**Main characteristics:** 
* Easy DIY, OpenSource and easy repairable
* Uses the factory calibrated temperature and humidity sensor AHT21
* The display is a 1.54 inches EInk display
* The microcontroller board is the ESP32-S2, running Pyhton (CircuitPython) firmware
* The systemn runs from a pair of NiMH batteries or one Lithium-ion battery, as the DC-DC boost converter supports input voltage from 1V up to 5V, and outputs a fixed 5V

All the components were bought on Aliexpress.

## Status and planned features
- [x] Develop and test the electronics
- [x] Develop and test the 3D printed enclosure
- [x] Show numeric values of humidity and temperature
- [x] Optimize the power usage
- [x] [Show graph from last 24h of humidity and temperature (10 minutes each measurement)](https://github.com/jposada202020/CircuitPython_uplot)
- [ ] [Send humidity and temperature to HomeAssistant](https://learn.adafruit.com/temperature-and-humidity-sensing-in-home-assistant-with-circuitpython)

## Pictures

Pictures from prototype on 2023.02.22.

Showing the temperature and humidity values:<br>
[<img src=prototype_01-2023.02.24.jpg width=300>](prototype_01-2023.02.24.jpg)

Details of the 3D printed enclosure:<br>
[<img src=prototype_02-2023.02.24.jpg width=322>](prototype_02-2023.02.24.jpg) [<img src=prototype_03-2023.02.24.jpg height=200>](prototype_03-2023.02.24.jpg)

Details of the DIY electronics:<br>
[<img src=prototype_01-2023.02.22.jpg width=300>](prototype_01-2023.02.22.jpg)

Details of the DIY build. Black board is the 1.54 inches EInk display, the purple board is the ESP32-S2 board (Lolin S2 Mini), the blue board is the AHT21 sensor and the green board is a DC-DC boost converter module that transforms the 2.4V from the NiMH batteries to 5V to power the ESP32-S2 board and all other components:<br>
[<img src=prototype_02-2023.02.22.jpg width=300>](prototype_02-2023.02.22.jpg)
