import time
import board
import displayio
import busio
import adafruit_ssd1681
import adafruit_ahtx0
from adafruit_display_text import label
import terminalio
import wifi

##################################################
# Try to save power
wifi.radio.enabled = False # This disables at least the web workflow, tested on CircuitPyhton 8.0.3
##################################################

i2c = busio.I2C(
    board.IO37, # SCLK pin
    board.IO35) # SDA pin)

temperature_humidity_sensor = adafruit_ahtx0.AHTx0(i2c)

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
    baudrate = 1000000)

display = adafruit_ssd1681.SSD1681(display_bus, width = 200, height = 200, busy_pin = board.IO12, rotation = 0)
time.sleep(1)

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


text_area_1 = label.Label(terminalio.FONT, text="Temperature", color=FOREGROUND_COLOR, scale=3)
text_area_1.anchor_point = 0.0, 0.0
text_area_1.anchored_position = 4, 20

text_temp = label.Label(terminalio.FONT, color=FOREGROUND_COLOR, scale=3)
text_temp.anchor_point = 1.0, 0.0
text_temp.anchored_position = DISPLAY_WIDTH, 60

g.append(text_area_1)
g.append(text_temp)

text_area_2 = label.Label(terminalio.FONT, text="Humidity", color=FOREGROUND_COLOR, scale=3)
text_area_2.anchor_point = 0.0, 0.0
text_area_2.anchored_position = 4, 120

text_humidity = label.Label(terminalio.FONT, color=FOREGROUND_COLOR, scale=3)
text_humidity.anchor_point = 1.0, 0.0
text_humidity.anchored_position = DISPLAY_WIDTH, 160

g.append(text_area_2)
g.append(text_humidity)

while True:
  # print()
  # print(temperature_humidity_sensor.temperature)
  # print(temperature_humidity_sensor.relative_humidity)

  temperature = round(temperature_humidity_sensor.temperature, 1)
  text_temp.text = f'{temperature} ºC'

  humidity = int(round(temperature_humidity_sensor.relative_humidity, 0))
  text_humidity.text = f'{humidity} %'

  display.show(g)
  display.refresh()

  time.sleep(180)
