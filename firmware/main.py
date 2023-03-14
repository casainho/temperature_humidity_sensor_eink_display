import time
import board
import displayio
import busio
import adafruit_ssd1681
from adafruit_display_text import label
import alarm
import supervisor
import sensor as Sensor
from circuitpython_uplot.uplot import Uplot, color
from circuitpython_uplot.ulogging import ulogging
from adafruit_bitmap_font import bitmap_font
import alarm

# disable auto-reload
supervisor.runtime.autoreload = False

###############################################################
# Let's keep track of number of times we run, by incrementing a counter

# NOTE: alarm.sleep_memory array size is 4096 bytes on ESP32-S2, CircuitPyhton 8.0.3

if not alarm.wake_alarm:
  # reset counter at a power on reset
  counter = 0
else:
  # get the counter
  counter = (alarm.sleep_memory[0] << 16) + (alarm.sleep_memory[1] << 8) + alarm.sleep_memory[2]
   
# let's increase the counter
counter += 1

# store the counter
alarm.sleep_memory[0] = (counter >> 16 & 0xff)
alarm.sleep_memory[1] = (counter >> 8 & 0xff)
alarm.sleep_memory[2] = (counter & 0xff)
###############################################################

###############################################################
# initialize the display
displayio.release_displays()

spi = busio.SPI(
    board.IO5, # CLK pin
    board.IO3, # MOSI pin
    None) # MISO pin, not need to drive this display

display_bus = displayio.FourWire(
    spi,
    command = board.IO9,
    reset = board.IO11,
    chip_select = board.IO7,
    baudrate = 60000000)

display = adafruit_ssd1681.SSD1681(display_bus, width = 200, height = 200, busy_pin = board.IO12, rotation = 0)
###############################################################

###############################################################
# initialize the sensor
sensor = Sensor.Sensor(board.IO37, board.IO35)
# read the sensor values
sensor.run_periodic()
###############################################################


g = displayio.Group()

# Set a white background
# Create the display object - the third color is red (0xff0000)
DISPLAY_WIDTH = 200
DISPLAY_HEIGHT = 200
FOREGROUND_COLOR = color.BLACK
BACKGROUND_COLOR = color.WHITE

background_bitmap = displayio.Bitmap(DISPLAY_WIDTH, DISPLAY_HEIGHT, 1)
# Map colors in a palette
palette = displayio.Palette(1)
palette[0] = BACKGROUND_COLOR
# Create a Tilegrid with the background and put in the displayio group
t = displayio.TileGrid(background_bitmap, pixel_shader=palette)
g.append(t)

# custom fonts
font_small = bitmap_font.load_font("fonts/Ubuntu-R-12.bdf")
font_medium = bitmap_font.load_font("fonts/Ubuntu-R-18.bdf")
font_big = bitmap_font.load_font("fonts/Ubuntu-R-42.bdf")

# numeric values
text_temperature = label.Label(font_big, color=FOREGROUND_COLOR, scale=1)
text_temperature.anchored_position = 70, 2
text_temperature.anchor_point = 1.0, 0.0
g.append(text_temperature)

text_temperature_unity = label.Label(font_medium, text='ºC', color=FOREGROUND_COLOR, scale=1)
text_temperature_unity.anchored_position = 73, 2
text_temperature_unity.anchor_point = 0.0, -1.3
g.append(text_temperature_unity)

text_humidity = label.Label(font_big, color=FOREGROUND_COLOR, scale=1)
text_humidity.anchored_position = 160, 2
text_humidity.anchor_point = 1.0, 0.0
g.append(text_humidity)

text_humidity_unity = label.Label(font_medium, text='%', color=FOREGROUND_COLOR, scale=1)
text_humidity_unity.anchored_position = 163, 2
text_humidity_unity.anchor_point = 0.0, -1.3
g.append(text_humidity_unity)

text_temperature.text = f'{int(round(sensor.temperature, 0))}'
text_humidity.text = f'{int(round(sensor.humidity, 0))}'

plot_1 = Uplot(
    21,
    46,
    179,
    63,
    padding=1,
    show_box=True,
    box_color=color.BLACK,
    background_color=color.WHITE,
    scale=8)

plot_2 = Uplot(
    0,
    79,
    179,
    63,
    padding=1,
    show_box=True,
    box_color=color.BLACK,
    background_color=color.WHITE,
    scale=4)

# Setting up tick parameters
plot_1.tick_params(tickx_height = 5, ticky_height = 5, tickcolor = color.BLACK, tickgrid = False)
plot_2.tick_params(tickx_height = 5, ticky_height = 5, tickcolor = color.BLACK, tickgrid = False)

# get the historic data of the sensors
historic_data_temperature, temperature_max, temperature_min, temperature_len = sensor.historic_data_temperature
historic_data_humidity, humidity_max, humidity_min, humidity_len = sensor.historic_data_humidity

# from random import choice
# temperatures = list(range(19, 32))
# humidity = list(range(60, 95))
# x = list(range(0, 144, 1))
# historic_data_temperature = [choice(temperatures) for _ in x]
# temperature_max = 32
# temperature_min = 0
# temperature_len = 144
# historic_data_humidity = [choice(humidity) for _ in x]
# humidity_max = 95

# calculate the max range y for temperature
if temperature_max > 55:
  temperature_range_y = temperature_max
elif temperature_max > 35:
  temperature_range_y = 60
elif temperature_max > 15:
  temperature_range_y = 40
else:
  temperature_range_y = 20

x = list(range(0, temperature_len))

ulogging(
  plot_1,
  x,
  historic_data_temperature,
  rangex=[0, 143],
  rangey=[0, temperature_range_y],
  line_color=color.BLACK,
  ticksx=[23, 47, 71, 95, 119, 143],
  ticksy=[10, 20, 30]
  )

ulogging(
  plot_2,
  x,
  historic_data_humidity,
  rangex=[0, 143],
  rangey=[0, 100],
  line_color=color.BLACK,
  ticksx=[23, 47, 71, 95, 119, 143],
  ticksy=[25, 50, 75]
  )

plot_1.append(plot_2)
g.append(plot_1)

# graph values
text_graph_temperature_min = label.Label(font_small, text=f'{temperature_min}', color=FOREGROUND_COLOR, scale=1)
text_graph_temperature_min.anchor_point = 0.5, 0.0
text_graph_temperature_min.anchored_position = 9, 100
g.append(text_graph_temperature_min)

text_graph_temperature_med = label.Label(font_small, text=f'{int(round(temperature_range_y / 2, 1))}', color=FOREGROUND_COLOR, scale=1)
text_graph_temperature_med.anchor_point = 0.5, 0.0
text_graph_temperature_med.anchored_position = 9, 74
g.append(text_graph_temperature_med)

text_graph_temperature_max = label.Label(font_small, text=f'{temperature_range_y}', color=FOREGROUND_COLOR, scale=1)
text_graph_temperature_max.anchor_point = 0.5, 0.0
text_graph_temperature_max.anchored_position = 9, 48
g.append(text_graph_temperature_max)

text_graph_humidity_min = label.Label(font_small, text='0', color=FOREGROUND_COLOR, scale=1)
text_graph_humidity_min.anchor_point = 0.5, 0.0
text_graph_humidity_min.anchored_position = 9, 179
g.append(text_graph_humidity_min)

text_graph_humidity_med = label.Label(font_small, text='50', color=FOREGROUND_COLOR, scale=1)
text_graph_humidity_med.anchor_point = 0.5, 0.0
text_graph_humidity_med.anchored_position = 9, 153
g.append(text_graph_humidity_med)

text_graph_humidity_max = label.Label(font_small, text='100', color=FOREGROUND_COLOR, scale=1)
text_graph_humidity_max.anchor_point = 0.5, 0.0
text_graph_humidity_max.anchored_position = 9, 127
g.append(text_graph_humidity_max)

text_graph_temperature_x_12h = label.Label(font_small, text='12h', color=FOREGROUND_COLOR, scale=1)
text_graph_temperature_x_12h.anchor_point = 1.0, 1.0
text_graph_temperature_x_12h.anchored_position = 123, 120
g.append(text_graph_temperature_x_12h)

text_graph_temperature_x_24h = label.Label(font_small, text='24h', color=FOREGROUND_COLOR, scale=1)
text_graph_temperature_x_24h.anchor_point = 1.0, 1.0
text_graph_temperature_x_24h.anchored_position = 198, 120
g.append(text_graph_temperature_x_24h)

text_graph_humidity_x_12h = label.Label(font_small, text='12h', color=FOREGROUND_COLOR, scale=1)
text_graph_humidity_x_12h.anchor_point = 1.0, 1.0
text_graph_humidity_x_12h.anchored_position = 123, 199
g.append(text_graph_humidity_x_12h)

text_graph_humidity_x_24h = label.Label(font_small, text='24h', color=FOREGROUND_COLOR, scale=1)
text_graph_humidity_x_24h.anchor_point = 1.0, 1.0
text_graph_humidity_x_24h.anchored_position = 198, 199
g.append(text_graph_humidity_x_24h)

text_counter = label.Label(font_small, text=f'{counter}', color=FOREGROUND_COLOR, scale=1)
text_counter.anchor_point = 0.0, 1.0
text_counter.anchored_position = 4, 199
g.append(text_counter)

display.show(g)
display.refresh()

# sleep for 180 seconds that is the min time of display refresh
seconds_to_sleep = 180
alarm_to_sleep = alarm.time.TimeAlarm(monotonic_time = time.monotonic() + seconds_to_sleep)
alarm.exit_and_deep_sleep_until_alarms(alarm_to_sleep)
# Does not return. Exits, and restarts after the sleep time.

