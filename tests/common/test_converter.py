from encodings import utf_8
import json
import google.protobuf.json_format as json_format

import sys
from acm_cplex_solver.common.utils import Utils


sys.path.append('../acm_cplex_solver/')

from acm_cplex_solver.generated_protobuf.acm_cplex_solver_pb2 import ACSModel
from acm_cplex_solver.common.converter import Converter


def test_convert_grpc_message_to_acs_model_ok():

    file_model = "./common/test_converter_data/2P_00_00_0.json" 
    _convert_ok(file_model)


def _convert_ok(file_model):
    with open(file_model, encoding='utf_8') as f:  
        json_object = json.load(f)
    for obj in json_object:
        acs_model = json_format.ParseDict(obj["acs_model"], ACSModel())              
        result_dict = Converter.convert_grpc_message_to_model(acs_model, alpha_formula=3).to_dict()
        expected_dict = obj["expected_paper_model"]
        # convert sang dict để so sánh, tránh định dạng numpy khó xử lý
        assert Utils.compare(result_dict, expected_dict) == True