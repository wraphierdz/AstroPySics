def degDecimal(deg, min, sec):
    """Return formatted sexagesimal to decimal"""
    return (deg + min/60 + sec/3600)