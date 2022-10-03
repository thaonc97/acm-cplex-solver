from dataclasses import astuple, dataclass, field
import string
from typing import List
import numpy as np
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
    alpha_formula: int = 3 # công thức tính alpha, hiện tại chỉ dùng công thức số 3
    alpha : ndarray = field(init = False) # alpha[t,u,k] = số lượng mong muốn của campaign t, ngày u, địa điểm k
    
    
    def __post_init__(self): 
        self._re_update_w()
        self.alpha = self._calculate_alpha(self.alpha_formula) # hiện tại chỉ dùng công thức 3        

    
    def _re_update_w(self):
        """Cập nhật trọng số cho các campaign:
        Nếu 1 campaign type B bất kì có 1 ngày mà tất cả các địa điểm của nó
        có campaign cấp C chạy, coi như w ngày hôm đó bằng 0.

        Parameters
        ----------
        model_ready_data : list
        have_c_network: np.array()
            Ma trận tồn tại campaign c: have_c[u,k] = 1 nếu ngày u địa điểm k
            có campaign type C network chạy
        have_c_domain : np.array()
            Tương tự have_c_network nhưng cho domain 
        """

        priority = self.priority
        if CampaignPriority.CLASS_C not in priority:
            pass  # Không cần tính toán thay đổi nếu ko có class C

        T = self.T
        U = self.U
        K = self.K
        t_0 = self.t_0
        D = self.D
        L = self.L
        cl = self.cl
        w = self.w.copy()
        # Compute have_c
        have_c_network = np.zeros([U, K])
        have_c_domain = np.zeros([U, K])
        for u in range(U):
            for k in range(K):
                have_c_network[u, k] = np.sum(
                    [cl[t, u, k] for t in range(len(cl[:, u, k])) if t < t_0])
                have_c_domain[u, k] = np.sum(
                    [cl[t, u, k] for t in range(len(cl[:, u, k])) if t >= t_0])  
        

        not_have_c_network = 1- have_c_network # Ma trận không có campaign c
        not_have_c_domain = 1 - have_c_domain

        for t in range(T):
            if priority[t] == CampaignPriority.CLASS_B:
                if t < t_0:
                    days_filled_by_c= np.sum(not_have_c_network[:,L[t]], axis = 1)

                else:
                    days_filled_by_c= np.sum(not_have_c_domain[:,L[t]], axis = 1)
                    
                for u in range (D[t][0],D[t][1] + 1):
                    if days_filled_by_c[u] == 0: 
                        w[t][u] = 0
                    # Giải thích:  Nếu days_filled_by_c[u] = 0 tức tất cả giá trị của
                    # not_have_c network (hoặc domain) vào ngày u của các địa điểm
                    # mà campaign t chạy đều bằng 0 , điều này đồng nghĩa với tất
                    #  cả các địa điểm vào ngày u đều có campaign cấp C chạy.
        self.w = w

    
    def _calculate_alpha(self, alpha_formula : int) -> ndarray:
        if alpha_formula == 0 :
            return self._formula_0()
        elif alpha_formula == 1:
            return self._formula_1()
        elif alpha_formula == 2:
            return self._formula_2()
        elif alpha_formula == 3:
            return self._formula_3()
        else:
            raise Exception("Sai tham số công thức alpha")

    def _formula_0(self):
        """
        Công thức phức tạp thầy Sơn
        """
      
        K = self.K
        U = self.U
        T = self.T
        r = self.r
        D = self.D
        G = self.G
        CTR = self.CTR
        d = self.d
        w = self.w
        L = self.L
        B = self.B       
        t_0 = self.t_0
        ratio = self.ratio
        priority = self.priority
        share_type = self.share_type
        cl = self.cl          
        w = self.w       
        
            # Calculate s_k
        s = []
        s_network = []
        s_domain = []
        for k in range(K):
            s_k_network = 0
            s_k_domain = 0
            for i in B[k]:
                if priority[i] == 'CLASS_B':
                    if i < t_0 :
                        s_k_network += d[i]/(len(L[i])*(D[i][1]+1-D[i][0]))
                    if i >= t_0:
                        s_k_domain += d[i]/(len(L[i])*(D[i][1]+1-D[i][0]))

            s_network.append(s_k_network)
            s_domain.append(s_k_domain)

        # Calculate alpha_tuk
        alpha_network =np.zeros((T,U,K))
        alpha_domain = np.zeros((T,U,K))
        for t in range(T):
            if t < t_0 and priority[t] == 'CLASS_B':
                deno = np.sum([w[t,u_bar]*r[u_bar,k_bar]/s_network[k_bar]
                            for u_bar in range(D[t][0], D[t][1]+1) for k_bar in L[t]])

                if deno !=0:
                    for u in range(D[t][0], D[t][1]+1):
                        for k in L[t]:
                            nume = w[t,u]*r[u,k]/s_network[k]
                            alpha_network[t,u,k] = nume/deno*d[t]
                else:
                    for u in range(D[t][0], D[t][1]+1):
                        for k in L[t]:
                            alpha_network[t,u,k] = 0  # If denominator = 0 then all associated alphas = 0

            if t>=t_0 and priority[t] == 'CLASS_B':
                deno = np.sum([w[t,u_bar]*r[u_bar,k_bar]/s_domain[k_bar] 
                            for u_bar in range(D[t][0], D[t][1]+1) for k_bar in L[t]])
                if deno !=0:
                    for u in range(D[t][0], D[t][1]+1):
                        for k in L[t]:
                            nume = w[t,u]*r[u,k]/s_domain[k]
                            alpha_domain[t,u,k] = nume/deno*d[t]
                else:
                    for u in range(D[t][0], D[t][1]+1):
                        for k in L[t]:
                            alpha_domain[t,u,k] = 0  # If denominator = 0 then all associated alphas = 0

        alpha = alpha_network + alpha_domain
        
        return alpha
    

    def _formula_1(self):
        """
        Tính theo công thức của thầy Sơn + đều theo ngày a Phong
        """
        K = self.K
        U = self.U
        T = self.T
        r = self.r
        D = self.D
        G = self.G
        CTR = self.CTR
        d = self.d
        w = self.w
        L = self.L
        B = self.B       
        t_0 = self.t_0
        ratio = self.ratio
        priority = self.priority
        share_type = self.share_type
        cl = self.cl          
        w = self.w 
        
        # Calculate d_tu
        #d_tu = [d[t]*w[t]/(np.sum(w[t])) for t in range(T)]
        d_tu = [self._calculate_d_t_u(d[t],w[t]) for t in range(T)]
        d_tu = np.nan_to_num(d_tu)  # Chuyển những thằng nan về 0, có thể không cần
        
        # Calculate s_k
        s = []
        s_network = []
        s_domain = []
        for k in range(K):
            s_k_network = 0
            s_k_domain = 0
            for i in B[k]:
                if priority[i] == 'CLASS_B':
                    if i < t_0 :
                        s_k_network += d[i]/(len(L[i])*(D[i][1]+1-D[i][0]))
                    if i >= t_0:
                        s_k_domain += d[i]/(len(L[i])*(D[i][1]+1-D[i][0]))

            s_network.append(s_k_network)
            s_domain.append(s_k_domain)
        
        # Calculate alpha_tuk
        alpha_network =np.zeros((T,U,K))
        alpha_domain = np.zeros((T,U,K))
        for u in range(U):
            for t in range(T):
                if D[t][0] <= u <= D[t][1]:
                    if t < t_0 and priority[t] == 'CLASS_B':
                        deno = np.sum([r[u,k_bar]/s_network[k_bar] for k_bar in L[t]])

                        if deno !=0:
                            for k in L[t]:
                                nume = r[u,k]/s_network[k]
                                alpha_network[t,u,k] = nume/deno*d_tu[t][u]
                        else:
                            for k in L[t]:
                                alpha_network[t,u,k] = 0  # If denominator = 0 then all associated alphas = 0

                    if t>=t_0 and priority[t] == 'CLASS_B':
                        deno = np.sum([r[u,k_bar]/s_domain[k_bar] for k_bar in L[t]])
                        
                        if deno !=0:
                            for k in L[t]:
                                nume = r[u,k]/s_domain[k]
                                alpha_domain[t,u,k] = nume/deno*d_tu[t][u]
                        else:
                            for k in L[t]:
                                alpha_domain[t,u,k] = 0  # If denominator = 0 then all associated alphas = 0

        alpha = alpha_network + alpha_domain
        
        return alpha
    

    def _formula_2(self):
        """
        Tính theo công thức đều theo ngày ez của a Phong
        """

        K = self.K
        U = self.U
        T = self.T
        r = self.r
        D = self.D
        G = self.G
        CTR = self.CTR
        d = self.d
        w = self.w
        L = self.L
        B = self.B       
        t_0 = self.t_0
        ratio = self.ratio
        priority = self.priority
        share_type = self.share_type     
        cl = self.cl          
        w = self.w 

        # Calculate d_tu: lượng yêu cầu chạy theo ngày của từng campaign
        #d_tu = [d[t]*w[t]/(np.sum(w[t])) for t in range(T)] 
        d_tu = [self._calculate_d_t_u(d[t],w[t]) for t in range(T)]
        d_tu = np.nan_to_num(d_tu)  # Chuyển những thằng nan về 0, có thể không cần

        alpha =np.zeros((T,U,K))
        for t in range(T):
            for u in range(D[t][0],D[t][1]+1):
                for k in L[t]:
                    deno = np.sum([r[u,k_bar] for k_bar in L[t]])
                    if deno ==0:
                        alpha[t,u,k] == 0
                    else: 
                        alpha[t,u,k] = d_tu[t][u]*r[u,k]/deno
                    
        return alpha
    
    
    def _formula_3(self):
        """
        Tính theo công thức đều theo ngày ez của a Phong, nhưng:
        Việc tinh alpha của các campaign cấp B phải xét xem 
        ngày địa điểm đó có bị chiếm bởi campagin cấp C hay không.

        """

        K = self.K
        U = self.U
        T = self.T
        r = self.r
        D = self.D
        G = self.G
        CTR = self.CTR
        d = self.d
        w = self.w
        L = self.L
        B = self.B       
        t_0 = self.t_0
        ratio = self.ratio
        priority = self.priority
        share_type = self.share_type        
        cl = self.cl          
        w = self.w 
        # Compute cl
        cl = np.zeros([T,U,K])
        for t in range(T):
            if priority[t] == "CLASS_C":
                for u in range(D[t][0], D[t][1]+1):
                    for k in L[t]:
                        cl[t,u,k] = 1
        
        # Compute have_c
        have_c_network = np.zeros([U,K])
        have_c_domain = np.zeros([U,K])
        for u in range(U):
            for k in range(K):
                have_c_network[u,k] = np.sum([cl[t,u,k] for t in range(len(cl[:,u,k])) if t <t_0])
                have_c_domain[u,k] = np.sum([cl[t,u,k] for t in range(len(cl[:,u,k])) if t >= t_0])

        # Calculate d_tu: lượng yêu cầu chạy theo ngày của từng campaign
        d_tu = [self._calculate_d_t_u(d[t],w[t]) for t in range(T)]
        d_tu = np.nan_to_num(d_tu)  # Chuyển những thằng nan về 0, có thể không cần

        alpha =np.zeros((T,U,K))

        for t in range(t_0):
            for u in range(D[t][0],D[t][1]+1):
                for k in L[t] :
                    if have_c_network[u,k] == 0:
                        deno = np.sum([r[u,k_bar] for k_bar in L[t] if have_c_network[u,k_bar] == 0])
                        if deno ==0:
                            alpha[t,u,k] == 0
                        else: 
                            alpha[t,u,k] = d_tu[t][u]*r[u,k]/deno
                            
        for t in range(t_0, T):
            for u in range(D[t][0],D[t][1]+1):
                for k in L[t] :
                    if have_c_domain[u,k] == 0:
                        deno = np.sum([r[u,k_bar] for k_bar in L[t] if have_c_domain[u,k_bar] == 0])
                        if deno ==0:
                            alpha[t,u,k] == 0
                        else: 
                            alpha[t,u,k] = d_tu[t][u]*r[u,k]/deno

        return alpha

    def _calculate_d_t_u(self,d,w):
        """TÍnh d_t_u tức lượng view mong muốn chạy của campaign từng ngày

        Parameters
        ----------
        d : int
            Tổng lượng view mong muốn chạy của campaign
        w : np.array()
            mảng chưa trọng số theo từng ngày của campaign, w[i] là trọng số ngày i

        Returns
        -------
        d_t_u:np.array
            mảng lượng view mong muốn từng ngày d_t_u[u] là lượng chạy mong muốn ngày u
        """

        total_w = np.sum(w)
        if total_w == 0:
            d_t_u = np.zeros_like(w)
            return d_t_u

        d_t_u = d*w / total_w
        return d_t_u