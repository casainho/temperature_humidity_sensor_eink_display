import time
import board
import busio
import adafruit_ahtx0
import alarm

class MemoryForSensorData():
  def __init__(self, offset_address, capacity):
    self.memory = alarm.sleep_memory # from now own, use self.memory instead of alarm.sleep_memory
    self.offset_address_initial = self.offset_address = offset_address
    self.capacity = capacity

    if alarm.wake_alarm:
      # recover the values from the sleep memory
      self.current_size = (self.memory[self.offset_address] << 8) + self.memory[self.offset_address + 1]
      self.offset_address += 2

      self.head_x2 = (self.memory[self.offset_address] << 8) + self.memory[self.offset_address + 1]
      self.offset_address += 2

      self.tail_x2 = (self.memory[self.offset_address] << 8) + self.memory[self.offset_address + 1]
      self.offset_address += 2
    else:
      # initial state of this variables
      self.current_size = 0
      self.head_x2 = 0
      self.tail_x2 = 0
      self.offset_address += 6

    self._update_variables()

  def _update_variables(self):
    # update the values on sleep memory
    self.memory[self.offset_address_initial] = (self.current_size >> 8) & 0xff
    self.memory[self.offset_address_initial + 1] = self.current_size & 0xff

    self.memory[self.offset_address_initial + 2] = (self.head_x2 >> 8) & 0xff
    self.memory[self.offset_address_initial + 3] = self.head_x2 & 0xff

    self.memory[self.offset_address_initial + 4] = (self.tail_x2 >> 8) & 0xff
    self.memory[self.offset_address_initial + 5] = self.tail_x2 & 0xff

  @property
  def sensor_memory_offset(self):
    "Returns the total number of bytes used"
    return self.offset_address + (self.capacity * 2)
  
  def add(self, value):
    if not isinstance(value, int):
      raise TypeError("value must be a int")
  
    # move head forward
    if self.tail_x2 == self.head_x2 and self.current_size == self.capacity:
      self.head_x2 = (self.head_x2 + 2) % (self.capacity * 2)

    # add the data
    self.memory[self.offset_address + self.tail_x2] = (value >> 8) & 0xff
    self.memory[self.offset_address + self.tail_x2 + 1] = value & 0xff

    # move tail forward (in step of 2)
    self.tail_x2 = (self.tail_x2 + 2) % (self.capacity * 2)

    # increase the current_size (only when ring buffer is not yet full)
    if self.current_size < self.capacity:
      self.current_size += 1

    self._update_variables()

  @property
  def values(self):
    # check if ring buffer is empty
    if self.current_size < 1:
      return []
    
    data = list([0] * self.capacity)
    head_x2 = self.head_x2

    for i in range(self.capacity):
      # get the element value
      # note that it must be dived by 10 as values are stored as ints
      data[i] = ((self.memory[self.offset_address + head_x2] << 8) + (self.memory[self.offset_address + head_x2 + 1] & 0xff)) / 10

      # move head forward
      head_x2 = (head_x2 + 2) % (self.capacity * 2)

    return data    

class Sensor(object):
  def __init__(self, i2c_clk_pin, i2c_sda_pin):
    i2c = busio.I2C(i2c_clk_pin, i2c_sda_pin)
    self.temperature_humidity_sensor = adafruit_ahtx0.AHTx0(i2c)
    self.last_temperature = 0
    self.last_humidity = 0
    self.data_sensor_temperature = MemoryForSensorData(0, 144)
    new_offset = self.data_sensor_temperature.sensor_memory_offset # this is the memory offset (memory used by previous MemoryForSensorData())
    self.data_sensor_humidity = MemoryForSensorData(new_offset, 144) 
    
    # # we want 144 values, of of every sensor read at every 10 minutes, that will be 24h: 144 --> 24h * (60 / 10)
    # self.historic_temperature_simulated = [round(value / 3, 1) for value in range(0, 144, 1)]
    # self.historic_humidity_simulated = [round(value / 2, 1) for value in range(5, 149, 1)]

  def run_periodic(self):
    "Must be called every 5 minutes: will read and store the sensor data"

    # read the sensor values
    self.last_temperature = round(self.temperature_humidity_sensor.temperature, 1)
    self.last_humidity = round(self.temperature_humidity_sensor.relative_humidity, 1)

    # store the sensor values on sleep memory (must be integers)
    self.data_sensor_temperature.add(int(self.last_temperature * 10))
    self.data_sensor_humidity.add(int(self.last_humidity * 10))

  @property
  def temperature(self):
    return self.last_temperature
  
  @property
  def humidity(self):
    return self.last_humidity

  @property
  def historic_data_temperature(self):
    "Return an array of data"
    return self.data_sensor_temperature.values

  @property
  def historic_data_humidity(self):
    "Return an array of data"
    return self.data_sensor_humidity.values

  # @property
  # def historic_data_temperature_simulated(self):
  #   "Return an array of simulated data"
  #   return self.historic_temperature_simulated

  # @property
  # def historic_data_humidity_simulated(self):
  #   "Return an array of simulated data"
  #   return self.historic_humidity_simulated