from dataclasses import asdict, dataclass, field
from typing import Literal

@dataclass
class Transaction:
    id: str
    type: Literal["income","expense"]
    date : str
    amount : int
    category : str
    memo : str = ""
    tags : list[str] = field(default_factory=list)


    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Transaction":
        return cls(**data)

