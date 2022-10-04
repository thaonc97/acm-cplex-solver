from cplex_model.paper_model import PaperModel
from generated_protobuf.acm_cplex_solver_pb2 import ACSModel, ACSParameter, ACSSolveRequest

import numpy as np
import string

class Converter:


    @staticmethod
    def convert_grpc_message_to_model(acs_model : ACSModel, alpha_formula: int = 3) -> PaperModel:

        
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
        
        t_0 = max([campaign.id for campaign in campaigns_class_b_c if campaign.is_network == True], default=0)+1 # id campaign domain đầu tiên
        
        
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

        paper_model = PaperModel(T, U, K, r, D, G, CTR, d, L, t_0, share_rate, priority, share_type, B, cl, w)

        return paper_model
   