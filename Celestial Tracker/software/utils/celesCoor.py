def celesCoor(decimal, hour=False, pnt=2):
    """Format celestial coordinate to sexagesimal (60 based number).
    Able to convert degrees to hour in celestial coordinate if hour=True. Support custom
    decimal or sexagesimal format, decimal floating point can be specified from pnt param."""

    unit = ['°', "'", '"']
    # convert derajat jadi jam (15° = 1h)
    if hour:
        mainComp_h = decimal/15
        decimal = mainComp_h
        unit = ['h', 'm', 's']
    # seksagesimal derajat:
    mainComp = int(decimal)
    min_float = (decimal-mainComp)*60
    min = int(min_float)
    sec = (min_float - min)*60
    return f'{mainComp}{unit[0]}{min}{unit[1]}{sec:.{pnt}f}{unit[2]}'
