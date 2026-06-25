# DIY CO2 Monitor with ESP32-C3, SCD41 and E-Ink Display

This is a simple DIY indoor air quality monitor based on an **ESP32-C3**, a **Sensirion SCD41** sensor and a small **E-Ink display**.

The device is designed to periodically measure real CO2 concentration, temperature and relative humidity, show the latest values on the display, and then enter a low-power sleep mode to save battery.

The project is intended to be:

* easy to build;
* open source;
* repairable;
* battery powered;
* low power;
* suitable for indoor air quality monitoring.

## Features

* Measures real CO2 concentration using the Sensirion SCD41 sensor.
* Measures temperature and relative humidity.
* Shows the latest readings on a 1.54 inch E-Ink display.
* Uses an ESP32-C3 microcontroller.
* Firmware written in MicroPython.
* Designed for low-power operation using deep sleep.
* Powered from NiMH batteries through a 3.3 V DC-DC buck converter.
* Uses a DD2712SA 3.3 V buck converter module.
* Periodic measurement and display update.
* Future option: send measurements to Home Assistant.

## Main characteristics

* Microcontroller: ESP32-C3.
* Sensor: Sensirion SCD41.
* Display: 1.54 inch E-Ink display.
* Firmware: MicroPython.
* Power supply: NiMH batteries.
* DC-DC converter: DD2712SA 3.3 V buck converter.
* Operating mode: wake up, measure, update display, deep sleep.
* Typical update interval: 5 minutes.

---

# Hardware

## Hardware overview

The hardware architecture is:

```text
4x NiMH batteries
   |
   |---- Power switch
   |
DD2712SA 3.3 V buck converter
   |
   +---- ESP32-C3
   +---- Sensirion SCD41
   +---- E-Ink display
```

## Main components

| Component         | Description                                                 |
| ----------------- | ----------------------------------------------------------- |
| ESP32-C3          | Main microcontroller running the MicroPython firmware       |
| Sensirion SCD41   | CO2, temperature and humidity sensor                        |
| E-Ink display     | Low-power display for showing the latest values             |
| DD2712SA 3.3 V    | DC-DC buck converter used to generate the 3.3 V supply rail |
| 4x NiMH batteries | Rechargeable battery pack                                   |
| Power switch      | Main power switch                                           |
| Capacitors        | Used to stabilize the 3.3 V rail during current peaks       |

## ESP32-C3

The project uses an **ESP32-C3** microcontroller.

The ESP32-C3 is responsible for:

* controlling the complete device;
* communicating with the SCD41 sensor using I2C;
* updating the E-Ink display;
* measuring the battery voltage, if implemented;
* managing the sleep/wake cycle;
* running the MicroPython firmware.

## Sensor

The project uses the **Sensirion SCD41** sensor.

The SCD41 measures:

* CO2 concentration, in ppm;
* temperature, in degrees Celsius;
* relative humidity, in percent.

The sensor communicates with the ESP32-C3 using I2C.

## Power supply

The device is powered from rechargeable **NiMH batteries**.

The recommended power architecture is:

```text
4x NiMH batteries
   |
DD2712SA 3.3 V buck converter
   |
3.3 V system rail
```

The DD2712SA 3.3 V module converts the battery voltage to a regulated 3.3 V supply for the ESP32-C3, SCD41 and E-Ink display.

---

# Firmware

## Firmware overview

The firmware is written in **MicroPython**.

The main firmware goal is to:

1. wake up from deep sleep;
2. initialize the required peripherals;
3. read the SCD41 sensor;
4. update the E-Ink display;
5. optionally measure battery voltage;
6. enter deep sleep again.

## Main firmware cycle

```text
Boot
  |
Initialize I2C
  |
Initialize SCD41
  |
Read CO2, temperature and humidity
  |
Read battery voltage
  |
Update E-Ink display
  |
Prepare peripherals for low-power mode
  |
Enter deep sleep
  |
Wake up after configured interval
```

## Suggested firmware structure

A modular MicroPython firmware structure is recommended:

```text
main.py
config.py
scd41.py
display.py
battery.py
power.py
```

## main.py

Main entry point.

Responsibilities:

* load configuration;
* initialize hardware;
* call the sensor reading functions;
* update the display;
* decide the next sleep interval;
* enter deep sleep.

## config.py

Project configuration.

Example:

```python
SLEEP_MINUTES = 5

I2C_SCL_PIN = 9
I2C_SDA_PIN = 8

BATTERY_CELLS = 4
LOW_BATTERY_VOLTAGE = 4.2
CRITICAL_BATTERY_VOLTAGE = 4.0

DISPLAY_ROTATION = 0
USE_WIFI = False
```

The exact I2C pins should be adjusted according to the ESP32-C3 board being used.

## scd41.py

SCD41 handling.

Responsibilities:

* initialize the SCD41 sensor;
* start measurements;
* wait until data is ready;
* read CO2, temperature and humidity;
* return a structured data object.

Example returned values:

```python
{
    "co2_ppm": 820,
    "temperature_c": 22.4,
    "humidity_percent": 54.0
}
```

## display.py

E-Ink display handling.

Responsibilities:

* initialize the display;
* draw the static layout;
* show CO2, temperature and humidity;
* show battery state;
* show warning messages;
* refresh the display.

Suggested status messages:

|        CO2 level | Display status          |
| ---------------: | ----------------------- |
|    Below 800 ppm | Good                    |
|  800 to 1200 ppm | Ventilation recommended |
| 1200 to 2000 ppm | Poor air quality        |
|   Above 2000 ppm | Ventilate urgently      |

## battery.py

Battery measurement and classification.

Responsibilities:

* read the ADC value;
* convert ADC reading to battery voltage;
* classify battery state;
* return battery voltage and status.

## power.py

Low-power handling.

Responsibilities:

* turn off unused peripherals when possible;
* disable Wi-Fi if not needed;
* prepare the ESP32-C3 for deep sleep;
* configure the wake-up timer.

Recommended approach:

* keep Wi-Fi disabled by default;
* keep active time as short as possible;
* avoid permanent LEDs;
* avoid unnecessary display refreshes;
* use deep sleep between measurements.

---

# Technical information

* The enclosure was designed in [FreeCAD](https://www.freecad.org/).
* The firmware is written in [MicroPython](https://micropython.org/).
* The microcontroller is an ESP32-C3.
* The display is a 1.54 inch E-Ink display.
* The CO2 sensor is the Sensirion SCD41.
* The power converter is the DD2712SA 3.3 V buck converter.
* The system is designed for periodic measurements and low-power sleep operation.
