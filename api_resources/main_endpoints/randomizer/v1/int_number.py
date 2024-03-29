from typing import Union
from random import randint
from time import perf_counter


def main(min_value: int, max_value: int) -> Union[dict, None]:
    start_time = perf_counter()
    generated_data = dict()

    try:
        generated_data['data'] = randint(min_value, max_value)
    except Exception:
        return None

    generated_data['processing_time'] = float(perf_counter() - start_time)

    return generated_data
