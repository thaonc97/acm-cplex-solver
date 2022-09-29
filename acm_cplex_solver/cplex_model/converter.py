from acm_cplex_solver.cplex_model.alpha_calculator import AlphaCalculator
from acm_cplex_solver.cplex_model.paper_model import PaperModel
from acm_cplex_solver.cplex_model.solver_parameter import SolverParameter
from acm_cplex_solver.cplex_model.validate import Validator
from acm_cplex_solver.generated_protobuf.acm_cplex_solver_pb2 import ACSModel, ACSOption, ACSParameter, ACSSolveRequest

import numpy as np
import string

class Converter:

    @staticmethod
    def convert_grpc_parameter_to_parameter(acs_parameter : ACSParameter) -> SolverParameter:
        return SolverParameter()

    
    @staticmethod
    def convert_grpc_option_to_option(acs_option : ACSOption):
        pass # TODO


    @staticmethod
    def convert_grpc_message_to_model(acs_model : ACSModel) -> PaperModel:

        
        places = acs_model.places
        campaigns_class_b_c = acs_model.campaigns_class_b_c 
        campaigns_class_a = acs_model.campaigns_class_a

        share_rate = [place.share_rate for place in places]
        D = [campaign.dates for campaign in campaigns_class_b_c] + [campaign.dates for campaign in campaigns_class_a]
        U = np.max(np.array(D)[:,1]) - np.min(np.array(D)[:,0]) +1 
        
        L = [np.array(campaign.place_ids) for campaign in campaigns_class_b_c] 

        T = len(campaigns_class_b_c)
        K = len(places)

        d = [campaign.total for campaign in campaigns_class_b_c]
        priority = [campaign.priority for campaign in campaigns_class_b_c]
        r_ku = [place.views for place in places]
        r =np.array(r_ku).T #Transpose r_ku to get r_uk
        
        t_0 = min([campaign.id for campaign in campaigns_class_b_c if campaign.is_network == False]) # id campaign domain đầu tiên
        
        G = [campaign.group_id for campaign in campaigns_class_b_c]
        #[g if not (np.isnan(g)) else None for group in groups]

        
        CTR_percent_k = [place.ctrs for place in places]
        CTR_t = [campaign.type for campaign in campaigns_class_b_c]
        CTR = np .zeros((T,K)) #CTR_t_k
        for t in range(T):
            CTR[t] = [CTR_percent_k[k][CTR_t[t]] for k in range(K)]

        try:
            share_type = [place.share_type for place in places] # sharetype
        except:
            print("Có vẻ dữ liệu cũ chưa có share type, đặt toàn bộ là soft")
            share_type = [0 for _ in range(K)]
        
        #Generate B_k
        B =[]
        for i in range(K):
            current_place_campaign_list=[]
            for j in range(len(L)) :
                if i in L[j]:
                    current_place_campaign_list.append(j)
            B.append(current_place_campaign_list)

        #Calculate w
        weights = [campaign.weights for campaign in campaigns_class_b_c]
        w = np.zeros((T,U))
        
        for t in range(T):
            for u in range(D[t][0],D[t][1]+1):
                if str(u) in weights[t]:
                    w[t,u] = weights[t][str(u)]
                else:
                    w[t,u] = 10


        # Compute cl
        cl = np.zeros([T, U, K])
        for t in range(T):
            if priority[t] == "CLASS_C":
                for u in range(D[t][0], D[t][1]+1):
                    for k in L[t]:
                        cl[t, u, k] = 1

        paper_model = PaperModel() 
        paper_model.U = U
        paper_model.T = T
        paper_model.K = K
        paper_model.D = D
        paper_model.G = G
        paper_model.d = d
        paper_model.r = r
        paper_model.CTR = CTR
        paper_model.w = w
        paper_model.L = L
        paper_model.B = B
        paper_model.t_0 = t_0
        paper_model.priority = priority
        paper_model.share_type = share_type
        paper_model.share_rate = share_rate
        

        paper_model.cl = cl
        # Cập nhật lại trọng số
        paper_model.w = Converter._calculate_w(paper_model)

        return paper_model
   

    @staticmethod
    def _calculate_w(paper_model : PaperModel):
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
        T = paper_model.T
        t_0 = paper_model.t_0
        D = paper_model.D
        L = paper_model.L        
        priority = paper_model.priority

        w = paper_model.w.copy()
        # Compute have_c
        have_c_network = np.zeros([paper_model.U, paper_model.K])
        have_c_domain = np.zeros([paper_model.U, paper_model.K])
        for u in range(paper_model.U):
            for k in range(paper_model.K):
                have_c_network[u, k] = np.sum(
                    [paper_model.cl[t, u, k] for t in range(len(paper_model.cl[:, u, k])) if t < paper_model.t_0])
                have_c_domain[u, k] = np.sum(
                    [paper_model.cl[t, u, k] for t in range(len(paper_model.cl[:, u, k])) if t >= paper_model.t_0])    

        if 'CLASS_C' not in priority:
            return w  # Không cần tính toán thay đổi nếu ko có class C

        not_have_c_network = 1- have_c_network # Ma trận không có campaign c
        not_have_c_domain = 1 - have_c_domain

        for t in range(T):
            if priority[t] == 'CLASS_B':
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
        return w

    
    @staticmethod
    def calculate_alpha(paper_model : PaperModel, alpha_formula : string):
        alpha_calculator = AlphaCalculator(paper_model)
        return alpha_calculator.calculate(alpha_formula)