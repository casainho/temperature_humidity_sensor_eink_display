import time
time_start = time.monotonic()

import supervisor
import alarm
import board
import displayio
import busio
import adafruit_ssd1681
from adafruit_display_text import label
import sensor as Sensor
from circuitpython_uplot.uplot import Uplot, color
from circuitpython_uplot.ulogging import ulogging
from main_extra import *

# disable CircuitPython auto-reload
supervisor.runtime.autoreload = False

# NOTE: alarm.sleep_memory array size is 4096 bytes on ESP32-S2, CircuitPyhton 8.0.3
# to keep track of sleep memory we use
sleep_memory_offset = 0

###############################################################
# Let's keep track of number of times we run, by incrementing a counter
#
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

# here we use the first 3 bytes of sleep memory
sleep_memory_offset += 3
###############################################################

###############################################################
# Prepare all the visuals to display
#
g = displayio.Group()

DISPLAY_WIDTH = 200
DISPLAY_HEIGHT = 200
FOREGROUND_COLOR = color.BLACK
BACKGROUND_COLOR = color.WHITE

background_bitmap = displayio.Bitmap(DISPLAY_WIDTH, DISPLAY_HEIGHT, 1)
palette = displayio.Palette(1)
palette[0] = BACKGROUND_COLOR
# create a Tilegrid with the background and put in the displayio group
t = displayio.TileGrid(background_bitmap, pixel_shader=palette)
g.append(t)

# custom fonts
font_small = get_font_small()
font_medium = get_font_medium()
font_big = get_font_big()

# temperature text field
text_temperature = label.Label(font_big, color=FOREGROUND_COLOR, scale=1)
text_temperature.anchored_position = 80, 2
text_temperature.anchor_point = 1.0, 0.0
g.append(text_temperature)

# temperature unity text field
text_temperature_unity = label.Label(font_medium, text='ºC', color=FOREGROUND_COLOR, scale=1)
text_temperature_unity.anchored_position = 81, 6
text_temperature_unity.anchor_point = 0.0, -0.9
g.append(text_temperature_unity)

# humidity text field
text_humidity = label.Label(font_big, color=FOREGROUND_COLOR, scale=1)
text_humidity.anchored_position = 170, 2
text_humidity.anchor_point = 1.0, 0.0
g.append(text_humidity)

# humidity unity text field
text_humidity_unity = label.Label(font_medium, text='%', color=FOREGROUND_COLOR, scale=1)
text_humidity_unity.anchored_position = 171, 6
text_humidity_unity.anchor_point = 0.0, -0.9
g.append(text_humidity_unity)

###############################################################
# initialize the temperature and humidity sensor
# make one read and store the values on the sleep memory
#
sensor = Sensor.Sensor(board.IO37, board.IO35, sleep_memory_offset)
sensor.read_and_store()
###############################################################

# write the temperature value to the text field - also round to have no decimals
text_temperature.text = f'{round_to_int(sensor.temperature)}'
# write the humidty value to the text field - also round to have no decimals
text_humidity.text = f'{round_to_int(sensor.humidity)}'

# get the historic data of the sensors from the sleep memory, so it will be displayed on the display
historic_data_temperature, temperature_max, temperature_min, temperature_len = sensor.historic_data_temperature
historic_data_humidity, humidity_max, humidity_min, humidity_len = sensor.historic_data_humidity

temperature_y_max, temperature_y_min = get_temperature_y_values(temperature_max, temperature_min)
humidity_y_max, humidity_y_min = get_humidity_y_values(humidity_max, humidity_min)

# prepare the uplot objects: first graph for temperature and second for humidity
plot_1 = Uplot(
    21,
    46,
    179,
    63,
    padding=1,
    show_box=True,
    box_color=color.BLACK,
    background_color=color.WHITE,
    scale=1)

plot_2 = Uplot(
    0,
    79,
    179,
    63,
    padding=1,
    show_box=True,
    box_color=color.BLACK,
    background_color=color.WHITE,
    scale=1)

# setting up the uplot tick parameters
plot_1.tick_params(tickx_height=5, ticky_height=5, tickcolor=color.BLACK, tickgrid=False)
plot_2.tick_params(tickx_height=5, ticky_height=5, tickcolor=color.BLACK, tickgrid=False)

# create a list with values for the x axis
x = list(range(0, temperature_len))

# setting up the ulogging optins
ulogging(
  plot_1,
  x,
  historic_data_temperature,
  rangex=[0, 143],
  rangey=[temperature_y_min, temperature_y_max],
  line_color=color.BLACK,
  ticksx=[23, 47, 71, 95, 119, 143],
  ticksy=[get_y_half_scale_value(temperature_y_max, temperature_y_min)],
  fill=True
  )

ulogging(
  plot_2,
  x,
  historic_data_humidity,
  rangex=[0, 143],
  rangey=[humidity_y_min, humidity_y_max],
  line_color=color.BLACK,
  ticksx=[23, 47, 71, 95, 119, 143],
  ticksy=[get_y_half_scale_value(humidity_y_max, humidity_y_min)],
  fill=True 
  )

# get the two plots appended to the display group
plot_1.append(plot_2)
g.append(plot_1)

# temperature y min field
text_graph_temperature_min = label.Label(font_small, text=f'{temperature_y_min}', color=FOREGROUND_COLOR, scale=1)
text_graph_temperature_min.anchor_point = 0.5, 0.0
text_graph_temperature_min.anchored_position = 9, 100
g.append(text_graph_temperature_min)

# temperature y max field
text_graph_temperature_max = label.Label(font_small, text=f'{temperature_y_max}', color=FOREGROUND_COLOR, scale=1)
text_graph_temperature_max.anchor_point = 0.5, 0.0
text_graph_temperature_max.anchored_position = 9, 48
g.append(text_graph_temperature_max)

# humidity y min field
text_graph_humidity_min = label.Label(font_small, text=f'{humidity_y_min}', color=FOREGROUND_COLOR, scale=1)
text_graph_humidity_min.anchor_point = 0.5, 0.0
text_graph_humidity_min.anchored_position = 9, 179
g.append(text_graph_humidity_min)

# humidity y max field
text_graph_humidity_max = label.Label(font_small, text=f'{humidity_y_max}', color=FOREGROUND_COLOR, scale=1)
text_graph_humidity_max.anchor_point = 0.5, 0.0
text_graph_humidity_max.anchored_position = 9, 127
g.append(text_graph_humidity_max)

# temperature x 12h field
text_graph_temperature_x_12h = label.Label(font_small, text='12h', color=FOREGROUND_COLOR, scale=1)
text_graph_temperature_x_12h.anchor_point = 1.0, 1.0
text_graph_temperature_x_12h.anchored_position = 123, 120
g.append(text_graph_temperature_x_12h)

# temperature x 24h field
text_graph_temperature_x_24h = label.Label(font_small, text='24h', color=FOREGROUND_COLOR, scale=1)
text_graph_temperature_x_24h.anchor_point = 1.0, 1.0
text_graph_temperature_x_24h.anchored_position = 198, 120
g.append(text_graph_temperature_x_24h)

# humidity x 12h field
text_graph_humidity_x_12h = label.Label(font_small, text='12h', color=FOREGROUND_COLOR, scale=1)
text_graph_humidity_x_12h.anchor_point = 1.0, 1.0
text_graph_humidity_x_12h.anchored_position = 123, 199
g.append(text_graph_humidity_x_12h)

# humidity x 24h field
text_graph_humidity_x_24h = label.Label(font_small, text='24h', color=FOREGROUND_COLOR, scale=1)
text_graph_humidity_x_24h.anchor_point = 1.0, 1.0
text_graph_humidity_x_24h.anchored_position = 198, 199
g.append(text_graph_humidity_x_24h)

# text counter field
text_counter = label.Label(font_small, text=f'{counter}', color=FOREGROUND_COLOR, scale=1)
text_counter.anchor_point = 0.0, 1.0
text_counter.anchored_position = 4, 199
g.append(text_counter)

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
    baudrate = 60000000) # try to use the higher SPI baudrate / clock, in the hope the display updates are faster and so less power is used by ESP32

display = adafruit_ssd1681.SSD1681(display_bus, width = 200, height = 200, busy_pin = board.IO12, rotation = 0)
###############################################################

# finally, draw the full display
display.show(g)
display.refresh()

# sleep for 600 seconds / 10 minutes
# decrease the time it takes to get here since the start
time_now = time.monotonic()
seconds_to_sleep = time_now + (600 - (time_now - time_start))
alarm_to_sleep = alarm.time.TimeAlarm(monotonic_time = seconds_to_sleep)
alarm.exit_and_deep_sleep_until_alarms(alarm_to_sleep)
# does not return. Exits, and restarts after the sleep time.
