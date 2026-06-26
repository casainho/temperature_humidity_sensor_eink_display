def round_to_int(value):
    return int(round(value, 0))


_CO2_Y_LEVELS = (400, 600, 800, 1000, 1500, 2000, 2500, 3000, 4000, 5000, 6000, 8000, 9999)


def _snap_up(value, levels):
    for level in levels:
        if value <= level:
            return level
    return levels[-1]


def _snap_down(value, levels):
    for level in reversed(levels):
        if value >= level:
            return level
    return levels[0]


def get_co2_y_values(co2_max, co2_min):
    y_max = _snap_up(co2_max, _CO2_Y_LEVELS[1:])
    y_min = _snap_down(co2_min, _CO2_Y_LEVELS)

    return y_max, y_min


def get_temperature_y_values(temperature_max, temperature_min):
    if temperature_max > 60:
        y_max = temperature_max
    elif temperature_max > 50:
        y_max = 60
    elif temperature_max > 40:
        y_max = 50
    elif temperature_max > 30:
        y_max = 40
    elif temperature_max > 20:
        y_max = 30
    elif temperature_max > 10:
        y_max = 20
    else:
        y_max = 10

    if temperature_min > 60:
        y_min = temperature_min
    elif temperature_min > 50:
        y_min = 50
    elif temperature_min > 40:
        y_min = 40
    elif temperature_min > 30:
        y_min = 30
    elif temperature_min > 20:
        y_min = 20
    elif temperature_min > 10:
        y_min = 10
    else:
        y_min = 0

    return y_max, y_min


def get_humidity_y_values(humidity_max, humidity_min):
    if humidity_max > 75:
        y_max = 100
    elif humidity_max > 50:
        y_max = 75
    elif humidity_max > 25:
        y_max = 50
    else:
        y_max = 25

    if humidity_min > 75:
        y_min = 75
    elif humidity_min > 50:
        y_min = 50
    elif humidity_min > 25:
        y_min = 25
    else:
        y_min = 0

    return y_max, y_min


def get_y_half_scale_value(y_max, y_min):
    return int(round(y_min + (y_max - y_min) / 2, 1))

