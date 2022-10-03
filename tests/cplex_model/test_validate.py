import json
import pytest
import google.protobuf.json_format as json_format

import sys

sys.path.append('/Projects/acm/acm/acmcplexsolver/acm_cplex_solver/')
sys.path.append('../acm_cplex_solver/')

import acm_cplex_solver.generated_protobuf.acm_cplex_solver_pb2 as acm_cplex_solver_pb2
from acm_cplex_solver.generated_protobuf.acm_cplex_solver_pb2 import ACSModel, ACSCampaign, ACSPlace
from acm_cplex_solver.cplex_model.validate import Validator

def test_validate_duplicate_place_id():

    file_model = "./tests/cplex_model/test_validate_data/duplicate_place_id.json" 
    with open(file_model) as f:  
        json_object = json.load(f)
        acs_model = json_format.ParseDict(json_object, acm_cplex_solver_pb2.ACSModel())
    with pytest.raises(Exception) as ex_info:
        Validator.validate_model(acs_model)
    assert str(ex_info.value) == "Có place id trùng nhau"


def test_validate_place_id_not_continuous():

    file_model = "./tests/cplex_model/test_validate_data/place_id_not_continuous.json" 
    with open(file_model) as f:  
        json_object = json.load(f)
        acs_model = json_format.ParseDict(json_object, acm_cplex_solver_pb2.ACSModel())
    with pytest.raises(Exception) as ex_info:
        Validator.validate_model(acs_model)
    assert str(ex_info.value) == "Mảng rỗng hoặc chỉ số id của place không liên tục và bắt đầu từ 0"


def test_validate_place_id_not_start_0():

    file_model = "./tests/cplex_model/test_validate_data/place_id_not_start_0.json" 
    with open(file_model) as f:  
        json_object = json.load(f)
        acs_model = json_format.ParseDict(json_object, acm_cplex_solver_pb2.ACSModel())
    with pytest.raises(Exception) as ex_info:
        Validator.validate_model(acs_model)
    assert str(ex_info.value) == "Mảng rỗng hoặc chỉ số id của place không liên tục và bắt đầu từ 0"