class SolverParameter:
    def __init__(self):     
        self.lower_ratio = 0.1   
        self.alpha_formula = '3'
        self.time_limit = 3600
        self.gap = 0.1        
        self.export_model = False 
        self.optimality_target = 0
        self.evenness_priority = 1
        self.method = "TWO_STEPS"
        self.delta = 0.9
        self.feasibility = 10**-4
