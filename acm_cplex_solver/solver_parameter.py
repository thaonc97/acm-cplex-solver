from generated_protobuf.acm_cplex_solver_pb2 import ACSParameter, ACSSolveMethod, ACSSolveIncludeClassAOption 


class SolverParameter:
    def __init__(self, acs_parameter : ACSParameter):

        if(acs_parameter.lower_ratio<0 or acs_parameter.lower_ratio>1):
            raise Exception("Tỉ lệ chặn dưới lower_ratio phải thuộc đoạn [0,1]")
        self.lower_ratio = acs_parameter.lower_ratio      

        if(acs_parameter.evenness_priority<0 or acs_parameter.evenness_priority>1):
            raise Exception("Tham số đều - max tài nguyên phải thuộc đoạn [0,1]")
        self.evenness_priority = acs_parameter.evenness_priority

        self.method = acs_parameter.solve_method
        self.time_limit_in_seconds = acs_parameter.time_limit_in_seconds
        if(self.time_limit_in_seconds<3600):
            self.time_limit_in_seconds=3600
        self.include_class_a_option = acs_parameter.include_class_a_option
      
