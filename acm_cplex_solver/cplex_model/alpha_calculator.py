from acm_cplex_solver.cplex_model.paper_model import PaperModel
from acm_cplex_solver.generated_protobuf.acm_cplex_solver_pb2 import ACSModel
import numpy as np

class AlphaCalculator:    
    """
    Các công thức tính alpha.
    """

    def __init__(self, paper_model : PaperModel):        
        self.paper_model = paper_model


    def calculate(self,formula = '3'):
        if formula == '0' :
            return self._formula_0()
        elif formula == '1':
            return self._formula_1()
        elif formula == '2':
            return self._formula_2()
        elif formula == '3':
            return self._formula_3()
        else:
            print("Invalid formula number!")

    def _formula_0(self):
        """
        Công thức phức tạp thầy Sơn
        """
      
        K = self.paper_model.K
        U = self.paper_model.U
        T = self.paper_model.T
        r = self.paper_model.r
        D = self.paper_model.D
        G = self.paper_model.G
        CTR = self.paper_model.CTR
        d = self.paper_model.d
        w = self.paper_model.w
        L = self.paper_model.L
        B = self.paper_model.B       
        t_0 = self.paper_model.t_0
        ratio = self.paper_model.share_rate
        priority = self.paper_model.priority
        share_type = self.paper_model.share_type
        campaign_list = self.paper_model.campaign_list
        cl = self.paper_model.cl          
        w = self.paper_model.w       
        
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
        K = self.paper_model.K
        U = self.paper_model.U
        T = self.paper_model.T
        r = self.paper_model.r
        D = self.paper_model.D
        G = self.paper_model.G
        CTR = self.paper_model.CTR
        d = self.paper_model.d
        w = self.paper_model.w
        L = self.paper_model.L
        B = self.paper_model.B       
        t_0 = self.paper_model.t_0
        ratio = self.paper_model.ratio
        priority = self.paper_model.priority
        share_type = self.paper_model.share_type
        campaign_list = self.paper_model.campaign_list
        cl = self.paper_model.cl          
        w = self.paper_model.w 
        
        # Calculate d_tu
        d_tu = [d[t]*w[t]/(np.sum(w[t])) for t in range(T)]
        
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

        K = self.paper_model.K
        U = self.paper_model.U
        T = self.paper_model.T
        r = self.paper_model.r
        D = self.paper_model.D
        G = self.paper_model.G
        CTR = self.paper_model.CTR
        d = self.paper_model.d
        w = self.paper_model.w
        L = self.paper_model.L
        B = self.paper_model.B       
        t_0 = self.paper_model.t_0
        ratio = self.paper_model.ratio
        priority = self.paper_model.priority
        share_type = self.paper_model.share_type     
        cl = self.paper_model.cl          
        w = self.paper_model.w 

        # Calculate d_tu: lượng yêu cầu chạy theo ngày của từng campaign
        d_tu = [d[t]*w[t]/(np.sum(w[t])) for t in range(T)] 

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

        K = self.paper_model.K
        U = self.paper_model.U
        T = self.paper_model.T
        r = self.paper_model.r
        D = self.paper_model.D
        G = self.paper_model.G
        CTR = self.paper_model.CTR
        d = self.paper_model.d
        w = self.paper_model.w
        L = self.paper_model.L
        B = self.paper_model.B       
        t_0 = self.paper_model.t_0
        ratio = self.paper_model.ratio
        priority = self.paper_model.priority
        share_type = self.paper_model.share_type        
        cl = self.paper_model.cl          
        w = self.paper_model.w 
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

    