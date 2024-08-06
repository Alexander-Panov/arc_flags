import time
import functools


def clock(func=None, *, verbose=False):
    if func is None:
        return functools.partial(clock, verbose=verbose)

    @functools.wraps(func)
    def clocked(*args, **kwargs):
        t0 = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - t0
        name = func.__name__
        if verbose:
            arg_lst = [repr(arg) for arg in args]
            arg_lst.extend(f'{k}={v!r}' for k, v in kwargs.items())
            arg_str = ', '.join(arg_lst)
            print(f'[{elapsed:.8f}s] {name}({arg_str}) -> {result!r}')
        else:
            print(f'[{elapsed:.8f}s] {name}')
        return result

    return clocked
