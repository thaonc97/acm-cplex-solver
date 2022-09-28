connection_str = "mongodb://acm:AWing%402020@118.70.206.204:27017/?authSource=admin"  # dev
# connection_str = "mongodb://192.168.10.202:27017"  # demo
# connection_str = "mongodb://172.16.2.106:27017"  # staging

# Miscs.
range_date_int_mapper = 365

# Problem
days_per_problem = 100

# Solver config
solve_method = "TWO_STEPS" # choose 'TWO_STEPS' or 'SOFT_CONSTRAINT'
split_method = 'binary' # choose 'binary' or 'by_places'

# grpc config
max_grpc_worker = 10
port = 50051

# log
enable_log = True