import os
from enum import Enum
from typing import Optional


class ExtendedEnum(Enum):
    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))


class Stacks(str, ExtendedEnum):
    DEV = 'dev'


class Vars(str, ExtendedEnum):
    STACK = 'STACK'
    SUBS_TO_CRAWL = 'SUBS_TO_CRAWL'
    REGEX_PATTERN_STOCKS = 'REGEX_PATTERN_STOCKS'
    STOCK_BLACKLIST = 'STOCK_BLACKLIST'
    INPUT_FILE_LIST = 'INPUT_FILE_LIST'
    COMMENT_THRESHOLD_LOWER = 'COMMENT_THRESHOLD_LOWER'
    COMMENT_THRESHOLD_UPPER = 'COMMENT_THRESHOLD_UPPER'


CONFIGURATION = {
    Stacks.DEV: {
        Vars.SUBS_TO_CRAWL: ["wallstreetbets", "stocks"],  # , "investing", "smallstreetbets"]
        Vars.REGEX_PATTERN_STOCKS: r'\b([A-Z]+)\b',
        Vars.STOCK_BLACKLIST: ["A", "I", "DD", "WSB", "YOLO", "RH", "EV", "PE", "ETH", "BTC", "E"],
        Vars.INPUT_FILE_LIST: ["input/list1.csv", "input/list2.csv", "input/list3.csv"],

        Vars.COMMENT_THRESHOLD_LOWER: -5,
        Vars.COMMENT_THRESHOLD_UPPER: 10
    }
}

ASSIGNED_STACK: Optional[Stacks] = None


def assign_stack(stack: Optional[Stacks]):
    global ASSIGNED_STACK
    ASSIGNED_STACK = stack


def get_stack() -> Stacks:
    if ASSIGNED_STACK is not None:
        return ASSIGNED_STACK
    if Vars.STACK.value not in os.environ:
        return Stacks.DEV
    else:
        return Stacks(os.environ[Vars.STACK.value])


def get_config(var) -> str:
    stack = get_stack()
    return get_config_for_stack(stack, var)


def get_config_for_stack(stack, var) -> str:
    if var.value not in os.environ:
        if var not in CONFIGURATION[stack]:
            raise Exception(f"Invalid configuration: missing env variable '{var}'")
        else:
            return CONFIGURATION[stack][var]
    else:
        return os.environ[var.value]
