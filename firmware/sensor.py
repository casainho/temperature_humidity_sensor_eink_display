import time
import board
import busio
import adafruit_ahtx0
import alarm

# we want 144 values, of of every sensor read at every 10 minutes, that will be 24h: 144 --> 24h * (60 / 10)
historic_temperature_simulated = [round(value / 3, 1) for value in range(0, 144, 1)]
historic_humidity_simulated = [round(value / 2, 1) for value in range(5, 149, 1)]

# ##################################################
# # Let's keep track of number of times we run, by incrementing a counter

# if not alarm.wake_alarm:
#   # reset counter at a power on reset
#   counter = 0
# else:
#   # get the counter
#   counter = (alarm.sleep_memory[0] << 24) + (alarm.sleep_memory[1] << 16) + (alarm.sleep_memory[2] << 8) + alarm.sleep_memory[3]
   
# # let's increase the counter
# counter += 1

# # store the counter
# alarm.sleep_memory[0] = (counter >> 24 & 0xff)
# alarm.sleep_memory[1] = (counter >> 16 & 0xff)
# alarm.sleep_memory[2] = (counter >> 8 & 0xff)
# alarm.sleep_memory[3] = (counter & 0xff)
# ##################################################

class Sensor(object):
  def __init__(self, i2c_clk_pin, i2c_sda_pin):
    i2c = busio.I2C(i2c_clk_pin, i2c_sda_pin)
    self.temperature_humidity_sensor = adafruit_ahtx0.AHTx0(i2c)
    self.last_temperature = 0
    self.last_humidity = 0

  def run_periodic(self):
    "Must be called ever 5 minutes: will read and store the sensor data"
    self.last_temperature = round(self.temperature_humidity_sensor.temperature, 1)
    self.last_humidity = round(self.temperature_humidity_sensor.relative_humidity, 1)

  @property
  def temperature(self):
    return self.last_temperature
  
  @property
  def humidity(self):
    return self.last_humidity

  @property
  def historic_data_temperature(self):
    "Return an array of data"
    return []

  @property
  def historic_data_humidity(self):
    "Return an array of data"
    return []

  @property
  def historic_data_temperature_simulated(self):
    "Return an array of simulated data"
    return historic_temperature_simulated

  @property
  def historic_data_humidity_simulated(self):
    "Return an array of simulated data"
    return historic_humidity_simulated