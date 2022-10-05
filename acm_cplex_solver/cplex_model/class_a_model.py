from dataclasses import astuple, dataclass, field
<<<<<<< HEAD

=======
from typing import List
>>>>>>> 81f2f6a868c1f22cce4b1a6a07f09866b5683c5c

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
