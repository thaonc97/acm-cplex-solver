1. Tạo link file protos từ acmmessage bằng lệnh (để xem nội dung file protos và gen lại nếu cần thiết)
mklink /j  D:\Projects\acm\acm\acmcplexsolver\acm_cplex_solver\protos\ D:\Projects\acm\acm\acmmessage\Protos\

Gen lại bằng lệnh nếu có thay đổi nội dung file protos

python -m grpc_tools.protoc -I./acm_cplex_solver/protos --python_out=./acm_cplex_solver/generated_protobuf --grpc_python_out=./acm_cplex_solver/generated_protobuf ./acm_cplex_solver/protos/acm_cplex_solver.proto
python -m grpc_tools.protoc -I./acm_cplex_solver/protos --python_out=./acm_cplex_solver/generated_protobuf --grpc_python_out=./acm_cplex_solver/generated_protobuf ./acm_cplex_solver/protos/acm_base.proto