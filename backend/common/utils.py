import random
import string


def random_lower_string(k: int) -> str:
    return "".join(random.choices(string.ascii_lowercase, k=k))
