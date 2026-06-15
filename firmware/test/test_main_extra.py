import unittest
import sys
sys.path.append('../')
from scale import (
    round_to_int,
    get_co2_y_values,
    get_temperature_y_values,
    get_humidity_y_values,
    get_y_half_scale_value,
)


class MainExtraTests(unittest.TestCase):

    def test_round_to_int(self):
        self.assertEqual(round_to_int(10.1), 10)
        self.assertEqual(round_to_int(123.4), 123)
        self.assertEqual(round_to_int(9.5), 10)
        self.assertEqual(round_to_int(0.0), 0)
        self.assertNotEqual(round_to_int(9.5), 9)

    def test_get_co2_y_values(self):
        self.assertEqual(get_co2_y_values(500,  420), (600,  400))
        self.assertEqual(get_co2_y_values(700,  420), (800,  400))
        self.assertEqual(get_co2_y_values(900,  420), (1000, 400))
        self.assertEqual(get_co2_y_values(1200, 420), (1500, 400))
        self.assertEqual(get_co2_y_values(1600, 420), (2000, 400))
        self.assertEqual(get_co2_y_values(2100, 420), (2500, 400))
        self.assertEqual(get_co2_y_values(2600, 420), (3000, 400))
        self.assertEqual(get_co2_y_values(4100, 420), (5000, 400))
        self.assertEqual(get_co2_y_values(8100, 420), (9999, 400))
        # min snapping
        self.assertEqual(get_co2_y_values(900, 650), (1000, 600))
        self.assertEqual(get_co2_y_values(900, 850), (1000, 800))

    def test_get_temperature_y_values(self):
        self.assertEqual(get_temperature_y_values(20, 0),  (20, 0))
        self.assertEqual(get_temperature_y_values(21, 11), (30, 10))
        self.assertEqual(get_temperature_y_values(72, 39), (72, 30))
        self.assertNotEqual(get_temperature_y_values(21, 11), (31, 5))

    def test_get_humidity_y_values(self):
        self.assertEqual(get_humidity_y_values(80, 0),  (100, 0))
        self.assertEqual(get_humidity_y_values(75, 24), (75,  0))
        self.assertEqual(get_humidity_y_values(72, 39), (75,  25))
        self.assertNotEqual(get_humidity_y_values(72, 39), (50, 25))

    def test_get_y_half_scale_value(self):
        self.assertEqual(get_y_half_scale_value(100, 50), 75)
        self.assertEqual(get_y_half_scale_value(21, 10),  15)
        self.assertEqual(get_y_half_scale_value(21, 8),   14)
        self.assertNotEqual(get_y_half_scale_value(21, 8), 15)
