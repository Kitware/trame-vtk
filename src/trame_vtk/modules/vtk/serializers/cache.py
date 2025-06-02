PROP_CACHE = {}


def cache_properties(obj_id, ctx, props):
    if not ctx.ignore_last_dependencies:
        prev = PROP_CACHE.get(obj_id)
        PROP_CACHE[obj_id] = props

        if prev is None:
            return props

        delta = {}
        if prev != props:
            for key in props:
                if prev.get(key) != props[key]:
                    delta[key] = props[key]
        return delta

    PROP_CACHE[obj_id] = props
    return props
