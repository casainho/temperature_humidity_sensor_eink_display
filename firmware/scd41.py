import time

_ADDR = 0x62

_CMD_STOP_PERIODIC   = 0x3F86
_CMD_SINGLE_SHOT     = 0x219D
_CMD_READ_MEAS       = 0xEC05
_CMD_FORCED_RECAL    = 0x362F
_CMD_SET_ASC         = 0x2416
_CMD_PERSIST         = 0x3615


def _crc8(data):
    crc = 0xFF
    for b in data:
        crc ^= b
        for _ in range(8):
            crc = ((crc << 1) ^ 0x31) & 0xFF if crc & 0x80 else (crc << 1) & 0xFF
    return crc


class SCD41:
    def __init__(self, i2c):
        self._i2c = i2c

    def _cmd(self, cmd):
        self._i2c.writeto(_ADDR, bytes([cmd >> 8, cmd & 0xFF]))

    def _write_word(self, cmd, value):
        crc = _crc8(bytes([value >> 8, value & 0xFF]))
        self._i2c.writeto(_ADDR, bytes([cmd >> 8, cmd & 0xFF, value >> 8, value & 0xFF, crc]))

    def _read_words(self, n):
        buf = bytearray(n * 3)
        self._i2c.readfrom_into(_ADDR, buf)
        result = []
        for i in range(n):
            word = (buf[i * 3] << 8) | buf[i * 3 + 1]
            if buf[i * 3 + 2] != _crc8(buf[i * 3:i * 3 + 2]):
                raise ValueError("SCD41 CRC error")
            result.append(word)
        return result

    def stop_periodic_measurement(self):
        self._cmd(_CMD_STOP_PERIODIC)
        time.sleep_ms(500)

    def perform_forced_recalibration(self, target_co2_ppm=400):
        self._cmd(_CMD_STOP_PERIODIC)
        time.sleep_ms(500)
        self._write_word(_CMD_FORCED_RECAL, target_co2_ppm)
        time.sleep_ms(400)

    def set_asc_enabled(self, enabled):
        self._write_word(_CMD_SET_ASC, 0x0001 if enabled else 0x0000)

    def persist_settings(self):
        self._cmd(_CMD_PERSIST)
        time.sleep_ms(800)

    def read(self):
        """Single-shot measurement. Returns (co2_ppm, temp_c, humidity_pct)."""
        self.stop_periodic_measurement()
        self._cmd(_CMD_SINGLE_SHOT)
        time.sleep_ms(5000)
        self._cmd(_CMD_READ_MEAS)
        time.sleep_ms(1)
        words = self._read_words(3)
        co2 = words[0]
        temp = round(-45.0 + 175.0 * words[1] / 65535.0, 1)
        hum = round(100.0 * words[2] / 65535.0, 1)
        return co2, temp, hum

