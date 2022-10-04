from encodings import utf_8
import json
import pytest
import google.protobuf.json_format as json_format

import sys

sys.path.append('/Projects/acm/acm/acmcplexsolver/acm_cplex_solver/')
#sys.path.append('../acm_cplex_solver/')


from acm_cplex_solver.generated_protobuf import acm_cplex_solver_pb2
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


def test_validate_place_id_not_continuous_or_start_0():

    file_model = "./tests/cplex_model/test_validate_data/place_id_not_continuous_or_start_0.json" 
    with open(file_model, encoding='utf_8') as f:  
        json_object = json.load(f)
    for obj in json_object:
        acs_model = json_format.ParseDict(obj["model"], acm_cplex_solver_pb2.ACSModel())
        with pytest.raises(Exception) as ex_info:
            Validator.validate_model(acs_model)
        assert str(ex_info.value) == obj["expected_string"]


def test_validate_duplicate_campaign_id():

    file_model = "./tests/cplex_model/test_validate_data/duplicate_campaign_id.json" 
    with open(file_model, encoding='utf_8') as f:  
        json_object = json.load(f)
    for obj in json_object:
        acs_model = json_format.ParseDict(obj["model"], acm_cplex_solver_pb2.ACSModel())
        with pytest.raises(Exception) as ex_info:
            Validator.validate_model(acs_model)
        assert str(ex_info.value) == obj["expected_string"]