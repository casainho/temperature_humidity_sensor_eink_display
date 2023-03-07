import time
import board
import displayio
import busio
import adafruit_ssd1681
from adafruit_display_text import label
import terminalio
import alarm
import supervisor
import sensor
from ulab import numpy as np
from circuitpython_uplot.uplot import Uplot
from circuitpython_uplot.ucartesian import ucartesian

_sensor = sensor.Sensor(board.IO37, board.IO35)

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

_sensor.run_periodic()
text_temperature.text = f'{_sensor.temperature}'
text_humidity.text = f'{int(round(_sensor.humidity, 0))}%'

# text_counter = label.Label(terminalio.FONT, color=FOREGROUND_COLOR, scale = 2)
# text_counter.anchor_point = 0.0, 0.0
# text_counter.anchored_position = 0, 180
# g.append(text_counter)

plot_1 = Uplot(
    20,
    50,
    200,
    70,
    padding = 1,
    show_box = True,
    background_color = WHITE)

plot_2 = Uplot(
    0,
    80,
    200,
    70,
    padding = 1,
    show_box = True,
    background_color = WHITE)

# Setting up tick parameters
plot_1.tick_params(tickheight = 10, tickcolor = BLACK, tickgrid = False)
plot_2.tick_params(tickheight = 10, tickcolor = BLACK, tickgrid = False)

x = list(range(0, 144, 1))
ucartesian(plot_1, x, _sensor.historic_data_temperature_simulated, fill = True, line_color = BLACK)
ucartesian(plot_2, x, _sensor.historic_data_humidity_simulated, fill = True, line_color = BLACK)
plot_1.append(plot_2)
g.append(plot_1)

display.show(g)
display.refresh()

# sleep for 180 seconds that is the min time of display refresh
seconds_to_sleep = 180 + 10
alarm_to_sleep = alarm.time.TimeAlarm(monotonic_time = time.monotonic() + seconds_to_sleep)
alarm.exit_and_deep_sleep_until_alarms(alarm_to_sleep)
# Does not return. Exits, and restarts after the sleep time.
  
