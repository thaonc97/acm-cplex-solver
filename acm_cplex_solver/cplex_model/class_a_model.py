from dataclasses import astuple, dataclass, field
from typing import List

from numpy import ndarray

@dataclass
class ClassAModel:
    """
    1 instance của class này thể hiện 1 số thông tin của 1 ngày-địa điểm (u,k)
    """
    r : ndarray # resource, chứa lượng view tại các địa điểm, r[u,k] là lượng view tại ngày u, địa điểm k
    ratio : List[float] # tỉ lệ chia sẻ network - domain, share_rate[k] = 1, nghĩa là tại địa điểm k tỉ lệ chia sẻ cho network là 100% 
    total_b_c_network: ndarray
    total_b_c_domain: ndarray
    campaigns_a_network : List[List[List[int]]] # campaigns_a_network[u][k] = List[int] = danh sách campaign network cấp A tại u,k
    campaigns_a_domain:  List[List[List[int]]] # campaigns_a_network[u][k] = List[int] = danh sách campaign network cấp A tại u,k
