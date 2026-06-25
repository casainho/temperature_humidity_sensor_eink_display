import unittest
import sys
sys.path.append('../')
from sensor import MemoryForSensorData, Sensor


class MemoryForSensorDataTests(unittest.TestCase):

    def test_object_init(self):
        msd = MemoryForSensorData(0, 144 * 2)
        self.assertEqual(msd._offset_address_initial, 0)
        self.assertEqual(msd._capacity_x2, 144 * 2)
        self.assertEqual(msd._current_size, 0)
        self.assertEqual(msd._head_x2, 0)
        self.assertEqual(msd._tail_x2, 0)
        self.assertEqual(msd._offset_address, 6)
        self.assertIsNone(msd._max_value)
        self.assertIsNone(msd._min_value)

    def test_sensor_memory_offset(self):
        msd = MemoryForSensorData(0, 144 * 2)
        self.assertEqual(msd.sensor_memory_offset, (144 * 2) + 6)

    def test_add_3_values(self):
        msd = MemoryForSensorData(0, 144 * 2)
        memory = bytearray((144 * 2) + 6)
        msd._memory = memory
        msd.add(5)
        msd.add(7)
        msd.add(9)
        self.assertEqual(msd._head_x2, 0)
        self.assertEqual(msd._tail_x2, 6)
        self.assertEqual(msd._current_size, 3)
        self.assertEqual(memory[6],  0)
        self.assertEqual(memory[7],  5)
        self.assertEqual(memory[8],  0)
        self.assertEqual(memory[9],  7)
        self.assertEqual(memory[10], 0)
        self.assertEqual(memory[11], 9)

    def test_add_216_values(self):
        # 216 values into a 144-capacity buffer → oldest 72 entries are overwritten.
        # Values are read back in chronological order (oldest first = from head).
        msd = MemoryForSensorData(0, 144 * 2)
        memory = bytearray((144 * 2) + 6)
        msd._memory = memory
        for x in range(216):
            msd.add(x)

        self.assertEqual(msd._head_x2, 144)
        self.assertEqual(msd._tail_x2, 144)
        self.assertEqual(msd._current_size, 144)

        # Physical storage spot 0 (byte offset 6) holds value 144 (overwrote 0)
        self.assertEqual(memory[6],  0x00)
        self.assertEqual(memory[7],  0x90)   # 0x90 = 144
        self.assertEqual(memory[8],  0x00)
        self.assertEqual(memory[9],  0x91)   # 0x91 = 145
        self.assertEqual(memory[10], 0x00)
        self.assertEqual(memory[11], 0x92)   # 0x92 = 146
        # Byte offset 100 (element index 47 in storage): value 144+47 = 191 = 0xBF
        self.assertEqual(memory[100], 0x00)
        self.assertEqual(memory[101], 0xBF)

        # Chronological readback: oldest element (72) first → newest (215) last
        expected = [x / 10 for x in range(72, 216)]
        self.assertEqual(msd.values, expected)
        self.assertEqual(msd.len, 144)
        self.assertAlmostEqual(msd.max, 21.5, places=1)
        self.assertAlmostEqual(msd.min, 7.2,  places=1)

    def test_scale_1(self):
        # CO2 ring buffer uses scale=1 (raw integer ppm)
        msd = MemoryForSensorData(0, 10 * 2, scale=1)
        memory = bytearray(10 * 2 + 6)
        msd._memory = memory
        msd.add(425)
        msd.add(450)
        vals = msd.values
        self.assertEqual(vals[0], 425.0)
        self.assertEqual(vals[1], 450.0)


class SensorTests(unittest.TestCase):

    def test_object_init(self):
        sensor = Sensor(None, None, 0)
        self.assertIsNone(sensor._sensor)
        # CO2  buffer: offset 0,   header 6, data 288 → end at 294
        self.assertEqual(sensor._data_co2.sensor_memory_offset, 294)
        # Temp buffer: offset 294, header 6, data 288 → end at 588
        self.assertEqual(sensor._data_temp.sensor_memory_offset, 588)
        # Humid buffer: offset 588, header 6, data 288 → end at 882
        self.assertEqual(sensor._data_humid.sensor_memory_offset, 882)
        self.assertEqual(sensor._data_co2.values,   [])
        self.assertEqual(sensor._data_temp.values,  [])
        self.assertEqual(sensor._data_humid.values, [])
