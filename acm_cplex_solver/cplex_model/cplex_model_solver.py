from common.converter import Converter
from cplex_model.paper_model import PaperModel
from cplex_model.solver_parameter import SolverParameter
from generated_protobuf.acm_cplex_solver_pb2 import ACSSolveMethod
import config
from generated_protobuf.acm_base_pb2 import CampaignPriority

#others
from docplex.mp.model import Model
import logging
import numpy as np



class CplexModelSolver: 
    
    EPSILON = 10**-6 

    def __init__(self, paper_model : PaperModel, parameter : SolverParameter):     
        self.paper_model = paper_model
        self.parameter = parameter


    def solve(self):
        methods = {
            ACSSolveMethod.SOLVE_TWO_STEPS : self._solve_b_c_2_steps,
            ACSSolveMethod.SOLVE_SOFT_CONSTRAINT: self._solve_b_c_soft
        }
        

        choosen_method = methods[self.parameter.method]        
        solve_result= choosen_method()
                            
        return solve_result
    
    
    def _solve_b_c_2_steps(self):
        """
        Sử dụng CPLEX để giải bài toán tối ưu 2 bước, không có biến nguyên, có cận dưới,
        mô hình sau này của a Phong.
        """
        step_1_solve_details = self._solve_step_1()  # Solve B,C

        step_2_solve_details = self._solve_step_2(step_1_solve_details)  # Solve B,C
        
        return step_2_solve_details

    def _solve_step_1(self):

        K = self.paper_model.K
        U = self.paper_model.U
        T = self.paper_model.T
        r = self.paper_model.r
        D = self.paper_model.D
        G = self.paper_model.G
        CTR = self.paper_model.CTR
        d = self.paper_model.d      
        L = self.paper_model.L
        B = self.paper_model.B       
        t_0 = self.paper_model.t_0
        ratio = self.paper_model.ratio
        priority = self.paper_model.priority
        share_type = self.paper_model.share_type        
        cl = self.paper_model.cl          
        w = self.paper_model.w       
        alpha = self.paper_model.alpha

              

        model = Model("Acm Solver 2 steps- Step 1")
        campaign_list = np.arange(T)
        t_u_k_set = [(t, u, k) for t in range(T)
                    for u in range(U) for k in range(K)]
        u_k_set = [(u, k) for u in range(U) for k in range(K)]
        x = model.continuous_var_dict(t_u_k_set, lb=0, name='x')
        z = model.continuous_var_dict(campaign_list, lb=-99999999, ub=0, name='z')

        model.add_constraints( 
            model.sum(model.sum((CTR[t_p,k]*x[t_p,u,k] 
                    for k in L[t_p] for u in range(D[t_p][0],D[t_p][1]+1) if w[t_p,u] !=0))
                    for t_p in range(T) if G[t_p]== G[t]) -z[t] == d[t] 
                    for t in range(T) if priority[t] == CampaignPriority.CLASS_B if G[t] is not None) #

        model.add_constraints(
            model.sum((CTR[t, k]*x[t, u, k]
                    for k in L[t] for u in range(D[t][0], D[t][1]+1) if w[t, u] != 0)) -z[t] == d[t] 
                    for t in range(T) if priority[t] == CampaignPriority.CLASS_B if G[t] is None)

        model.add_constraints(x[t_prime, u, k] == 0
                            for t in range(t_0) if priority[t] == CampaignPriority.CLASS_C
                            for u in range(D[t][0], D[t][1]+1) if w[t, u] != 0
                            for k in L[t] for t_prime in range(t_0) if t_prime != t)

        model.add_constraints(x[t_prime, u, k] == 0
                            for t in range(t_0, T) if priority[t] == CampaignPriority.CLASS_C
                            for u in range(D[t][0], D[t][1] + 1) if w[t, u] != 0
                            for k in L[t] for t_prime in range(t_0, T) if t_prime != t)

        model.add_constraints(
            model.sum(x[t, u, k] for t in range(t_0) if t in B[k]
                    and u in range(D[t][0], D[t][1]+1) and w[t, u] != 0)
            <= ratio[k]*r[u, k] for k in range(K) for u in range(U))  # Chặn cứng

        model.add_constraints(
            model.sum(x[t, u, k] for t in range(t_0, T) if t in B[k]
                    and u in range(D[t][0], D[t][1]+1) and w[t, u] != 0)
            <= (1-ratio[k])*r[u, k] for k in range(K) for u in range(U))  # Chặn cứng

        # Chặn dưới
        model.add_constraints(x[t,u,k] >= self.parameter.lower_ratio*alpha[t,u,k]*min(1, r[u,k]*ratio[k]/deno) 
            for t in range(t_0) if priority[t] == CampaignPriority.CLASS_B  
                for u in range(D[t][0],D[t][1]+1) 
                    for (deno,k) in ( (np.sum(alpha[:,u, k]),k) for k in L[t] if w[t,u] !=0 and CTR[t,k] !=0) if deno !=0)
        model.add_constraints(x[t,u,k] >= self.parameter.lower_ratio*alpha[t,u,k]*min(1, r[u,k]*(1-ratio[k])/deno) 
            for t in range(t_0, T) if priority[t] == CampaignPriority.CLASS_B 
                for u in range(D[t][0],D[t][1]+1) 
                    for (deno,k) in ( (np.sum(alpha[:,u, k]),k) for k in L[t] if w[t,u] !=0 and CTR[t,k] !=0) if deno !=0)

        opt_func_even = model.sum(
                model.sum(
                    model.sum(
                        1/(alpha[t,u,k]+self.EPSILON)**1*((1-cl[t,u,k])*x[t,u,k]*CTR[t,k]-alpha[t,u,k])**2 + cl[t,u,k]*(x[t,u,k] -r[u,k])**2 
                        for k in L[t]) for u in range(D[t][0],D[t][1]+1)  if w[t,u] !=0)  for t in range (T))
        
        opt_func_max_resource = -model.sum(z[t] for t in range(T))
        model.minimize(self.parameter.evenness_priority * opt_func_even + (1 - self.parameter.evenness_priority) * opt_func_max_resource)
        model.parameters.simplex.tolerances.feasibility = config.CPLEX_FEASIBILITY
        model.parameters.mip.tolerances.mipgap = config.CPLEX_GAP
        model.time_limit = self.parameter.time_limit_in_seconds
        model.parameters.optimalitytarget = config.CPLEX_OPTIMALITY_TARGET
        if config.CPLEX_EXPORT_MODEL == True:
            logging.info(model.export_as_lp())
        sol = model.solve(log_output = config.CPLEX_ENABLE_LOG)
       
        
        solve_details = {
            'model': model,
            'solution': sol,
            'x_dict' : x,
            'z_dict': z,
            'alpha': alpha,
        }

        return solve_details

    def _solve_step_2(self, step_1_solve_result):
        
        K = self.paper_model.K
        U = self.paper_model.U
        T = self.paper_model.T
        r = self.paper_model.r
        D = self.paper_model.D
        G = self.paper_model.G
        CTR = self.paper_model.CTR
        d = self.paper_model.d
        L = self.paper_model.L
        B = self.paper_model.B       
        t_0 = self.paper_model.t_0
        ratio = self.paper_model.ratio
        priority = self.paper_model.priority
        share_type = self.paper_model.share_type
        cl = self.paper_model.cl         
        w = self.paper_model.w       
        alpha = self.paper_model.alpha

        
        step_1_docplex_sol = step_1_solve_result['solution']
        step_1_x_dict = step_1_solve_result['x_dict']
        step_1_z_dict = step_1_solve_result['z_dict']
        x_star = step_1_docplex_sol.get_value_dict(step_1_x_dict)
        z_star = step_1_docplex_sol.get_value_dict(step_1_z_dict)

        model = Model("AcmSolver 2 steps-Step 2")
        campaign_list = np.arange(T)
        t_u_k_set = [(t, u, k) for t in range(T)
                        for u in range(U) for k in range(K)]
        u_k_set = [(u, k) for u in range(U) for k in range(K)]
        x = model.continuous_var_dict(t_u_k_set, lb=0, name='x')
        x_a = model.continuous_var_dict(u_k_set, lb=0, name='x_a')
        z = model.continuous_var_dict(campaign_list, lb=-99999999, ub=0, name='z')

        model.add_constraints(
            model.sum(model.sum((CTR[t_p,k]*x[t_p,u,k] 
                    for k in L[t_p] for u in range(D[t_p][0],D[t_p][1]+1) if w[t_p,u] !=0))
                    for t_p in range(T) if G[t_p]== G[t]) -z[t] == d[t] 
                    for t in range(T) if priority[t] == CampaignPriority.CLASS_B if G[t] is not None) 

        model.add_constraints(
            model.sum((CTR[t, k]*x[t, u, k]
                    for k in L[t] for u in range(D[t][0], D[t][1]+1) if w[t, u] != 0)) -z[t] == d[t] 
                    for t in range(T) if priority[t] == CampaignPriority.CLASS_B if G[t] is None)

        model.add_constraints(
            model.sum(x[t, u, k] for t in B[k] if u in range(D[t][0], D[t][1]+1) if w[t, u] != 0) + x_a[u, k] == r[u, k] for u in range(U) for k in range(K)) 

        model.add_constraints(x[t_prime, u, k] == 0
                            for t in range(t_0) if priority[t] == CampaignPriority.CLASS_C
                            for u in range(D[t][0], D[t][1]+1) if w[t, u] != 0
                            for k in L[t] for t_prime in range(t_0) if t_prime != t)

        model.add_constraints(x[t_prime, u, k] == 0
                            for t in range(t_0, T) if priority[t] == CampaignPriority.CLASS_C
                            for u in range(D[t][0], D[t][1] + 1) if w[t, u] != 0
                            for k in L[t] for t_prime in range(t_0, T) if t_prime != t)

        model.add_constraints(x_a[u, k] == 0
                            for t in range(T) if priority[t] == CampaignPriority.CLASS_C
                            for u in range(U)
                            for k in range(K) if u in range(D[t][0], D[t][1]+1) and w[t, u] != 0 and k in L[t])

        model.add_constraints(
            model.sum((x[t, u, k]
                    for k in L[t] for u in range(D[t][0], D[t][1]+1) if w[t, u] != 0)) >= 
                    np.sum([x_star[t,u,k] for k in L[t] for u in range(D[t][0], D[t][1]+1) if w[t, u] != 0 ]) for t in range(T))   

        model.add_constraints(
            model.sum(x[t,u,k] for t in range(t_0) if t in B[k] and u in range(D[t][0],D[t][1]+1) and w[t,u] !=0) 
            <= ratio[k]*r[u,k] for k in range(K) if share_type[k] == 1 for u in range(U)) # Không cho network tràn sang domain
            
        # Chặn dưới
        model.add_constraints(x[t,u,k] >= self.parameter.lower_ratio*alpha[t,u,k]*min(1, r[u,k]*ratio[k]/deno) 
            for t in range(t_0) if priority[t] == CampaignPriority.CLASS_B  
                for u in range(D[t][0],D[t][1]+1) 
                    for (deno,k) in ( (np.sum(alpha[:,u, k]),k) for k in L[t] if w[t,u] !=0 and CTR[t,k] !=0) if deno !=0)
        model.add_constraints(x[t,u,k] >= self.parameter.lower_ratio*alpha[t,u,k]*min(1, r[u,k]*(1-ratio[k])/deno) 
            for t in range(t_0, T) if priority[t] == CampaignPriority.CLASS_B 
                for u in range(D[t][0],D[t][1]+1) 
                    for (deno,k) in ((np.sum(alpha[:,u, k]),k) for k in L[t] if w[t,u] !=0 and CTR[t,k] !=0) if deno !=0)
        
        opt_func_even = model.sum(
                model.sum(
                    model.sum(
                        1/(alpha[t,u,k]+self.EPSILON)**1*((1-cl[t,u,k])*x[t,u,k]*CTR[t,k]-alpha[t,u,k])**2 + cl[t,u,k]*(x[t,u,k] -r[u,k])**2 
                        for k in L[t]) for u in range(D[t][0],D[t][1]+1)  if w[t,u] !=0)  for t in range (T))
        
        opt_func_max_resource = -model.sum(z[t] for t in range(T))

        model.minimize(self.parameter.evenness_priority * opt_func_even + (1 - self.parameter.evenness_priority) * opt_func_max_resource)
        model.parameters.simplex.tolerances.feasibility = config.CPLEX_FEASIBILITY
        model.parameters.mip.tolerances.mipgap = config.CPLEX_GAP
        model.time_limit = self.parameter.time_limit_in_seconds
        model.parameters.optimalitytarget = config.CPLEX_OPTIMALITY_TARGET
        if config.CPLEX_EXPORT_MODEL == True:
            logging.info(model.export_as_lp())
        sol = model.solve(log_output = config.CPLEX_ENABLE_LOG)
        
        solve_details = {
            'model': model,
            'solution': sol,
            'x_dict' : x,
            'x_a_dict' :x_a,
            'z_dict': z,
            'alpha': alpha,
        }

        return solve_details


    def _solve_b_c_soft(self):
        """
        Sử dụng CPLEX để giải bài toán tối ưu, có các biến nguyên,
        ràng buộc mềm, mô hình ban đầu của thầy Sơn
        """
      
        K = self.paper_model.K
        U = self.paper_model.U
        T = self.paper_model.T
        r = self.paper_model.r
        D = self.paper_model.D
        G = self.paper_model.G
        CTR = self.paper_model.CTR
        d = self.paper_model.d
        L = self.paper_model.L
        B = self.paper_model.B       
        t_0 = self.paper_model.t_0
        ratio = self.paper_model.ratio
        priority = self.paper_model.priority
        share_type = self.paper_model.share_type        
        cl = self.paper_model.cl         
        w = self.paper_model.w       
        alpha = self.paper_model.alpha
        
        p_network = .9*r/(np.sum(alpha, axis = 0) + 1)
        p_domain = .9*r/(np.sum(alpha, axis = 0) + 1)
        
        p_network = np.minimum(p_network,p)
        p_domain = np.minimum(p_domain,p)

        model = Model("awing_model_ver_10.6")
        campaign_list = np.arange(T)
        t_u_k_set = [(t, u, k) for t in range(T)
                        for u in range(U) for k in range(K)]
        u_k_set = [(u, k) for u in range(U) for k in range(K)]
        x= model.continuous_var_dict(t_u_k_set,lb = 0, name = 'x')
        x_a = model.continuous_var_dict(u_k_set,lb = 0, name = 'x_a')
        y= model.binary_var_dict(campaign_list, name = 'y')
        z = model.continuous_var_dict(campaign_list, lb=-99999999, ub = 0, name = 'z')
        
        #if get_click ==True: # for research purpose
        #    click = model.continuous_var_dict(t_u_k_set,lb = 0, name = 'click')
        #    model.add_constraints(click[t,u,k] == x[t,u,k]*CTR[t,k] for t in range(T) for u in range(U) for k in range(K))
            
        model.add_constraints(
            model.sum(model.sum((CTR[t_p,k]*x[t_p,u,k] 
                    for k in L[t_p] for u in range(D[t_p][0],D[t_p][1]+1) if w[t_p,u] !=0))
                    for t_p in range(T) if G[t_p]== G[t]) -z[t] == d[t] 
                    for t in range(T) if priority[t] == CampaignPriority.CLASS_B if G[t] is not None) 

        model.add_constraints(
            model.sum((CTR[t, k]*x[t, u, k]
                    for k in L[t] for u in range(D[t][0], D[t][1]+1) if w[t, u] != 0)) -z[t] == d[t] 
                    for t in range(T) if priority[t] == CampaignPriority.CLASS_B if G[t] is None)
        
        model.add_constraints(
            model.sum(x[t,u,k] for t in B[k] if u in range(D[t][0],D[t][1]+1) if w[t,u] !=0) + x_a[u,k] == r[u,k] for u in range(U) for k in range(K))  #(2)
        
        model.add_constraints(y[t] == 1 for t in range(T) if priority[t] == CampaignPriority.CLASS_C)
        model.add_constraints(x_a[u,k] == 0 
            for t in range(T) if priority[t] == CampaignPriority.CLASS_C 
                for u in range(U) 
                    for k in range(K) if u in range(D[t][0],D[t][1]+1) and w[t,u] != 0 and k in L[t])
        # Constraint 2 in case  class C
        logging.debug('constraints (2) added!')
        
        cnst_3 = [model.indicator_constraint(y[t], z[t] >= 0, 0) for t in range(T) if priority[t] == CampaignPriority.CLASS_B]
        cnst_3_5 = [model.indicator_constraint(y[t], z[t] <= -10**-3, 1) for t in range(T) if priority[t] == CampaignPriority.CLASS_B]
        model.add_indicator_constraints(cnst_3) # (3)
        model.add_indicator_constraints(cnst_3_5) # (3.5)
        logging.debug('constraints (3) added!')
        
        model.add_constraints(
            model.sum(x[t1,u,k] for t1 in range(t_0) if t1 in B[k] and u in range(D[t1][0],D[t1][1]+1) and w[t1,u] !=0) 
            >=ratio[k]*r[u,k]*y[t] for t in range(t_0) if priority[t] ==CampaignPriority.CLASS_B for u in range(D[t][0],D[t][1]+1) for k in L[t] if w[t,u] !=0 and CTR[t,k] !=0  and have_c_network[u,k] == 0 ) #(4)
        logging.debug('constraints (4) added!')
        
        model.add_constraints(
            model.sum(x[t1,u,k] for t1 in range(t_0,T) if t1 in B[k] and u in range(D[t1][0],D[t1][1]+1) and w[t1,u] !=0) 
            >=(1-ratio[k])*r[u,k]*y[t] for t in range(t_0,T) if priority[t] ==CampaignPriority.CLASS_B for u in range(D[t][0],D[t][1]+1) for k in L[t] if w[t,u] !=0 and CTR[t,k] !=0 and have_c_domain[u,k] == 0) #(5)
        logging.debug('constraints (5) added!')
        model.add_constraints(x[t_prime,u,k] == 0 
                            for t in range(t_0) if priority[t] == CampaignPriority.CLASS_C
                            for u in range(D[t][0],D[t][1]+1) if w[t,u] != 0
                            for k in L[t] for t_prime in range(t_0) if t_prime != t)
        
        model.add_constraints(x[t_prime,u,k] == 0 
                            for t in range(t_0,T) if priority[t] == CampaignPriority.CLASS_C
                            for u in range(D[t][0],D[t][1] + 1) if w[t,u] != 0
                            for k in L[t] for t_prime in range(t_0,T) if t_prime != t)
        
        # _________________ Constraint a Phong new
        
        model.add_constraints(x[t,u,k] >= p_network[u,k]*alpha[t,u,k] for t in range(t_0) if priority[t] ==CampaignPriority.CLASS_B for u in range(D[t][0],D[t][1]+1) for k in L[t] if w[t,u] !=0 and CTR[t,k] !=0  and have_c_network[u,k] == 0)
        
        model.add_constraints(x[t,u,k] >= p_domain[u,k]*alpha[t,u,k] for t in range(t_0,T) if priority[t] ==CampaignPriority.CLASS_B for u in range(D[t][0],D[t][1]+1) for k in L[t] if w[t,u] !=0 and CTR[t,k] !=0  and have_c_network[u,k] == 0)
        
        #________________End constraint a Phong new

        #_______BEGIN 2 campaign type c case at 1 date place_____
        model.add_constraints(x[t,u,k] >= r[u,k]*ratio[k] for t in range(t_0) if priority[t] == CampaignPriority.CLASS_C for u in range(D[t][0],D[t][1]+1) for k in L[t] if w[t,u] !=0)
        model.add_constraints(x[t,u,k] >= r[u,k]*(1-ratio[k]) for t in range(t_0,T) if priority[t] == CampaignPriority.CLASS_C for u in range(D[t][0],D[t][1]+1) for k in L[t] if w[t,u] !=0)
        #______END 2 campaign type c case________
        
        # Strich sharing constraint: ràng buộc share cứng, ko cho network tràn sang domain
        model.add_constraints(
            model.sum(x[t1,u,k] for t1 in range(t_0) if t1 in B[k] and u in range(D[t1][0],D[t1][1]+1) and w[t1,u] !=0) 
            <= ratio[k]*r[u,k] for k in range(K) if share_type[k] == 1 for u in range(U)) # Không cho network tràn sang domain
        
        opt_func_even = model.sum(
                model.sum(
                    model.sum(
                        1/(alpha[t,u,k]+self.EPSILON)**1*((1-cl[t,u,k])*x[t,u,k]*CTR[t,k]-alpha[t,u,k])**2 + cl[t,u,k]*(x[t,u,k] -r[u,k])**2 
                        for k in L[t]) for u in range(D[t][0],D[t][1]+1)  if w[t,u] !=0)  for t in range (T))
        model.minimize(opt_func_even)
        

        """ if opt_func =="max_rss":
            logging.debug("Maximum resource possible")
            opt_func_max_resource = -model.sum(z[t] for t in range(T))
            model.minimize(opt_func_max_resource)
        elif opt_func == 'trade_off':
            logging.debug("Trade off optimization function")
            model.minimize(evenness_priority * opt_func_even + (1 - evenness_priority) * opt_func_max_resource)
        elif opt_func == 'even':
            logging.debug("Trade off optimization function")
            
        elif opt_func =='max_rss_constraints':
            logging.debug("Max resource constraints")
            max_allocated = self.paper_model.max_allocated']
            model.add_constraint(
                model.sum((CTR[t,k]*x[t,u,k] 
                            for t in range(T) if priority[t] == CampaignPriority.CLASS_B for k in L[t] for u in range(D[t][0],D[t][1]+1) if w[t,u] !=0 )) >= delta * max_allocated)
            model.minimize(opt_func_even) """
            

        logging.debug('obj.function added!')

        model.parameters.simplex.tolerances.feasibility = config.CPLEX_FEASIBILITY
        model.parameters.mip.tolerances.mipgap = config.CPLEX_GAP
        model.time_limit = self.parameter.time_limit_in_seconds
        model.parameters.optimalitytarget = config.CPLEX_OPTIMALITY_TARGET
        if config.CPLEX_EXPORT_MODEL == True:
            logging.info(model.export_as_lp())
        sol = model.solve(log_output = config.CPLEX_ENABLE_LOG)
        
        solve_details = {
            'model': model,
            'solution': sol,
            'x_dict' : x,
            'x_a_dict' :x_a,
            'y_dict': y,
            'z_dict': z,
            'alpha': alpha,
        }
        #if get_click == True:
        #    solve_details['click'] = click
        return solve_details