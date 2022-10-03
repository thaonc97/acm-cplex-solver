
from acm_cplex_solver.cplex_model.converter import Converter
from acm_cplex_solver.cplex_model.cplex_model_solver import CplexModelSolver
from acm_cplex_solver.cplex_model.solver_parameter import SolverParameter
from acm_cplex_solver.cplex_model.validate import Validator
from generated_protobuf import acm_cplex_solver_pb2, acm_cplex_solver_pb2_grpc

class AcmCplexSolverService(acm_cplex_solver_pb2_grpc.AcmCplexSolver):
    def __init__(self):
        pass

    def Solve(self,request,context):
        
        
        Validator.validate_model(request.model)
        
        
        parameter = SolverParameter(request.parameter)
        option = Converter.convert_grpc_option_to_option(request.option)
        paper_model = Converter.convert_grpc_message_to_model(request.model, parameter.alpha_formula)
        solver = CplexModelSolver(paper_model, parameter, option)

        result = solver.solve()
        
        response = []
        return response