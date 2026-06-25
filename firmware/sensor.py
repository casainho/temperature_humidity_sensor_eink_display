# RTC memory layout (1101 bytes used, 1104 bytes reserved):
#   [0..2]     counter (3 bytes)
#   [3..368]   CO2 ring buffer   (6 header + 360 data)
#   [369..734] Temp ring buffer  (6 header + 360 data)
#   [735..1100] Humid ring buffer (6 header + 360 data)

_RTC_MEM_SIZE = 1104
_SENSOR_MEM_OFFSET = 3  # first 3 bytes reserved for the wake counter

try:
    import machine
    from scd41 import SCD41

    _rtc = machine.RTC()

    def _is_deepsleep_wake():
        return machine.reset_cause() == machine.DEEPSLEEP_RESET

    def _load_mem():
        raw = _rtc.memory()
        if _is_deepsleep_wake() and len(raw) >= _RTC_MEM_SIZE:
            return bytearray(raw)
        return bytearray(_RTC_MEM_SIZE)

    def _save_mem(data):
        _rtc.memory(data)

    _testing = False

except Exception:
    print("sensor.py: running in test mode")
    _testing = True

    def _is_deepsleep_wake():
        return False

    def _load_mem():
        return bytearray(_RTC_MEM_SIZE)

    def _save_mem(data):
        pass


_mem = _load_mem()


class MemoryForSensorData:
    """Circular ring buffer backed by the shared RTC memory bytearray."""

    def __init__(self, offset_address, capacity_x2, scale=10):
        self._memory = _mem
        self._scale = scale
        self._offset_address_initial = offset_address
        self._offset_address = offset_address
        self._capacity_x2 = capacity_x2

        self._current_size = 0
        self._head_x2 = 0
        self._tail_x2 = 0

        if _is_deepsleep_wake():
            m = self._memory
            o = offset_address
            self._current_size = (m[o] << 8) | m[o + 1]
            self._head_x2 = (m[o + 2] << 8) | m[o + 3]
            self._tail_x2 = (m[o + 4] << 8) | m[o + 5]

        self._offset_address += 6
        self._max_value = None
        self._min_value = None

    @property
    def sensor_memory_offset(self):
        return self._offset_address + self._capacity_x2

    def add(self, value):
        cap = self._capacity_x2
        o = self._offset_address

        if self._tail_x2 == self._head_x2 and (self._current_size * 2) == cap:
            self._head_x2 = (self._head_x2 + 2) % cap

        self._memory[o + self._tail_x2]     = (value >> 8) & 0xFF
        self._memory[o + self._tail_x2 + 1] = value & 0xFF
        self._tail_x2 = (self._tail_x2 + 2) % cap

        if (self._current_size * 2) < cap:
            self._current_size += 1

        oi = self._offset_address_initial
        self._memory[oi]     = (self._current_size >> 8) & 0xFF
        self._memory[oi + 1] = self._current_size & 0xFF
        self._memory[oi + 2] = (self._head_x2 >> 8) & 0xFF
        self._memory[oi + 3] = self._head_x2 & 0xFF
        self._memory[oi + 4] = (self._tail_x2 >> 8) & 0xFF
        self._memory[oi + 5] = self._tail_x2 & 0xFF

    @property
    def values(self):
        if self._current_size < 1:
            return []
        data = [0.0] * self._current_size
        cap = self._capacity_x2
        o = self._offset_address
        head_x2 = self._head_x2
        self._max_value = None
        self._min_value = None
        for i in range(self._current_size):
            raw = (self._memory[o + head_x2] << 8) | (self._memory[o + head_x2 + 1] & 0xFF)
            v = raw / self._scale
            data[i] = v
            if self._max_value is None or v > self._max_value:
                self._max_value = v
            if self._min_value is None or v < self._min_value:
                self._min_value = v
            head_x2 = (head_x2 + 2) % cap
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


class Sensor:
    def __init__(self, i2c_scl_pin, i2c_sda_pin, sleep_memory_offset, i2c_bus=1):
        if not _testing:
            i2c = machine.I2C(i2c_bus,
                              scl=machine.Pin(i2c_scl_pin),
                              sda=machine.Pin(i2c_sda_pin),
                              freq=100_000)
            self._sensor = SCD41(i2c)
        else:
            self._sensor = None

        self._last_co2   = 0
        self._last_temp  = 0.0
        self._last_humid = 0.0

        # CO2 stored as raw ppm integer (scale=1)
        self._data_co2   = MemoryForSensorData(sleep_memory_offset, 180 * 2, scale=1)
        sleep_memory_offset = self._data_co2.sensor_memory_offset

        # Temperature stored ×10 so one decimal place survives integer storage
        self._data_temp  = MemoryForSensorData(sleep_memory_offset, 180 * 2, scale=10)
        sleep_memory_offset = self._data_temp.sensor_memory_offset

        # Humidity stored ×10
        self._data_humid = MemoryForSensorData(sleep_memory_offset, 180 * 2, scale=10)

    def read(self):
        co2, temp, humid = self._sensor.read()
        self._last_co2   = int(co2)
        self._last_temp  = round(temp, 1)
        self._last_humid = round(humid, 1)

    def read_and_store(self):
        self.read()

        self._data_co2.add(self._last_co2)
        self._data_temp.add(int(self._last_temp * 10))
        self._data_humid.add(int(self._last_humid * 10))

        _save_mem(_mem)

    @property
    def co2(self):
        return self._last_co2

    @property
    def temperature(self):
        return self._last_temp

    @property
    def humidity(self):
        return self._last_humid

    @property
    def historic_data_co2(self):
        v = self._data_co2.values
        return v, self._data_co2.max, self._data_co2.min, self._data_co2.len

    @property
    def historic_data_temperature(self):
        v = self._data_temp.values
        return v, self._data_temp.max, self._data_temp.min, self._data_temp.len

    @property
    def historic_data_humidity(self):
        v = self._data_humid.values
        return v, self._data_humid.max, self._data_humid.min, self._data_humid.len
