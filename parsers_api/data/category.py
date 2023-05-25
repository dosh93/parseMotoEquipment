from dataclasses import dataclass
from typing import List


@dataclass
class Category:
    id: int
    name: int
    markup: str


def db_to_category(rows) -> List[Category]:
    return [Category(id=row[0], name=row[1], markup=row[2]) for row in rows]
