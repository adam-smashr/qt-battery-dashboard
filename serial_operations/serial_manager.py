def read_voltage(data: str) -> float:
    try:
        return float(data.strip())
    except ValueError:
        return -1.0
