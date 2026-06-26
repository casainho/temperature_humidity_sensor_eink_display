import time
import machine
import ubinascii
from machine import Pin, SPI

# ---------------------------------------------------------------------------
# Pin assignments for ESP32-S2 mini — adjust to match your board wiring
# ---------------------------------------------------------------------------
I2C_SCL  = 37   # sensor SCL
I2C_SDA  = 35   # sensor SDA

SPI_CLK   = 5   # SSD1681 CLK
SPI_MOSI  = 3   # SSD1681 MOSI (SDI)
EINK_CS   = 7   # SSD1681 chip select
EINK_DC   = 9   # SSD1681 data/command
EINK_RST  = 11  # SSD1681 reset
EINK_BUSY = 12  # SSD1681 busy (input)

# ---------------------------------------------------------------------------
# Imports (sensor module initialises RTC memory on import)
# ---------------------------------------------------------------------------
from sensor import _mem, _is_deepsleep_wake, _SENSOR_MEM_OFFSET, Sensor
from scale import (
    round_to_int,
    get_co2_y_values, get_temperature_y_values,
    get_y_half_scale_value,
)
from draw import draw_text, text_width, draw_graph, BLACK, WHITE
from fonts import robotobold40 as font_top     # top-row values (height 40 px)
from fonts import robotobold18 as font_medium  # units / graph labels (height 18 px)
from fonts import robotobold12 as font_small   # graph labels (height 11 px)
from ssd1681 import SSD1681

_t_start = time.ticks_ms()
SENSOR_SETTLE_MS = 500
DISPLAY_SETTLE_MS = 1000
REFRESH_INTERVAL_MS = 20_000
DEBUG_DUMP_FRAMEBUFFER = True
DUMP_CHUNK_SIZE = 64
WARMUP_READS = 4
GRAPH_STORE_EVERY = 8  # store 1 graph point every 8 cycles (8 × 20 s = 160 s → 180 pts = 8 h)

# ---------------------------------------------------------------------------
# Wake counter (bytes 0-2 of shared RTC memory)
# ---------------------------------------------------------------------------
if _is_deepsleep_wake():
    counter = (_mem[0] << 16) | (_mem[1] << 8) | _mem[2]
else:
    counter = 0
counter += 1
_mem[0] = (counter >> 16) & 0xFF
_mem[1] = (counter >> 8) & 0xFF
_mem[2] = counter & 0xFF

# ---------------------------------------------------------------------------
# Sensor and display objects are reused across refreshes.
sensor = Sensor(I2C_SCL, I2C_SDA, _SENSOR_MEM_OFFSET, i2c_bus=1)

# ---------------------------------------------------------------------------
# Derived layout positions based on actual font heights
# ---------------------------------------------------------------------------
TOP_H = font_top.height()      # 40 px
MED_H = font_medium.height()   # 18 px
SM_H  = font_small.height()    # 11 px

TOP_Y     = 0                         # top value row
TOP_GY    = 46                        # CO2 graph top
TOP_GH    = 63                        # CO2 graph height
BOT_GY    = 123                       # temperature graph top
BOT_GH    = 63                        # temperature graph height
GX        = 27                        # graph left edge (space for y-axis labels)
GW        = 173                       # graph width including box
X12H      = GX + GW // 2              # true midpoint of the graph x-axis
X24H      = 198                       # original-style right edge label position
X_STEPS   = 179                       # fixed x-axis slots for 180 stored points
BOTTOM    = 199                       # bottom text row
Y_LABEL_X  = GX - 2                   # right edge for y-axis labels


def _draw_y_label(fb, value, y):
    text = str(value)
    draw_text(fb, font_small, text, Y_LABEL_X - text_width(font_small, text), y)


def _x_label_for_zero_center(font, text, center_x):
    zero_center = text_width(font, text[0]) + text_width(font, text[1]) // 2
    return center_x - zero_center


def _draw_screen(fb, co2, temp, humid, co2_data, co2_y_min, co2_y_max,
                 temp_data, temp_y_min, temp_y_max, counter_value):
    fb.fill(WHITE)

    # Top row: CO2, temperature, humidity
    co2_str = str(min(round_to_int(co2), 9999))
    temp_str = str(min(round_to_int(temp), 99))
    humid_str = str(min(round_to_int(humid), 99))
    # Compute each group width and distribute two equal gaps between the three groups.
    UNIT_GAP = 2
    w_co2   = text_width(font_top, co2_str)
    w_temp  = text_width(font_top, temp_str)
    w_humid = text_width(font_top, humid_str)
    temp_unit = 'C'
    ppm_unit_w = max(
        text_width(font_small, 'pp'),
        text_width(font_small, 'm'),
    )
    w_co2_group   = w_co2   + UNIT_GAP + ppm_unit_w
    w_temp_group  = w_temp  + UNIT_GAP + text_width(font_small, temp_unit)
    w_humid_group = w_humid + UNIT_GAP + text_width(font_small, '%')
    gap = max(0, (200 - w_co2_group - w_temp_group - w_humid_group) // 2)

    co2_x   = 0
    temp_x  = w_co2_group + gap
    humid_x = temp_x + w_temp_group + gap
    unit_y  = TOP_Y + TOP_H - SM_H - 4
    temp_unit_y = unit_y - 4

    draw_text(fb, font_top, co2_str, co2_x, TOP_Y)
    ppm_x = co2_x + w_co2 + UNIT_GAP
    draw_text(fb, font_small, 'pp', ppm_x, temp_unit_y - (SM_H + 1))
    draw_text(fb, font_small, 'm', ppm_x, temp_unit_y)

    draw_text(fb, font_top, temp_str, temp_x, TOP_Y)
    draw_text(fb, font_small, temp_unit, temp_x + w_temp + UNIT_GAP, temp_unit_y)

    draw_text(fb, font_top, humid_str, humid_x, TOP_Y)
    draw_text(fb, font_small, '%', humid_x + w_humid + UNIT_GAP, temp_unit_y)

    # First graph: CO2
    co2_y_mid = get_y_half_scale_value(co2_y_max, co2_y_min)
    _draw_y_label(fb, co2_y_max, TOP_GY)
    _draw_y_label(fb, co2_y_mid, TOP_GY + TOP_GH // 2 - SM_H // 2)
    _draw_y_label(fb, co2_y_min, TOP_GY + TOP_GH - SM_H)
    draw_graph(fb, GX, TOP_GY, GW, TOP_GH, co2_data, co2_y_min, co2_y_max, x_steps=X_STEPS)
    draw_text(fb, font_small, '4h', _x_label_for_zero_center(font_small, '4h', X12H), TOP_GY + TOP_GH + 2)
    draw_text(fb, font_small, '8h', X24H - text_width(font_small, '8h'), TOP_GY + TOP_GH + 2)

    # Second graph: temperature
    temp_y_mid = get_y_half_scale_value(temp_y_max, temp_y_min)
    _draw_y_label(fb, temp_y_max, BOT_GY)
    _draw_y_label(fb, temp_y_mid, BOT_GY + BOT_GH // 2 - SM_H // 2)
    _draw_y_label(fb, temp_y_min, BOT_GY + BOT_GH - SM_H)
    draw_graph(fb, GX, BOT_GY, GW, BOT_GH, temp_data, temp_y_min, temp_y_max, x_steps=X_STEPS)
    draw_text(fb, font_small, '4h', _x_label_for_zero_center(font_small, '4h', X12H), BOT_GY + BOT_GH + 2)
    draw_text(fb, font_small, '8h', X24H - text_width(font_small, '8h'), BOT_GY + BOT_GH + 2)

    # Bottom-left cycle counter
    draw_text(fb, font_small, str(counter_value), 0, BOTTOM)


def _dump_framebuffer(display_obj, counter_value):
    if not DEBUG_DUMP_FRAMEBUFFER:
        return

    buf = display_obj._buf
    print('FB_BEGIN counter={} len={}'.format(counter_value, len(buf)))
    for offset in range(0, len(buf), DUMP_CHUNK_SIZE):
        chunk = buf[offset:offset + DUMP_CHUNK_SIZE]
        print('{:04x}: {}'.format(offset, ubinascii.hexlify(chunk).decode()))
    print('FB_END counter={}'.format(counter_value))


# ---------------------------------------------------------------------------
# Initialise display
# ---------------------------------------------------------------------------
time.sleep_ms(DISPLAY_SETTLE_MS)
spi = SPI(1,
          baudrate=20_000_000,
          polarity=0, phase=0,
          sck=Pin(SPI_CLK),
          mosi=Pin(SPI_MOSI),
          miso=None)

display = SSD1681(
    spi,
    cs=Pin(EINK_CS, Pin.OUT),
    dc=Pin(EINK_DC, Pin.OUT),
    rst=Pin(EINK_RST, Pin.OUT),
    busy=Pin(EINK_BUSY, Pin.IN),
)

_CAL_FLAG = '/cal_flag'

def _cal_flag_value():
    try:
        with open(_CAL_FLAG) as f:
            return int(f.read().strip())
    except Exception:
        return 1

def _set_cal_flag(value):
    with open(_CAL_FLAG, 'w') as f:
        f.write(str(value))

if _cal_flag_value() == 0:
    sensor.calibrate_co2()
    _set_cal_flag(1)
    display.fb.fill(WHITE)
    msg = 'CO2 calibrated'
    draw_text(display.fb, font_medium, msg,
              max(0, (200 - text_width(font_medium, msg)) // 2), 91)
    display.show()
    time.sleep_ms(20_000)

sample_count = 0
while True:
    cycle_start = time.ticks_ms()

    counter += 1
    _mem[0] = (counter >> 16) & 0xFF
    _mem[1] = (counter >> 8) & 0xFF
    _mem[2] = counter & 0xFF

    if sample_count < WARMUP_READS or (sample_count % GRAPH_STORE_EVERY) != 0:
        sensor.read()
    else:
        sensor.read_and_store()
    sample_count += 1
    time.sleep_ms(SENSOR_SETTLE_MS)

    co2   = sensor.co2
    temp  = sensor.temperature
    humid = sensor.humidity

    co2_data,   co2_max,   co2_min,   _ = sensor.historic_data_co2
    temp_data,  temp_max,  temp_min,  _ = sensor.historic_data_temperature

    co2_y_max,  co2_y_min  = get_co2_y_values(co2_max or co2, co2_min or co2)
    temp_y_max, temp_y_min = get_temperature_y_values(temp_max or temp, temp_min or temp)

    _draw_screen(display.fb, co2, temp, humid, co2_data, co2_y_min, co2_y_max,
                 temp_data, temp_y_min, temp_y_max, counter)

    display.show()
    _dump_framebuffer(display, counter)

    elapsed_ms = time.ticks_diff(time.ticks_ms(), cycle_start)
    time.sleep_ms(max(0, REFRESH_INTERVAL_MS - elapsed_ms))

