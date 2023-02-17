import time
import board
import displayio
import busio
import adafruit_ssd1681
import adafruit_ahtx0
from adafruit_display_text import label
import terminalio

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


text_1_group = displayio.Group(x = 4, y = 20, scale = 3)
text_area_1 = label.Label(terminalio.FONT, color = FOREGROUND_COLOR)
text_1_group.append(text_area_1)
g.append(text_1_group)

text_2_group = displayio.Group(x = 4, y = 120, scale = 3)
text_area_2 = label.Label(terminalio.FONT, color = FOREGROUND_COLOR)
text_2_group.append(text_area_2)
g.append(text_2_group)

while True:
  # print()
  # print(temperature_humidity_sensor.temperature)
  # print(temperature_humidity_sensor.relative_humidity)

  temperature = round(temperature_humidity_sensor.temperature, 1)
  text_area_1.text = f'Temperature\n     {temperature} ºC'

  humidity = int(round(temperature_humidity_sensor.relative_humidity, 0))
  text_area_2.text = f'Humidity\n       {humidity} %'

  display.show(g)
  display.refresh()

  time.sleep(180)
