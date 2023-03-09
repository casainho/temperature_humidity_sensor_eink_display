import time
import board
import displayio
import busio
import adafruit_ssd1681
from adafruit_display_text import label
import terminalio
import alarm
import supervisor
import sensor as Sensor
from ulab import numpy as np
from circuitpython_uplot.uplot import Uplot
from circuitpython_uplot.ucartesian import ucartesian
import supervisor
from adafruit_bitmap_font import bitmap_font

# disable auto-reload
supervisor.runtime.autoreload = False

sensor = Sensor.Sensor(board.IO37, board.IO35)

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

g = displayio.Group()

# Set a white background
# Create the display object - the third color is red (0xff0000)
DISPLAY_WIDTH = 200
DISPLAY_HEIGHT = 200
BLACK = 0x000000
WHITE = 0xFFFFFF
FOREGROUND_COLOR = BLACK
BACKGROUND_COLOR = WHITE

background_bitmap = displayio.Bitmap(DISPLAY_WIDTH, DISPLAY_HEIGHT, 1)
# Map colors in a palette
palette = displayio.Palette(1)
palette[0] = BACKGROUND_COLOR
# Create a Tilegrid with the background and put in the displayio group
t = displayio.TileGrid(background_bitmap, pixel_shader=palette)
g.append(t)

text_temperature = label.Label(terminalio.FONT, color=FOREGROUND_COLOR, scale=3)
text_temperature.anchor_point = 0.0, 0.0
text_temperature.anchored_position = 25, 0
g.append(text_temperature)

text_humidity = label.Label(terminalio.FONT, color=FOREGROUND_COLOR, scale=3)
text_humidity.anchor_point = 0.0, 0.0
text_humidity.anchored_position = 130, 0
g.append(text_humidity)

sensor.run_periodic()
text_temperature.text = f'{sensor.temperature}'
text_humidity.text = f'{int(round(sensor.humidity, 0))}%'

# print('---------------')
# print(text_temperature.text)
# print(text_humidity.text)
# print('...')
# print(sensor.historic_data_temperature)
# print('...')
# print(sensor.historic_data_humidity)

# text_counter = label.Label(terminalio.FONT, color=FOREGROUND_COLOR, scale = 2)
# text_counter.anchor_point = 0.0, 0.0
# text_counter.anchored_position = 0, 180
# g.append(text_counter)

plot_1 = Uplot(
    20,
    50,
    179,
    60,
    padding = 1,
    show_box = True,
    box_color = BLACK,
    background_color = WHITE)

plot_2 = Uplot(
    0,
    80,
    179,
    60,
    padding = 1,
    show_box = True,
    box_color = BLACK,
    background_color = WHITE)

# # Setting up tick parameters
# plot_1.tick_params(tickx_height = 5, ticky_height = 5, tickcolor = BLACK, tickgrid = False)
# plot_2.tick_params(tickx_height = 5, ticky_height = 5, tickcolor = BLACK, tickgrid = False)

# print(len(sensor.historic_data_temperature))
# print(sensor.historic_data_temperature)

# get the historic data of the sensors
historic_data_temperature, temperature_max, temperature_min, temperature_len = sensor.historic_data_temperature
historic_data_humidity, humidity_max, humidity_min, humidity_len = sensor.historic_data_humidity

# calculate the max range y for temperature
if temperature_max > 55:
  temperature_range_y = temperature_max
elif temperature_max > 35:
  temperature_range_y = 60
elif temperature_max > 15:
  temperature_range_y = 40
else:
  temperature_range_y = 20

print(temperature_range_y)

x = list(range(0, temperature_len))
ucartesian(plot_1, x, historic_data_temperature, rangex=[0, 143], rangey=[0, temperature_range_y], fill=True, line_color=BLACK)
ucartesian(plot_2, x, historic_data_humidity, rangex=[0, 143], rangey=[0, 100], fill=True, line_color=BLACK)
plot_1.append(plot_2)
g.append(plot_1)

# graph values
font_10px = bitmap_font.load_font("fonts/Ubuntu-R-16.bdf")
text_graph_temperature_max = label.Label(font_10px, text=f'{temperature_range_y}', color=FOREGROUND_COLOR, scale=1)
text_graph_temperature_max.anchor_point = 0.0, 0.0
text_graph_temperature_max.anchored_position = 0, 48
g.append(text_graph_temperature_max)

text_graph_temperature_min = label.Label(font_10px, text='0', color=FOREGROUND_COLOR, scale=1)
text_graph_temperature_min.anchor_point = 0.0, 0.0
text_graph_temperature_min.anchored_position = 0, 48 + 50
g.append(text_graph_temperature_min)

# ###################################
# # For simulation only!!
# temperatures = [20, 22]
# humidity = [90, 95]
# x = list(range(0, 50, 1))
# temp_y = [choice(temperatures) for _ in x]
# humidity_y = [choice(humidity) for _ in x]
# ucartesian(plot_1, x, temp_y, rangex = [0, 143], rangey = [0, 40], fill = False, line_color = BLACK)
# ucartesian(plot_2, x, humidity_y, rangex = [0, 143], rangey = [0, 100], fill = False, line_color = BLACK)
# plot_1.append(plot_2)
# g.append(plot_1)
# ###################################

display.show(g)
display.refresh()

# sleep for 180 seconds that is the min time of display refresh
seconds_to_sleep = 180
alarm_to_sleep = alarm.time.TimeAlarm(monotonic_time = time.monotonic() + seconds_to_sleep)
alarm.exit_and_deep_sleep_until_alarms(alarm_to_sleep)
# Does not return. Exits, and restarts after the sleep time.
  
