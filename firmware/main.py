import time
import board
import displayio
import busio
import adafruit_ssd1681
import adafruit_ahtx0
from adafruit_display_text import label
import terminalio
import wifi
import alarm

##################################################
# Try to save power
wifi.radio.enabled = False # This disables at least the web workflow, tested on CircuitPyhton 8.0.3
##################################################

##################################################
# Let's keep track of number of times we run, by incrementing a counter

if not alarm.wake_alarm:
  # reset counter at a power on reset
  counter = 0
else:
  # get the counter
  counter = (alarm.sleep_memory[0] << 24) + (alarm.sleep_memory[1] << 16) + (alarm.sleep_memory[2] << 8) + alarm.sleep_memory[3]
   
# let's increase the counter
counter += 1

# store the counter
alarm.sleep_memory[0] = (counter >> 24 & 0xff)
alarm.sleep_memory[1] = (counter >> 16 & 0xff)
alarm.sleep_memory[2] = (counter >> 8 & 0xff)
alarm.sleep_memory[3] = (counter & 0xff)
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
text_area_1.anchored_position = 4, 0

text_temp = label.Label(terminalio.FONT, color=FOREGROUND_COLOR, scale=3)
text_temp.anchor_point = 1.0, 0.0
text_temp.anchored_position = DISPLAY_WIDTH, 40

g.append(text_area_1)
g.append(text_temp)

text_area_2 = label.Label(terminalio.FONT, text="Humidity", color=FOREGROUND_COLOR, scale=3)
text_area_2.anchor_point = 0.0, 0.0
text_area_2.anchored_position = 4, 90

text_humidity = label.Label(terminalio.FONT, color=FOREGROUND_COLOR, scale=3)
text_humidity.anchor_point = 1.0, 0.0
text_humidity.anchored_position = DISPLAY_WIDTH, 135

g.append(text_area_2)
g.append(text_humidity)

text_counter = label.Label(terminalio.FONT, color=FOREGROUND_COLOR, scale = 2)
text_counter.anchor_point = 0.0, 0.0
text_counter.anchored_position = 0, 180
g.append(text_counter)

while True:
  # print()
  # print(temperature_humidity_sensor.temperature)
  # print(temperature_humidity_sensor.relative_humidity)

  temperature = round(temperature_humidity_sensor.temperature, 1)
  text_temp.text = f'{temperature} ºC'

  humidity = int(round(temperature_humidity_sensor.relative_humidity, 0))
  text_humidity.text = f'{humidity} %'

  text_counter.text = f'{counter}'

  display.show(g)
  display.refresh()

  # sleep for 180 seconds that is the min time of display refresh
  seconds_to_sleep = 180 + 10
  alarm_to_sleep = alarm.time.TimeAlarm(monotonic_time = time.monotonic() + seconds_to_sleep)
  alarm.exit_and_deep_sleep_until_alarms(alarm_to_sleep)
  # Does not return. Exits, and restarts after the sleep time.
  
