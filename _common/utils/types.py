def cast(value, caster, fallback = None):
    # TODO move to scripts
    try:
        return caster(value)
    except ValueError:
        return fallback