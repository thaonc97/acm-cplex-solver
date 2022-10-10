
from concurrent import futures
import logging
import grpc
import time
import config
from services.acm_cplex_solver_service import AcmCplexSolverService
from generated_protobuf import acm_cplex_solver_pb2_grpc

def serve():

    logging.basicConfig(format=config.LOG_FORMATTER, level=config.LOG_LEVEL, datefmt='%d-%b-%y %H:%M:%S')

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=config.GRPC_MAX_WORKER))
    acm_cplex_solver_pb2_grpc.add_AcmCplexSolverServicer_to_server(
        AcmCplexSolverService(), server)
    server.add_insecure_port(f'[::]:{config.GRPC_PORT}')
    server.start()
    logging.info(f'Server started. Listening on port {config.GRPC_PORT}.')

    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()