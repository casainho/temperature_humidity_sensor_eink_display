def round_to_int(value):
  return int(round(value, 0))

def get_temperature_y_values(temperature_max, temperature_min):
  # calculate the max ranges y for temperature
  if temperature_max > 60:
    temperature_y_max = temperature_max
  elif temperature_max > 50:
    temperature_y_max = 60
  elif temperature_max > 40:
    temperature_y_max = 50
  elif temperature_max > 30:
    temperature_y_max = 40
  elif temperature_max > 20:
    temperature_y_max = 30
  elif temperature_max > 10:
    temperature_y_max = 20
  else:
    temperature_y_max = 10

  # calculate the min ranges y for temperature
  if temperature_min > 60:
    temperature_y_min = temperature_min
  elif temperature_min > 50:
    temperature_y_min = 50
  elif temperature_min > 40:
    temperature_y_min = 40
  elif temperature_min > 30:
    temperature_y_min = 30
  elif temperature_min > 20:
    temperature_y_min = 20
  elif temperature_min > 10:
    temperature_y_min = 10
  else:
    temperature_y_min = 0

  return temperature_y_max, temperature_y_min

def get_humidity_y_values(humidity_max, humidity_min):
  # calculate the max ranges y for humidity
  if humidity_max > 75:
    humidity_y_max = 100
  elif humidity_max > 50:
    humidity_y_max = 75
  elif humidity_max > 25:
    humidity_y_max = 50
  else:
    humidity_y_max = 25

  # calculate the min ranges y for humidity
  if humidity_min > 75:
    humidity_y_min = 75
  elif humidity_min > 50:
    humidity_y_min = 50
  elif humidity_min > 25:
    humidity_y_min = 25
  else:
    humidity_y_min = 0

  return humidity_y_max, humidity_y_min