
import google.protobuf.json_format as json_format
import logging
from common.converter import Converter
from paper_model.paper_model_solver import PaperModelSolver
from solver_parameter import SolverParameter
from common.validator import Validator
from generated_protobuf import acm_cplex_solver_pb2, acm_cplex_solver_pb2_grpc

class AcmCplexSolverService(acm_cplex_solver_pb2_grpc.AcmCplexSolver):
    def __init__(self):
        pass

    def Solve(self,request,context):
        
        logging.debug(json_format.MessageToJson(request))

        parameter = SolverParameter(request.parameter)
        paper_model = Converter.convert_grpc_message_to_paper_model(request.model)
        bc_solver = PaperModelSolver(paper_model, parameter)
        x_bc_df, z_df = bc_solver.solve()
        class_a_model_solver = Converter.convert_solve_details_to_class_a_model(x_bc_df, paper_model, request.model.campaigns_class_a)
        x_a = class_a_model_solver.solve()
        result = Converter.convert_solver_to_acs_result(x_bc_df, z_df, x_a)

        logging.debug(json_format.MessageToJson(result))

        return result