import unittest
import sys
sys.path.append('../')
from sensor import *

class MemoryForSensorDataTests(unittest.TestCase):
  def test_MemoryForSensorData_object(self):
    memory_sensor_data = MemoryForSensorData(0, 144*2)
    self.assertEqual(memory_sensor_data._memory, 0)
    self.assertEqual(memory_sensor_data._offset_address_initial, 0)
    self.assertEqual(memory_sensor_data._capacity_x2, 144*2)
    self.assertEqual(memory_sensor_data._current_size, 0)
    self.assertEqual(memory_sensor_data._head_x2, 0)
    self.assertEqual(memory_sensor_data._tail_x2, 0)
    self.assertEqual(memory_sensor_data._offset_address, 6)
    self.assertEqual(memory_sensor_data._max_value, None)
    self.assertEqual(memory_sensor_data._min_value, None)

  def test_MemoryForSensorData_object_sensor_memory_offset(self):
    memory_sensor_data = MemoryForSensorData(0, 144*2)
    self.assertEqual(memory_sensor_data.sensor_memory_offset, (144*2) + 6)

  def test_MemoryForSensorData_object_add_1(self):
    # testing adding 3 values
    memory_sensor_data = MemoryForSensorData(0, 144*2)
    memory = bytearray((144*2) + 6)
    memory_sensor_data._memory = memory
    memory_sensor_data.add(5)
    memory_sensor_data.add(7)
    memory_sensor_data.add(9)
    self.assertEqual(memory_sensor_data._head_x2, 0)
    self.assertEqual(memory_sensor_data._tail_x2, 6)
    self.assertEqual(memory_sensor_data._current_size, 3)
    self.assertEqual(memory[6], 0)
    self.assertEqual(memory[7], 5)
    self.assertEqual(memory[8], 0)
    self.assertEqual(memory[9], 7)
    self.assertEqual(memory[10], 0)
    self.assertEqual(memory[11], 9)

  def test_MemoryForSensorData_object_add_2(self):
    # testing adding 216 values (216 values equal to 24h + 12h)
    memory_sensor_data = MemoryForSensorData(0, 144*2)
    memory = bytearray((144*2) + 6)
    memory_sensor_data._memory = memory
    for x in range(216):
      memory_sensor_data.add(x)

    self.assertEqual(memory_sensor_data._head_x2, 144)
    self.assertEqual(memory_sensor_data._tail_x2, 144)
    self.assertEqual(memory_sensor_data._current_size, 144)
    self.assertEqual(memory[6], 0x00)
    self.assertEqual(memory[7], 0x90)
    self.assertEqual(memory[8], 0x00)
    self.assertEqual(memory[9], 0x91)
    self.assertEqual(memory[10], 0x00)
    self.assertEqual(memory[11], 0x92)
    self.assertEqual(memory[100], 0x00)
    self.assertEqual(memory[101], 0xBF)

    list_values_to_check = list([x / 10 for x in range(144, 216)])
    list_values_to_check += list([x / 10 for x in range(72, 144)])
    self.assertEqual(memory_sensor_data.values, list_values_to_check)
    self.assertEqual(memory_sensor_data.len, 144)
    self.assertEqual(memory_sensor_data._max_value, 21.5)
    self.assertEqual(memory_sensor_data.min, 7.2)

class SensorTests(unittest.TestCase):
  def test_SensorTests_object(self):
    sensor = Sensor(None, None, 0)
    self.assertEqual(sensor._temperature_humidity_sensor, 0)
    self.assertEqual(sensor._data_sensor_temperature.sensor_memory_offset, 294)
    self.assertEqual(sensor._data_sensor_humidity.sensor_memory_offset, 294 * 2)
    self.assertEqual(sensor._data_sensor_temperature.values, [])
    self.assertEqual(sensor._data_sensor_humidity.values, [])