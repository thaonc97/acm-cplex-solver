from typing import List
import numpy as np
import pandas as pd
from cplex_model.class_a_model import ClassAModel
from cplex_model.paper_model import PaperModel

class ClassASolver():

    @staticmethod
    def _convert(solve_details, paper_model : PaperModel) ->   List[List[ClassAModel]]:
        """_summary_

        Args:
            solve_details (_type_): _description_
            paper_model (PaperModel): _description_

        Returns:
            ndarray: n[u][k] = ClassAModel của ngày u, địa điểm k
        """
        t_0 = PaperModel.t_0
        docplex_sol = solve_details['solution']
        x_dict = solve_details['x_dict']
        x_a_dict = solve_details['x_a_dict']
        df_x_a = docplex_sol.get_value_df(x_a_dict, 'x_a', ['date','place_id'])  # Data Frame of x_a
        if x_dict:
            df_b_c = docplex_sol.get_value_df(x_dict, key_column_names=['campaign_id', 'date', 'place_id'])
        df_x_a = docplex_sol.get_value_df(x_a_dict, 'x_a', ['date','place_id'])

        df_b_c_nw = df_b_c[df_b_c['campaign_id'] <t_0]
        df_b_c_nw_grouped = df_b_c_nw.groupby(['date','place_id']).agg({"value":"sum"}).reset_index()
        total_b_c_nw ={
            (date, place): view for date,place,view in zip(
                df_b_c_nw_grouped['date'], 
                df_b_c_nw_grouped['place_id'],
                df_b_c_nw_grouped['value']) 
        }
        df_b_c_domain = df_b_c[df_b_c['campaign_id'] >=t_0]
        df_b_c_domain_grouped = df_b_c_domain.groupby(['date','place_id']).agg({"value":"sum"}).reset_index()
        total_b_c_domain ={
            (date, place): view for date,place,view in zip(
                df_b_c_domain_grouped['date'], 
                df_b_c_domain_grouped['place_id'],
                df_b_c_nw_grouped['value'] ) 
        }
        x_a = {
            (date,place): view for date,place,view in zip(df_x_a['date'], df_x_a['place'], df_x_a['value'])
        }
        U = PaperModel.U
        K = PaperModel.K
        
        class_a_models = []
        for u in range(U):
            cur_u_class_a_models = []
            for k in range(K):
                r = paper_model.r[u.k]
                ratio =paper_model.ratio[k]
                total_network_left = r*ratio - total_b_c_nw[(u,k)]  
                total_domain_left = r*(1-ratio) - total_b_c_domain[(u,k)]
                x_a = x_a[(u,k)]
                class_a_model = ClassAModel()
                class_a_model.r = r
                class_a_model.ratio = ratio
                class_a_model.total_network_lefts = total_network_left
                class_a_model.total_domain_lefts = total_domain_left
                cur_u_class_a_models.append(class_a_model)
            class_a_models.append(cur_u_class_a_models)

        return class_a_models
    
    @staticmethod
    def _get_running_a(classes_a :List[List[ClassAModel]], a_resources): 
        """Thêm thông tin về các campaign cấp A network, domain chạy vào các ClassA

        Args:
            class_a (_type_): danh sách class a
            resources (_type_): mảng 2 chiều chứa ClassAModel tại ngày u, địa điểm k
        """
        for date in range(len(classes_a)):
            for place in range(len(date)):
                cur_class_a_campaigs_network = []
                cur_class_a_campaigns_domain = []
                for campaign in a_resources:
                    weights = {
                        weight_info.date:weight_info.weight for weight_info in campaign.weights
                    }
                    if place in campaign.place_ids and date in range (campaign.dates[0],campaign.dates[1] + 1):
                        if campaign.is_network == True and not (str(date) in campaign.weights and campaign['weights'][str(date)] == 0):
                            cur_class_a_campaigs_network.append(campaign.id)
                        if campaign.is_network == False and not (str(date) in campaign['weights'] and campaign['weights'][str(date)] == 0):
                            cur_class_a_campaigns_domain.append(campaign.id)
                classes_a[date][place].campaigns_network = cur_class_a_campaigs_network
                classes_a[date][place].campaigns_domain = cur_class_a_campaigns_domain

    def _solve(class_a):
        sol_campaigns_a = []
        for place in class_a:
            U,K = class_a.r.shape
            for u in range(U):
                for k in range(K):
                    num_a_network = len(class_a.campaigns_a_network[u][k])
                    num_a_domain  = len(class_a.campaigns_a_domain[u][k])
                    if num_a_network != 0 and num_a_domain == 0:
                        for t in class_a.campaigns_a_network[u][k]:
                            sol_campaigns_a = ClassASolver._append_class_a(sol_campaigns_a,t, u, k, class_a.total_network_lefts[u][k]/num_a_network)
                    elif num_a_network == 0 and num_a_domain != 0:
                        for t in class_a.campaigns_a_domain[u][k]:
                            sol_campaigns_a = ClassASolver._append_class_a(sol_campaigns_a,t, u, k, class_a.total_domain_lefts[u][k]/num_a_network)
                    elif num_a_network !=0 and num_a_domain !=0:
                        for t in class_a.campaigns_a_network[u][k]:
                            sol_campaigns_a = ClassASolver._append_class_a(sol_campaigns_a,t, u, k, class_a.r[u][k]/num_a_network)
                        for t in class_a.campaigns_a_domain[u][k]:
                            sol_campaigns_a = ClassASolver._append_class_a(sol_campaigns_a,t, u, k, class_a.r[u][k]/num_a_network)
                    elif num_a_network == 0 and num_a_domain == 0:
                        sol_campaigns_a = ProcessClassA._append_class_a(sol_campaigns_a, -1, u, k, class_a.total_network_lefts[u][k] + class_a.total_network_lefts[u][k])
        
        return sol_campaigns_a

    @staticmethod
    def _append_class_a(sol_campaigns_a, campaign_id, solve_place_id, date, value):
        """
        Append class a campaigns to a dict
        """
        sol_campaigns_a.append({
            'campaign_id' : campaign_id,
            'date': date,
            'place_id':solve_place_id,
            'value': value
        })

    def solve(solve_details, paper_model, resource):
        classes_a = ClassASolver._convert(solve_details, paper_model)
        classed_a_added_campaigns = ClassASolver._get_running_a(classes_a, resource)
        class_a_result = ClassASolver._solve(classed_a_added_campaigns, resource)
        return class_a_result
    

class ProcessClassA:
    
    @staticmethod
    def _get_leftover_details(df_sol_b_c, df_x_a, preprocessed_data):
        """
        Trả về 1 dataframe chi tiết về lượng thừa của campaign, place

        Parameters
        ----------
        df_sol_b_c: pandas.DataFrame
            output sau khi chạy solve_single_model
        df_x_a: pandas.DataFrame
        preprocessed_data: preprocessed data
        
        Returns
        -------
        df_leftovers_details: pandas.DataFrame
            dataframe chi tiết về lượng thừa domain, network, tổng lượng chạy campaign
            class A tại từng địa điểm từng ngày có campaign class A
        """
        share_rate = preprocessed_data.places['share_rate'].to_numpy()
        r = np.stack([views_each_place for views_each_place in preprocessed_data.places['views']])
        r = r.T
        t_0 = preprocessed_data.t_0

        df_sol_b_c_network = df_sol_b_c[df_sol_b_c['campaign_id'] <t_0]
        df_sol_b_c_network_grouped = df_sol_b_c_network.groupby(['date','solve_place_id']).agg({"value":"sum"}).reset_index()
        df_sol_b_c_network_grouped = df_sol_b_c_network_grouped.rename(columns = {"value":"value_network"},errors = 'ignore')

        df_sol_b_c_domain = df_sol_b_c[df_sol_b_c['campaign_id'] >=t_0]
        df_sol_b_c_domain_grouped = df_sol_b_c_domain.groupby(['date','solve_place_id']).agg({"value":"sum"}).reset_index()
        df_sol_b_c_domain_grouped = df_sol_b_c_domain_grouped.rename(columns = {"value":"value_domain"},errors = 'ignore')

        estimate_views_network =  r*share_rate
        estimate_views_domain = r*(1 - np.array(share_rate))
        
        df_sol_b_c_grouped = pd.merge(df_sol_b_c_network_grouped,df_sol_b_c_domain_grouped, how = 'outer', on = ['date','solve_place_id'],sort = True)
        df_sol_b_c_grouped= df_sol_b_c_grouped.fillna(0)
        df_sol_b_c_grouped['network_leftovers'] = estimate_views_network.reshape(-1) - df_sol_b_c_grouped['value_network']
        df_sol_b_c_grouped['domain_leftovers'] = estimate_views_domain.reshape(-1) - df_sol_b_c_grouped['value_domain']
        
        df_leftovers_details = pd.merge(df_sol_b_c_grouped, df_x_a, on=['date','solve_place_id'])

        return df_leftovers_details

    @staticmethod
    def _add_campaigns_details_to_df(df_leftovers_details,preprocessed_data):
        """
        Thêm trường series_campaign_network_a_solve_ids, series_campaign_domain_a_solve_ids vào df leftovers để biết ngày và địa điêm đấy có
        campaign loại a network và campaign loại a domain nào chạy
        """
        preprocessed_campaigns_a = preprocessed_data.campaigns.loc[preprocessed_data.campaigns['priority'] == 'CLASS_A']
        preprocessed_campaigns_a_dict = preprocessed_campaigns_a.to_dict('records')

        series_campaign_network_a_solve_ids = []
        series_campaign_domain_a_solve_ids = []

        for date,solve_place_id in zip(df_leftovers_details['date'],df_leftovers_details['solve_place_id']):
            campaign_network_a_solve_ids = []
            campaign_domain_a_solve_ids = []
            # df_leftovers_details
            for campaign in preprocessed_campaigns_a_dict:
                if solve_place_id in campaign['solve_place_ids'] and date in range (campaign['dates'][0],campaign['dates'][1] +1):
                    if campaign['isNetwork'] == True and not (str(date) in campaign['weights'] and campaign['weights'][str(date)] == 0):
                        campaign_network_a_solve_ids.append(campaign['solve_id'])
                    if campaign['isNetwork'] == False and not (str(date) in campaign['weights'] and campaign['weights'][str(date)] == 0):
                        campaign_domain_a_solve_ids.append(campaign['solve_id'])

            series_campaign_network_a_solve_ids.append(campaign_network_a_solve_ids)
            series_campaign_domain_a_solve_ids.append(campaign_domain_a_solve_ids)

        df_leftovers_details['campaign_network_a_solve_ids'] = series_campaign_network_a_solve_ids
        df_leftovers_details['campaign_domain_a_solve_ids'] = series_campaign_domain_a_solve_ids

        return df_leftovers_details

    @staticmethod
    def _compute_class_a(df_leftovers_details):
        """
        Tính toán lượng view chi tiết mỗi ngày địa điểm.
        """
        df_leftovers_details_non_zero = df_leftovers_details[df_leftovers_details['x_a'] > 10**-6]  #'dates-places has x_a != 0'
        df_leftovers_details_only_zero = df_leftovers_details[df_leftovers_details['x_a'] <= 10**-6]  # 'dates-places has x_a  = 0'
        
        leftovers_details_non_zero_dict = df_leftovers_details_non_zero.to_dict('records')
        leftovers_details_only_zero_dict = df_leftovers_details_only_zero.to_dict('records')
        sol_campaigns_a = []
        
        for date_place in leftovers_details_non_zero_dict :  # When  x_a >0
            num_class_a_networks = len(date_place['campaign_network_a_solve_ids'])
            num_class_a_domains = len(date_place['campaign_domain_a_solve_ids'])
            if num_class_a_networks != 0 and num_class_a_domains == 0:  # campaigns class A network only
                for campaign_id in date_place['campaign_network_a_solve_ids']:
                    sol_campaigns_a = ProcessClassA._append_class_a(sol_campaigns_a, campaign_id, date_place['solve_place_id'], date_place['date'], date_place['x_a']/num_class_a_networks)

            elif num_class_a_domains != 0 and num_class_a_networks == 0:  # campaigns class A domain only
                for campaign_id in date_place['campaign_domain_a_solve_ids']:
                    sol_campaigns_a = ProcessClassA._append_class_a(sol_campaigns_a, campaign_id, date_place['solve_place_id'], date_place['date'], date_place['x_a']/num_class_a_domains)

            elif num_class_a_domains != 0 and num_class_a_networks != 0:  # both class A network and domain
                if date_place['domain_leftovers'] >=10**-6 and date_place['network_leftovers'] >= 10**-6:  # Both domain and network still have resources
                    for campaign_id in date_place['campaign_domain_a_solve_ids']:
                        sol_campaigns_a = ProcessClassA._append_class_a(sol_campaigns_a, 
                                                                        campaign_id, 
                                                                        date_place['solve_place_id'], 
                                                                        date_place['date'], 
                                                                        date_place['domain_leftovers']/num_class_a_domains)

                    for campaign_id in date_place['campaign_network_a_solve_ids']:
                        sol_campaigns_a = ProcessClassA._append_class_a(sol_campaigns_a, 
                                                                        campaign_id, 
                                                                        date_place['solve_place_id'], 
                                                                        date_place['date'], 
                                                                        date_place['network_leftovers']/num_class_a_networks)

                if date_place['domain_leftovers'] >=10**-6 and date_place['network_leftovers'] <= 10**-6:  # Only domain has resources
                    for campaign_id in date_place['campaign_domain_a_solve_ids']:
                        sol_campaigns_a = ProcessClassA._append_class_a(sol_campaigns_a, campaign_id, date_place['solve_place_id'], date_place['date'], date_place['x_a']/num_class_a_domains)
                        
                if date_place['domain_leftovers'] <= 10**-6 and date_place['network_leftovers'] > 10**-6: # Only network has resources
                    for campaign_id in date_place['campaign_network_a_solve_ids']:
                        sol_campaigns_a = ProcessClassA._append_class_a(sol_campaigns_a, campaign_id, date_place['solve_place_id'], date_place['date'], date_place['x_a']/num_class_a_networks)
                        
            elif num_class_a_domains == 0 and num_class_a_networks == 0:
                sol_campaigns_a = ProcessClassA._append_class_a(sol_campaigns_a, "-1", date_place['solve_place_id'], date_place['date'], date_place['x_a'])
        
        for date_place in leftovers_details_only_zero_dict:  # when xA = 0 
            if len(date_place['campaign_domain_a_solve_ids']) >0:  # have campaign domain type A
                for campaign_id in date_place['campaign_domain_a_solve_ids']:
                    sol_campaigns_a = ProcessClassA._append_class_a(sol_campaigns_a, campaign_id, date_place['solve_place_id'], date_place['date'], 0)
            
            if len(date_place['campaign_network_a_solve_ids']) >0:  # have campaign network type A
                for campaign_id in date_place['campaign_network_a_solve_ids']:
                    sol_campaigns_a = ProcessClassA._append_class_a(sol_campaigns_a, campaign_id, date_place['solve_place_id'], date_place['date'], 0)

        
        return pd.DataFrame(sol_campaigns_a)

    @staticmethod
    def _append_class_a(sol_campaigns_a, campaign_id, solve_place_id, date, value):
        """
        Append class a campaigns to a dict. Used in ProcessClassA._compute_class_a
        """
        sol_campaigns_a.append({
            'campaign_id' : campaign_id,
            'solve_place_id':solve_place_id,
            'date': date,
            'value': value
        })
        
        return sol_campaigns_a

    @staticmethod
    def process_class_a(df_sol_b_c, df_x_a, preprocessed_data):
        """
        Main function to run. Process class a .

        Parameters
        ----------
            df_sol_b_c: pd.DataFrame
            Dataframe solution of all campaigns in class b and c
            df_x_a: pd.DataFrame
            Dataframe of x_a (leftovers after campaigns b,c ran) in each place-day. 

        Returns
        -------
            class_a_soltion: pd.DataFrame
            Dataframe of solution of all campaigns class A.
        """
        df_leftovers_details = ProcessClassA._get_leftover_details(df_sol_b_c, df_x_a, preprocessed_data)
        df_leftovers_details = ProcessClassA._add_campaigns_details_to_df(df_leftovers_details, preprocessed_data)
        class_a_solution = ProcessClassA._compute_class_a(df_leftovers_details)
        return class_a_solution