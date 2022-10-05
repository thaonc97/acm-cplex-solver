
from common.converter import Converter
from cplex_model.cplex_model_solver import CplexModelSolver
from cplex_model.solver_parameter import SolverParameter
from cplex_model.validate import Validator
from generated_protobuf import acm_cplex_solver_pb2, acm_cplex_solver_pb2_grpc

class AcmCplexSolverService(acm_cplex_solver_pb2_grpc.AcmCplexSolver):
    def __init__(self):
        pass

    def Solve(self,request,context):
        
                
        parameter = SolverParameter(request.parameter)
        paper_model = Converter.convert_grpc_message_to_model(request.model, parameter.alpha_formula)
        bc_solver = CplexModelSolver(paper_model, parameter, )
        result = bc_solver.solve()
        class_a = Converter.convert_solve_details_to_class_a_model(result, paper_model, request.model.campaigns_class_a)
        response = []
        return response