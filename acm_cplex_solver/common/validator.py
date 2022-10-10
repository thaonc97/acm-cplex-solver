import numpy as np
from generated_protobuf.acm_cplex_solver_pb2 import ACSModel
from generated_protobuf.acm_base_pb2 import CampaignPriority
from .utils import Utils

class Validator:

        
    @staticmethod
    def validate_model(acs_model: ACSModel):
        campaigns_class_b_c = acs_model.campaigns_class_b_c
        campaigns_class_a = acs_model.campaigns_class_a
        places = acs_model.places

        # pace id liên tục từ 0, không cần check dulicate do liên tục là đã đảm bảo ko duplicate
        check_continuous, K = Utils.check_continuous_list([place.id for place in places])
        if(check_continuous!=0):
            raise Exception("Mảng rỗng hoặc chỉ số id của place không liên tục và bắt đầu từ 0")

        U = len(places[0].views)
        if(U==0):
            raise Exception("Địa điểm 0 không có thông tin lượt views")
       

        # U = np.max(np.array(D)[:,1]) - np.min(np.array(D)[:,0]) +1

        if(len([campaign for campaign in campaigns_class_b_c if campaign.priority==CampaignPriority.CLASS_A])>0):
            raise Exception("Có campaign cấp A trong campaigns_class_b_c")

        if(len([campaign for campaign in campaigns_class_a if campaign.priority!=CampaignPriority.CLASS_A])>0):
            raise Exception("Có campaign khác cấp A trong campaigns_class_a")

        # total B>=0
        if min([campaign.total for campaign in campaigns_class_b_c if campaign.priority==CampaignPriority.CLASS_B], default=0)<0:
            raise Exception("Có campaign cấp B có total < 0")

        # id campaign_b_c từ 0-> t0-1 là network và liên tục
        check_continuous, t_0 = Utils.check_continuous_list([campaign.id for campaign in campaigns_class_b_c if campaign.is_network==True])
        if(check_continuous==1):
            raise Exception("Chỉ số id của campaign network cấp B,C không liên tục và bắt đầu từ 0")
        
        # id campaign_b_c từ t0-> T-1 là domain và liên tục
        check_continuous, T = Utils.check_continuous_list([campaign.id for campaign in campaigns_class_b_c if campaign.is_network==False], t_0)
        if(check_continuous==1):
            raise Exception("Chỉ số id của campaign domain cấp B,C không liên tục và bắt đầu từ " + str(t_0))

        all_campaigns = [campaign for campaign in campaigns_class_b_c] + [campaign for campaign in campaigns_class_a]

        # id tất cả campaign không trùng
        is_duplicate = Utils.check_duplicate([campaign.id for campaign in all_campaigns])
        if(is_duplicate==True):
            raise Exception("Các campaign a,b,c có id trùng nhau.")

        

        for campaign in all_campaigns:
            # Kiểm tra campaign dates phải có 2 phần tử [fromDate, toDate], fromDate<=toDate, toDate<U     
            if(len(campaign.dates)!=2 or campaign.dates[0]>campaign.dates[1] or campaign.dates[1]>=U):
                raise Exception("Campaign " + str(campaign.id) + " có dates không phù hợp.")

            # kiểm tra trọng số phải >=0, 0<= date <U     
            for weight in campaign.weights:
                if(weight.weight<0):
                    raise Exception("Campaign " +str(campaign.id) + " có weight nhỏ hơn 0")
                if(weight.date>=U):
                    raise Exception("Campaign " +str(campaign.id) + " weight có date>=" + str(U))
            
            if(Utils.check_duplicate(campaign.place_ids)):
                raise Exception("Campaign "+ str(campaign.id) + " có place_ids trùng nhau")
            if(max(campaign.place_ids, default=K)>=K or min(campaign.place_ids) < 0):
                raise Exception("Campaign "+ str(campaign.id) + " có place_ids rỗng hoặc không thuộc khoảng 0->" + str(K-1))


        max_campaign_type = max([campaign.type for campaign in all_campaigns], default=0)+1
        for place in places:
            if(len(place.ctrs)<max_campaign_type):
                raise Exception("Địa điểm "+ str(place.id) + " không có đủ "+ str(max_campaign_type) + " loại ctr")

            if(len([ctr for ctr in place.ctrs if ctr<0 or ctr>1])>0):
                raise Exception("Địa điểm "+ str(place.id) + " có ctr không thuộc khoảng [0,1]")

            if(place.share_rate <0 or place.share_rate >1):
                raise Exception("Địa điểm "+ str(place.id) + " có share_rate không thuộc khoảng [0,1]")

            if(len([view for view in place.views if view<0])>0):
                raise Exception("Địa điểm "+ str(place.id) + " có view < 0")

            if(len(place.views) != U):
                raise Exception("Lượt view của địa điểm "+ str(place.id) + " khác " + str(U) + " ngày")
            
            

            
