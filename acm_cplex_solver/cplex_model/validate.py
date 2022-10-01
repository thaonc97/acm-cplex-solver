from datetime import date
import numpy as np
from acm_cplex_solver.generated_protobuf.acm_cplex_solver_pb2 import ACSModel
from acm_cplex_solver.generated_protobuf.acm_base_pb2 import CampaignPriority
from acm_cplex_solver.utils.utils import Utils

class Validator:

        
    @staticmethod
    def validate_model(acs_model: ACSModel):
        campaigns_class_b_c = acs_model.campaigns_class_b_c
        campaigns_class_a = acs_model.campaigns_class_a
        places = acs_model.places

        # duplicate place id
        if(Utils.check_duplicate([place.id for place in places])):
            raise Exception("Có place id trùng nhau")

        # pace id liên tục từ 0
        check_continuous, K = Utils.check_continuous_list([place.id for place in places])
        if(check_continuous!=False):
            raise Exception("Mảng rỗng hoặc chỉ số id của place không liên tục và bắt đầu từ 0")
        

        # duplicate campaign id
        all_campaigns = [campaign for campaign in campaigns_class_b_c] + [campaign for campaign in campaigns_class_a]
        if(Utils.check_duplicate([campaign.id for campaign in all_campaigns])):
            raise Exception("Có campaign id trùng nhau")
        

        # total B>=0
        if min([campaign.total for campaign in campaigns_class_b_c if campaign.priority==CampaignPriority.CLASS_B], default=0)<0:
            raise Exception("Có campaign cấp B có total < 0")

        # id campaign_b_c từ 0-> t0-1 là network và liên tục
        check_continuous, t_0 = Utils.check_continuous_list([campaign.id for campaign in campaigns_class_b_c if campaign.is_network==True])
        if(check_continuous==1):
            raise Exception("Chỉ số id của campaign network cấp B,C không liên tục và bắt đầu từ 0")
        
        # id campaign_b_c từ t0-> T-1 là domain và liên tục
        is_continuous, T = Utils.check_continuous_list([campaign.id for campaign in campaigns_class_b_c if campaign.is_network==False], t_0)
        if(check_continuous==1):
            raise Exception("Chỉ số id của campaign domain cấp B,C không liên tục và bắt đầu từ t_0")

        # Kiểm tra campaign dates phải có 2 phần tử [fromDate, toDate], fromDate<=toDate
        D = [campaign.dates for campaign in all_campaigns]
        for dates in D:
            if(len(dates)!=2 or dates[0]>dates[1]):
                raise Exception("Tồn tại campaign có dates không phù hợp.")

        U = np.max(np.array(D)[:,1]) - np.min(np.array(D)[:,0]) +1

        for campaign in all_campaigns:
            for weight in campaign.weights:
                if(weight.weight<0):
                    raise Exception("campaign " +str(campaign.id) + " có weight nhỏ hơn 0")
                if(weight.date>U):
                    raise Exception("campaign " +str(campaign.id) + " weight có date nằm ngoài chỉ số")
            
            if(Utils.check_duplicate(campaign.place_ids)):
                raise Exception("Campaign "+ str(campaign.id) + " có place_ids trùng nhau")
            if(max(campaign.place_ids)>K or min(campaign.place_ids) < 0):
                raise Exception("Campaign "+ str(campaign.id) + " có place_id không thuộc khoảng 0->" + str(K-1))


        max_campaign_type = max([campaign.type for campaign in all_campaigns])+1
        for place in places:
            if(len(place.ctrs)<max_campaign_type):
                raise Exception("Địa điểm "+ str(place.id) + " không có đủ "+ str(max_campaign_type) + " loại ctr")

            if(len([view for view in place.views if view<0])>0):
                raise Exception("Địa điểm "+ str(place.id) + " có view < 0")

            if(len(place.views) != U):
                raise Exception("Lượt view của "+ str(place.id) + " không đủ " + U + " ngày")
            
            if(place.share_rate <0 or place.share_rate >1):
                raise Exception("Địa điểm "+ str(place.id) + " có share_rate không thuộc khoảng [0,1]")

            if(len([ctr for ctr in place.ctrs if ctr<0 or ctr>1])>0):
                raise Exception("Địa điểm "+ str(place.id) + " có ctr không thuộc khoảng [0,1]")

        
        



        


""" Validate


class_a 
index_continous_check(class_a, T) >= T, kiểm tra xem có cần check liên tục ko ?




- places
len(ctrs) >= max(campaigns.type), campaign


,  """