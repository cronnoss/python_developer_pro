# https://python-type-challenges.zeabur.app
from typing import Any, Dict, Final, List, Tuple, Union


def any_func(arg: Any):
    # Modify so it takes an argument of arbitrary type.
    return arg


def dict_func(args: Dict[str, str]):
    # should accept a dict argument, both keys and values are string.
    return args


# "final" challenge: Make sure `my_list` cannot be re-assigned to.
llist: list = []
my_list: Final = llist


def kwargs_func(**kwargs: int | str):
    # takes keyword arguments of type integer or string
    return kwargs


def list_func(args: List[str]):
    # foo should accept a list argument, whose elements are string
    return args


def optional_func(arg: None | int = None):
    # can accept an integer argument, None or no argument at all.
    return arg


def parameter_func(x: int):
    # should accept an integer argument.
    return x


def return_func() -> int:
    # should return an integer argument.
    return 1


def tuple_func(x: Tuple[str, int]):
    # should accept a tuple argument, 1st item is a string, 2nd item is an integer
    return x


# Create a new type called Vector, which is a list of float.
# Python 3.13
type Vector = list[float]


# Python 3.11
# Vector: TypeAlias = list[float]

def typealias_func(v: Vector):
    # Create a new type called Vector, which is a list of float.
    return v


def union_func(x: Union[str, int]):
    # should accept an argument that's either a string or integer.
    return x


# `a` should be an integer
a: int
