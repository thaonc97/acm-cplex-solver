from dataclasses import astuple, dataclass, field
from typing import List

from numpy import ndarray

@dataclass
class ClassAModelSolver:
    
 
    r : ndarray # resource, chứa lượng view tại các địa điểm, r[u,k] là lượng view tại ngày u, địa điểm k
    ratio : List[float] # tỉ lệ chia sẻ network - domain, share_rate[k] = 1, nghĩa là tại địa điểm k tỉ lệ chia sẻ cho network là 100% 
    total_b_c_network: ndarray
    total_b_c_domain: ndarray
    campaigns_class_a_network : List[List[List[int]]] # campaigns_a_network[u][k] = List[int] = danh sách campaign network cấp A tại u,k
    campaigns_class_a_domain:  List[List[List[int]]] # campaigns_a_network[u][k] = List[int] = danh sách campaign network cấp A tại u,k


    def solve(self) -> list:
        
        
        x_a = []
        U,K = self.r.shape
        for u in range(U):
            for k in range(K):
                num_a_network = len(self.campaigns_class_a_network[u][k])
                num_a_domain  = len(self.campaigns_class_a_domain[u][k])
                left_network = self.r[u,k]*self.ratio[k] - self.total_b_c_network[u,k]
                left_domain = self.r[u,k]*(1 - self.ratio[k]) - self.total_b_c_domain[u,k]
                left_total = abs(left_network+left_domain)
                # nếu ko có campaign cấp A thì add -1 vào nếu còn tài nguyên
                if num_a_network == 0 and num_a_domain == 0:                    
                    if(left_total>0):
                        self._add_x_a(x_a, -1, u, k, left_total)

                # nếu chỉ có network thì chia hết cho campaign network, left_total=0 vẫn chia = 0 để dự phòng
                elif num_a_network != 0 and num_a_domain == 0:
                    for t in self.campaigns_class_a_network[u][k]:
                        self._add_x_a(x_a, t, u, k, left_total/num_a_network)

                # nếu chỉ có domain thì chia hết cho campaign domain, left_total=0 vẫn chia = 0 để dự phòng        
                elif num_a_network == 0 and num_a_domain != 0:
                    for t in self.campaigns_class_a_domain[u][k]:
                        self._add_x_a(x_a, t, u, k, left_total/num_a_domain)

                elif num_a_network !=0 and num_a_domain !=0:
                    if(left_total>0):
                        # lấy min để xác định lượng tài nguyên thực sự còn phân bổ cho network
                        # ví dụ left_total = 10, left_network = - 5, left_domain = 15 nghĩa là network đã chạy lấn sang 5
                        # thì phần còn dư cho network là 0, dư cho domain là 10                        
                        if(min(left_network, left_total)>0):
                            for t in self.campaigns_class_a_network[u][k]:
                                self._add_x_a(x_a, t, u, k, min(left_network, left_total)/num_a_network)                       
                           
                        if(min(left_domain, left_total)>0):
                            for t in self.campaigns_class_a_domain[u][k]:
                                self._add_x_a(x_a, t, u, k, min(left_domain, left_total)/num_a_domain)   

                    else:
                        # trường hợp hết tài nguyên thì vẫn add campaign cấp A = 0 vào để dự phòng
                        for t in self.campaigns_class_a_network[u][k]:
                            self._add_x_a(x_a, t, u, k, 0)
                        for t in self.campaigns_class_a_domain[u][k]:
                            self._add_x_a(x_a, t, u, k, 0)
        
        return x_a

    def _add_x_a(self, x_a, campaign_id, date, place_id, value):
        x_a.append({
            'campaign_id' : campaign_id,
            'date': date,
            'place_id':place_id,            
            'value': value
        })
