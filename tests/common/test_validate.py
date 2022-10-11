import sys

sys.path.append('./')
sys.path.append('./acm_cplex_solver/')

from encodings import utf_8
import json
import pytest
import google.protobuf.json_format as json_format


from acm_cplex_solver.generated_protobuf import acm_cplex_solver_pb2
from acm_cplex_solver.generated_protobuf.acm_cplex_solver_pb2 import ACSModel, ACSCampaign, ACSPlace
from acm_cplex_solver.common.validator import Validator

def test_exception_validate_place_id_not_continuous_or_start_0():

    file_model = "./tests/common/test_validate_data/place_id_not_continuous_or_start_0.json" 
    _validate_exception(file_model)

def test_exception_validate_empty_views():
    file_model = "./tests/common/test_validate_data/empty_place_views.json" 
    _validate_exception(file_model)

def test_exception_validate_campaign_class_b_total_less_than_0():

    file_model = "./tests/common/test_validate_data/campaign_class_b_total_less_than_0.json" 
    _validate_exception(file_model)

def test_exception_validate_campaign_class_in_wrong_list():

    file_model = "./tests/common/test_validate_data/campaign_class_in_wrong_list.json" 
    _validate_exception(file_model)

def test_validate_ok_empty_class_b_c_campaigns():
    file_model = "./tests/common/test_validate_data/empty_class_b_c_campaigns.json" 
    _validate_ok(file_model)

def test_validate_ok_empty_all_campaigns():
    file_model = "./tests/common/test_validate_data/empty_all_campaigns.json" 
    _validate_ok(file_model)

def test_exception_validate_campaign_id_not_continuous_or_start_0():

    file_model = "./tests/common/test_validate_data/campaign_id_not_continuous_or_start_0.json" 
    _validate_exception(file_model)

def test_exception_validate_campaign_wrong_properties():

    file_model = "./tests/common/test_validate_data/campaign_wrong_properties.json" 
    _validate_exception(file_model)

def test_exception_validate_places_wrong_properties():

    file_model = "./tests/common/test_validate_data/places_wrong_properties.json" 
    _validate_exception(file_model)


def test_exception_validate_have_2_campaign_class_c():

    file_model = "./tests/common/test_validate_data/have_2_campaign_class_c.json" 
    _validate_exception(file_model)


def test_ok_all():

    file_model = "./tests/common/test_validate_data/ok_all.json" 
    _validate_ok(file_model)


def _validate_exception(file_model):
    with open(file_model, encoding='utf_8') as f:  
        json_object = json.load(f)
    for obj in json_object:
        acs_model = json_format.ParseDict(obj["model"], acm_cplex_solver_pb2.ACSModel())
        with pytest.raises(Exception) as ex_info:
            Validator.validate_model(acs_model)
        assert str(ex_info.value) == obj["expected_string"]

def _validate_ok(file_model):
    with open(file_model, encoding='utf_8') as f:  
        json_object = json.load(f)
    for obj in json_object:
        acs_model = json_format.ParseDict(obj["model"], acm_cplex_solver_pb2.ACSModel())
        Validator.validate_model(acs_model)