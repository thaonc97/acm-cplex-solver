# GRPC config
GRPC_MAX_WORKER = 10
GRPC_PORT = 50051

# CPLEX
CPLEX_GAP = 0.1
CPLEX_OPTIMALITY_TARGET = 0
CPLEX_DELTA = 0.9
CPLEX_FEASIBILITY = 10**-4
LOG_LEVEL = "DEBUG" # DEBUG < INFO < WARNING < ERROR < CRITICAL < FATAL
#log_fomartter = "%(message)s"
# Nếu muốn thêm thời gian và loglevel thì dùng format bên dưới
LOG_FORMATTER = "%(asctime)s:%(levelname)s:%(message)s"