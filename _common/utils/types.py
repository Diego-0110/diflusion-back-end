def cast(value, caster, fallback = None):
    try:
        return caster(value)
    except ValueError:
        return fallback