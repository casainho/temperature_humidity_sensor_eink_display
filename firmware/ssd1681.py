import time
import framebuf

_W = 200
_H = 200

# SSD1681 commands
_SW_RESET          = 0x12
_DRIVER_OUTPUT     = 0x01
_DATA_ENTRY_MODE   = 0x11
_SET_RAM_X         = 0x44
_SET_RAM_Y         = 0x45
_BORDER_WAVEFORM   = 0x3C
_TEMP_SENSOR       = 0x18
_DISP_UPDATE_CTRL2 = 0x22
_MASTER_ACTIVATION = 0x20
_SET_RAM_X_CNT     = 0x4E
_SET_RAM_Y_CNT     = 0x4F
_WRITE_RAM_BW      = 0x24
_DEEP_SLEEP        = 0x10


class SSD1681:
    def __init__(self, spi, cs, dc, rst, busy):
        self._spi  = spi
        self._cs   = cs
        self._dc   = dc
        self._rst  = rst
        self._busy = busy

        # 200×200, 1 bit/pixel, white background (all bits set = white on e-ink)
        self._buf = bytearray(_W * _H // 8)
        self.fb = framebuf.FrameBuffer(self._buf, _W, _H, framebuf.MONO_HLSB)
        self.fb.fill(1)  # white

        self._hw_reset()
        self._init()

    def _hw_reset(self):
        self._rst(1); time.sleep_ms(10)
        self._rst(0); time.sleep_ms(10)
        self._rst(1); time.sleep_ms(10)

    def _wait(self):
        time.sleep_ms(5)
        while self._busy():   # BUSY pin HIGH = controller busy
            time.sleep_ms(10)

    def _cmd(self, c):
        self._dc(0); self._cs(0)
        self._spi.write(bytes([c]))
        self._cs(1)

    def _data(self, *args):
        self._dc(1); self._cs(0)
        self._spi.write(bytes(args))
        self._cs(1)

    def _init(self):
        self._cmd(_SW_RESET); self._wait()
        self._cmd(_DRIVER_OUTPUT);  self._data(0xC7, 0x00, 0x00)  # 200 lines (MUX=199)
        self._cmd(_DATA_ENTRY_MODE); self._data(0x03)               # X+, Y+
        self._cmd(_SET_RAM_X);       self._data(0x00, 0x18)         # X: 0..24 (25 bytes)
        self._cmd(_SET_RAM_Y);       self._data(0x00, 0x00, 0xC7, 0x00)  # Y: 0..199
        self._cmd(_BORDER_WAVEFORM); self._data(0x05)
        self._cmd(_TEMP_SENSOR);     self._data(0x80)               # use internal sensor
        self._cmd(_DISP_UPDATE_CTRL2); self._data(0xB1)
        self._cmd(_MASTER_ACTIVATION); self._wait()

    def show(self):
        self._cmd(_SET_RAM_X_CNT); self._data(0x00)
        self._cmd(_SET_RAM_Y_CNT); self._data(0x00, 0x00)
        self._cmd(_WRITE_RAM_BW)
        self._dc(1); self._cs(0)
        self._spi.write(self._buf)
        self._cs(1)
        self._cmd(_DISP_UPDATE_CTRL2); self._data(0xF7)  # full update
        self._cmd(_MASTER_ACTIVATION); self._wait()

    def sleep(self):
        self._cmd(_DEEP_SLEEP); self._data(0x01)  # deep sleep, retain RAM
