
from concurrent import futures
import logging
import grpc
import time
import config
from acm_cplex_solver.services.acm_cplex_solver_service import AcmCplexSolverService
from acm_cplex_solver.generated_protobuf import acm_cplex_solver_pb2_grpc

def serve():
    logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO, datefmt='%d-%b-%y %H:%M:%S')

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=config.grpc_max_worker))
    acm_cplex_solver_pb2_grpc.add_AcmCplexSolverServicer_to_server(
        AcmCplexSolverService(), server)
    server.add_insecure_port(f'[::]:{config.grpc_port}')
    server.start()
    logging.info(f'Server started. Listening on port {config.grpc_port}.')

    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()