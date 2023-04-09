import busio

try:
  import adafruit_ahtx0
  import alarm
  testing = False
except Exception:
  print("sensor.py: Assuming we are running the unit tests")
  testing = True

class MemoryForSensorData():
  def __init__(self, offset_address, capacity_x2):
    
    if not testing:
      self._memory = alarm.sleep_memory # from now own, use self.memory instead of alarm.sleep_memory
    else:
      self._memory = 0

    self._offset_address_initial = self._offset_address = offset_address
    self._capacity_x2 = capacity_x2

    # initial state of this variables
    self._current_size = 0
    self._head_x2 = 0
    self._tail_x2 = 0

    if not testing and alarm.wake_alarm:
      # recover the values from the sleep memory
      self._current_size = (self._memory[self._offset_address] << 8) + self._memory[self._offset_address + 1]
      self._head_x2 = (self._memory[self._offset_address + 2] << 8) + self._memory[self._offset_address + 3]
      self._tail_x2 = (self._memory[self._offset_address + 4] << 8) + self._memory[self._offset_address + 5]

    self._offset_address += 6 # we use 6 bytes
    self._max_value = None
    self._min_value = None

  @property
  def sensor_memory_offset(self):
    "Returns the total number of bytes used"
    return self._offset_address + self._capacity_x2
  
  def add(self, value):  
    # move head forward
    if self._tail_x2 == self._head_x2 and (self._current_size * 2) == self._capacity_x2:
      self._head_x2 = (self._head_x2 + 2) % self._capacity_x2

    # add the data
    self._memory[self._offset_address + self._tail_x2] = (value >> 8) & 0xff
    self._memory[self._offset_address + self._tail_x2 + 1] = value & 0xff

    # move tail forward (in step of 2)
    self._tail_x2 = (self._tail_x2 + 2) % self._capacity_x2

    # increase the current_size (only when ring buffer is not yet full)
    if (self._current_size * 2) < self._capacity_x2:
      self._current_size += 1

    # update the values on sleep memory
    self._memory[self._offset_address_initial] = (self._current_size >> 8) & 0xff
    self._memory[self._offset_address_initial + 1] = self._current_size & 0xff

    self._memory[self._offset_address_initial + 2] = (self._head_x2 >> 8) & 0xff
    self._memory[self._offset_address_initial + 3] = self._head_x2 & 0xff

    self._memory[self._offset_address_initial + 4] = (self._tail_x2 >> 8) & 0xff
    self._memory[self._offset_address_initial + 5] = self._tail_x2 & 0xff

  @property
  def values(self):
    # check if ring buffer is empty
    if self._current_size < 1:
      return []
    
    data = list([0] * self._current_size)
    head_x2 = 0
  
    for i in range(len(data)):
      # get the element value
      # note that it must be dived by 10 as values are stored as ints 
      data[i] = ((self._memory[self._offset_address + head_x2] << 8) + (self._memory[self._offset_address + head_x2 + 1] & 0xff)) / 10

      # init max and min values
      if self._max_value is None:
        self._max_value = data[i]
        self._min_value = data[i]

      # update max_value
      if data[i] > self._max_value:
        self._max_value = data[i]

      # update min_value
      if data[i] < self._min_value:
        self._min_value = data[i]

      # move head forward
      head_x2 = (head_x2 + 2) % (self._capacity_x2 * 2)

    return data
  
  @property
  def len(self):
    return self._current_size
  
  @property
  def max(self):
    return self._max_value
  
  @property
  def min(self):
    return self._min_value

class Sensor(object):
  def __init__(self, i2c_clk_pin, i2c_sda_pin, sleep_memory_offset):
    
    if not testing:
      i2c = busio.I2C(i2c_clk_pin, i2c_sda_pin)
      self._temperature_humidity_sensor = adafruit_ahtx0.AHTx0(i2c)
    else:
      self._temperature_humidity_sensor = 0
      
    self._last_temperature = 0
    self._last_humidity = 0
    self._data_sensor_temperature = MemoryForSensorData(sleep_memory_offset, 288) # 144 points, 2 bytes for each point = 288
    sleep_memory_offset = self._data_sensor_temperature.sensor_memory_offset # this is the updated sleep memory offset
    self._data_sensor_humidity = MemoryForSensorData(sleep_memory_offset, 288)

  def read_and_store(self):
    "Must be called to read the sensor data. Will store the sensor data in the sleep memory"

    # read the sensor values and round the values
    self._last_temperature = round(self._temperature_humidity_sensor.temperature, 1)
    self._last_humidity = round(self._temperature_humidity_sensor.relative_humidity, 1)

    # store the sensor values on sleep memory (must be integers)
    self._data_sensor_temperature.add(int(self._last_temperature * 10))
    self._data_sensor_humidity.add(int(self._last_humidity * 10))

  @property
  def temperature(self):
    return self._last_temperature
  
  @property
  def humidity(self):
    return self._last_humidity

  @property
  def historic_data_temperature(self):
    "Return a list with temperature values, max, min and lenght"
    return self._data_sensor_temperature.values, \
      self._data_sensor_temperature.max, \
      self._data_sensor_temperature.min, \
      self._data_sensor_temperature.len

  @property
  def historic_data_humidity(self):
    "Return a list with humidity values, max, min and lenght"
    return self._data_sensor_humidity.values, \
      self._data_sensor_humidity.max, \
      self._data_sensor_humidity.min, \
      self._data_sensor_humidity.len
  