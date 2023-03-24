import unittest
import warnings
import sys
sys.path.append('../')
from main_extra import *

class MainTests(unittest.TestCase):
  def test_round_to_int(self):
    self.assertEqual(round_to_int(10.1), 10)
    self.assertEqual(round_to_int(123.4), 123)
    self.assertEqual(round_to_int(9.5), 10)
    self.assertEqual(round_to_int(0.0), 0)
    self.assertNotEqual(round_to_int(9.5), 9)
    self.assertNotEqual(round_to_int(0.5), 1)

  def test_get_temperature_y_values(self):
    self.assertEqual(get_temperature_y_values(20, 0), (20 , 0))
    self.assertEqual(get_temperature_y_values(21, 11), (30 , 10))
    self.assertEqual(get_temperature_y_values(72, 39), (72 , 30))
    self.assertNotEqual(get_temperature_y_values(21, 11), (31 , 5))

  def test_get_humidity_y_values(self):
    self.assertEqual(get_humidity_y_values(80, 0), (100 , 0))
    self.assertEqual(get_humidity_y_values(75, 24), (75 , 0))
    self.assertEqual(get_humidity_y_values(72, 39), (75 , 25))
    self.assertNotEqual(get_humidity_y_values(72, 39), (50 , 25))

  def test_get_fonts(self):
    get_fonts = ['get_font_small', 'get_font_medium', 'get_font_big']

    # leave test directory to previous one
    import os
    os.chdir("../")

    for get_font in get_fonts:
      try:
        with warnings.catch_warnings():
          warnings.simplefilter("ignore", ResourceWarning)
          globals()[get_font]()
        
      except Exception as e:
        assert False, f"'{get_font}' raised an exception {e}"

  def test_get_y_half_scale_value(self):
    self.assertEqual(get_y_half_scale_value(100, 50), 75)
    self.assertEqual(get_y_half_scale_value(21, 10), 15)
    self.assertEqual(get_y_half_scale_value(21, 8), 14)
    self.assertNotEqual(get_y_half_scale_value(21, 8), 15)
