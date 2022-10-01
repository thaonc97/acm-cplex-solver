from dataclasses import astuple, dataclass
from typing import List
from numpy import array, ndarray

from acm_cplex_solver.generated_protobuf.acm_base_pb2 import CampaignPriority, ShareType


@dataclass
class PaperModel:
    """_summary_
        Chứa model giống paper.
    Returns:
        _type_: _description_
    """
    T : int # tổng số chiến dịch cấp B,C, id chiến dịch từ 0--> T-1
    U : int # tổng số ngày chạy của tất cả chiến dịch, đánh số từ 0 --> U-1
    K : int # tổng số địa điểm, đánh số từ 0 --> K-1
    r : ndarray # resource, chứa lượng view tại các địa điểm, r[u,k] là lượng view tại ngày u, địa điểm k
    D : List[List[int]] # mảng chứa ngày chạy của các chiến dịch, mỗi chiến dịch có ngày chạy dạng [fromDate, toDate]
    G : list # mảng chứa giá trị group_id của campaign, nếu = none thì ko có nhóm
    CTR : ndarray # CTR của địa điểm
    d : List[float] # lượng chạy của các campaign B,C
    L : List[array] # danh sách địa điểm của campaign, L[t] là danh sách địa điểm của campaign t
     
    t_0 : int # id của campaign domain đầu tiên tính từ 0 --> T-1
    ratio : List[float] # tỉ lệ chia sẻ network - domain, share_rate[k] = 1, nghĩa là tại địa điểm k tỉ lệ chia sẻ cho network là 100%  
    priority : List[int] # class B,C của các campaign cấp B,C
    share_type : List[int] # Loại chia sẻ, thường dùng là SOFT
    B : List[List[int]] # chứa danh sách chiến dịch chạy tại địa điểm K
    cl : ndarray #  cl[t,u,k] = 1 nghĩa là campaign cấp C t chạy tại ngày u, điểm k 
    w : ndarray # chứa trọng số của campaign tại các ngày, w[t,u] = 10, mặc định, 0 là 0 chạy, = 20 là chạy gấp đôi 10    
    alpha : ndarray = None # alpha[t,u,k] = số lượng mong muốn của campaign t, ngày u, địa điểm k
    