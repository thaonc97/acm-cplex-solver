
from acm_cplex_solver.cplex_model.cplex_model_solver import CplexModelSolver
from generated_protobuf import acm_cplex_solver_pb2, acm_cplex_solver_pb2_grpc

class AcmCplexSolverService(acm_cplex_solver_pb2_grpc.AcmCplexSolverService):
    def __init__(self):
        pass

    def Solve(self,request,context):
        
        
        solver = CplexModelSolver(request.model, request.parameter, request.option)
        result = solver.solve()

        
        response = []
        return response