from generated_protobuf.acm_cplex_solver_pb2 import ACSParameter, SolveMethod


class SolverParameter:
    def __init__(self, acs_parameter : ACSParameter):    
        """ if(acs_parameter.lower_ratio == None):
            self.lower_ratio = 0.1   
        else:
            self.lower_ratio = acs_parameter.lower_ratio   """
        self.lower_ratio = 0.1 
        self.alpha_formula = 3        
        self.evenness_priority = 1
        self.method = SolveMethod.SOLVE_TWO_STEPS
        self.time_limit_in_seconds = 3600
      
