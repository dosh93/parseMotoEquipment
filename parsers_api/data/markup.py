import json
import dataclasses

from enum import Enum
from dataclasses import dataclass
from typing import List
from parsers_api.my_helper.helpers import send_service_message

from parsers_api.logger import logger


class MarkupType(Enum):
    FIX = 'fix'
    PERCENTAGE = 'percentage'


@dataclass
class Markup:
    threshold: int
    markup: int
    markup_type: MarkupType


def json_to_markup(json_str: str) -> List[Markup]:
    data = json.loads(json_str)
    return [Markup(threshold=item['threshold'], markup=item['markup'], markup_type=MarkupType(item['markup_type'])) for
            item in data]


def markup_to_json(markup):
    return json.dumps(to_serializable(markup), ensure_ascii=False)


def to_serializable(val):
    if isinstance(val, Enum):
        return val.value
    elif dataclasses.is_dataclass(val):
        return {k: to_serializable(v) for k, v in dataclasses.asdict(val).items()}
    elif isinstance(val, list):
        return [to_serializable(v) for v in val]
    return val


def apply_markup(price: float, markups: List[Markup], url: str) -> float:
    applied_price = price
    for markup in sorted(markups, key=lambda m: m.threshold, reverse=True):
        if price >= markup.threshold:
            if markup.markup_type == MarkupType.FIX:
                applied_price += markup.markup
            elif markup.markup_type == MarkupType.PERCENTAGE:
                applied_price += price * (markup.markup / 100)
            break
    logger.info(f"Current price {price}, applied_price {applied_price}, markup {markups}")
    if price == applied_price:
        send_service_message(
            f"Product with url {url} is not applied markup. Price {price} and applied_price {applied_price}",
            "not_apply_markup")
    return applied_price


def remove_markup(applied_price: float, markups: List[Markup]) -> float:
    price_without_markup = applied_price
    for markup in sorted(markups, key=lambda m: m.threshold, reverse=True):
        if markup.markup_type == MarkupType.FIX:
            price_without_markup = applied_price - markup.markup
        elif markup.markup_type == MarkupType.PERCENTAGE:
            price_without_markup = applied_price / (1 + markup.markup / 100)
        if price_without_markup >= markup.threshold:
            logger.info(
                f"Applied price {applied_price}, price without markup {price_without_markup}, markup {markups}")
            return price_without_markup

    logger.warning(f"No matching markup found for applied price {applied_price}")
    return applied_price
