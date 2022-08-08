from applitoolsify.config import VERBOSE


def print_verbose(*args, **kwargs):
    if VERBOSE:
        print(*args, **kwargs)
