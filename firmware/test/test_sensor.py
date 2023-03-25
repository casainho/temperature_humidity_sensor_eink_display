import unittest
import sys
sys.path.append('../')
from sensor import *

class SensorTests(unittest.TestCase):
  def test_MemoryForSensorData_object(self):
    memory_sensor_data = MemoryForSensorData(0, 144*2)
    self.assertEqual(memory_sensor_data.memory, 0)
    self.assertEqual(memory_sensor_data.offset_address_initial, 0)
    self.assertEqual(memory_sensor_data.capacity_x2, 144*2)
    self.assertEqual(memory_sensor_data.current_size, 0)
    self.assertEqual(memory_sensor_data.head_x2, 0)
    self.assertEqual(memory_sensor_data.tail_x2, 0)
    self.assertEqual(memory_sensor_data.offset_address, 6)
    self.assertEqual(memory_sensor_data.max_value, None)
    self.assertEqual(memory_sensor_data.min_value, None)

  def test_MemoryForSensorData_object_sensor_memory_offset(self):
    memory_sensor_data = MemoryForSensorData(0, 144*2)
    self.assertEqual(memory_sensor_data.sensor_memory_offset, (144*2) + 6)

  def test_MemoryForSensorData_object_add(self):
    # testing adding 3 values
    memory_sensor_data = MemoryForSensorData(0, 144*2)
    memory = bytearray((144*2) + 6)
    memory_sensor_data.memory = memory
    memory_sensor_data.add(5)
    memory_sensor_data.add(7)
    memory_sensor_data.add(9)
    self.assertEqual(memory_sensor_data.head_x2, 0)
    self.assertEqual(memory_sensor_data.tail_x2, 6)
    self.assertEqual(memory_sensor_data.current_size, 3)
    self.assertEqual(memory[6], 0)
    self.assertEqual(memory[7], 5)
    self.assertEqual(memory[8], 0)
    self.assertEqual(memory[9], 7)
    self.assertEqual(memory[10], 0)
    self.assertEqual(memory[11], 9)
    del(memory)
    del(memory_sensor_data)

    # testing adding 216 values (216 values equal to 24h + 12h)
    memory_sensor_data = MemoryForSensorData(0, 144*2)
    memory = bytearray((144*2) + 6)
    memory_sensor_data.memory = memory
    for x in range(216):
      memory_sensor_data.add(x)

    self.assertEqual(memory_sensor_data.head_x2, 144)
    self.assertEqual(memory_sensor_data.tail_x2, 144)
    self.assertEqual(memory_sensor_data.current_size, 144)
    self.assertEqual(memory[6], 0x00)
    self.assertEqual(memory[7], 0x90)
    self.assertEqual(memory[8], 0x00)
    self.assertEqual(memory[9], 0x91)
    self.assertEqual(memory[10], 0x00)
    self.assertEqual(memory[11], 0x92)
    self.assertEqual(memory[11], 0x92)

    sensor_values = memory_sensor_data.values
    sensor_values.sort() # sort in ascending order
    list_values_to_check = list([x / 10 for x in range(72, 216)])
    self.assertEqual(sensor_values, list_values_to_check)

    self.assertEqual(memory_sensor_data.len, 144)
    self.assertEqual(memory_sensor_data.max_value, 21.5)
    self.assertEqual(memory_sensor_data.min, 7.2)