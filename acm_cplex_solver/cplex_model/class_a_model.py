from dataclasses import astuple, dataclass, field
from typing import List

@dataclass
class ClassAModel:
    """
    1 instance của class này thể hiện 1 số thông tin của 1 ngày-địa điểm (u,k)
    """
    r: float
    ratio: float
    total_network_lefts: float
    total_domain_lefts: float
    x_a: float
    campaigns_network :List[int] 
    campaigns_domain : List[int]
