from copy import deepcopy
from typing import List, Tuple
from acm_cplex_solver.cplex_model.class_a_model_solver import ClassAModelSolver
from acm_cplex_solver.cplex_model.validate import Validator
from acm_cplex_solver.generated_protobuf.acm_cplex_solver_pb2 import ACSCampaign
from cplex_model.paper_model import PaperModel
from generated_protobuf.acm_cplex_solver_pb2 import ACSModel, ACSParameter, ACSSolveRequest

import numpy as np

class Converter:


    @staticmethod
    def convert_grpc_message_to_model(acs_model : ACSModel, alpha_formula: int) -> PaperModel:

        
        Validator.validate_model(acs_model)
        
        places = acs_model.places
        campaigns_class_b_c = acs_model.campaigns_class_b_c 
        campaigns_class_a = acs_model.campaigns_class_a

        share_rate = [place.share_rate for place in places]
        D = [campaign.dates for campaign in campaigns_class_b_c] + [campaign.dates for campaign in campaigns_class_a]
        #U = np.max(np.array(D)[:,1]) - np.min(np.array(D)[:,0]) +1 
        U = len(places[0].views) # tất cả các place có cùng số ngày views = U
        
        L = [np.array(campaign.place_ids) for campaign in campaigns_class_b_c] 

        T = len(campaigns_class_b_c)
        K = len(places)

        d = [campaign.total for campaign in campaigns_class_b_c]
        priority = [campaign.priority for campaign in campaigns_class_b_c]
        r_ku = [place.views for place in places]
        r =np.array(r_ku).T #Transpose r_ku to get r_uk
                
        t_0 = min([campaign.id for campaign in campaigns_class_b_c if campaign.is_network == False], default=T) 
        # id campaign domain đầu tiên, nếu campaign domain rỗng thì = T
        
        
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

        paper_model = PaperModel(T, U, K, r, D, G, CTR, d, L, t_0, share_rate, priority, share_type, B, cl, w, alpha_formula)

        return paper_model

    
    @staticmethod
    def convert_solve_details_to_class_a_model(
        solve_details, paper_model : PaperModel, campaigns_class_a : List[ACSCampaign]) -> ClassAModelSolver: 
        
        t_0 = paper_model.t_0
        U = paper_model.U
        K = paper_model.K
        docplex_sol = solve_details['solution']
        x_dict = solve_details['x_dict']
      
        if x_dict:
            df_b_c = docplex_sol.get_value_df(x_dict, key_column_names=['campaign_id', 'date', 'place_id'])
      

        df_b_c_nw = df_b_c[df_b_c['campaign_id'] <t_0]
        df_b_c_nw_grouped = df_b_c_nw.groupby(['date','place_id']).agg({"value":"sum"}).reset_index()
        total_networks = df_b_c_nw_grouped["value"].to_numpy().reshape([U,K])

        df_b_c_domain = df_b_c[df_b_c['campaign_id'] >=t_0]
        df_b_c_domain_grouped = df_b_c_domain.groupby(['date','place_id']).agg({"value":"sum"}).reset_index()
        
        total_domains = df_b_c_domain_grouped["value"].to_numpy().reshape([U,K])

        campaigns_class_a_network, campaigns_class_a_domain = Converter._get_running_a(U, K, campaigns_class_a)
        a_model = ClassAModelSolver(paper_model.r, paper_model.ratio, total_networks, total_domains, campaigns_class_a_network, campaigns_class_a_domain)
        

        return a_model
    
    @staticmethod
    def _get_running_a(U : int, K: int, campaigns_class_a : List[ACSCampaign]): 
        
        campaigns_class_a_network = []

        for u in range(U):
            empty_list_u = []
            for k in range(K):
                empty_list_u.append([])            
            campaigns_class_a_network.append(empty_list_u)

        campaigns_class_a_domain = deepcopy(campaigns_class_a_network)

        # add campaign.id vào ngày u, địa điểm k nếu campaign có chạy qua ngày u, địa điểm k, và date có weight>0 
        for campaign in campaigns_class_a:
            for u in range(campaign.dates[0], campaign.dates[1]+1):
                for k in campaign.place_ids:
                    for weight in campaign.weights:
                        if(weight.weight > 0):
                            if(campaign.is_network == True):
                                campaigns_class_a_network[u][k].append(campaign.id)
                            else:
                                campaigns_class_a_domain[u][k].append(campaign.id)
        
        
        return campaigns_class_a_network, campaigns_class_a_domain