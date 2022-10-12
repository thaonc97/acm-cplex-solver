import sys

sys.path.append('./')
sys.path.append('./acm_cplex_solver/')

from encodings import utf_8
import json
import google.protobuf.json_format as json_format

from acm_cplex_solver.common.utils import Utils

from acm_cplex_solver.generated_protobuf.acm_cplex_solver_pb2 import ACSModel
from acm_cplex_solver.common.converter import Converter
import pytest


def test_convert_grpc_message_to_acs_model_0_campaign():
    file_model = "./tests/test_common/test_converter_data/2P_00_00_0.json"
    _convert_return_true(file_model)

def test_convert_grpc_message_to_acs_model_1_campaign_b_domain():
    file_model = "./tests/test_common/test_converter_data/2P_00_01_0.json"
    _convert_return_true(file_model)

def test_convert_grpc_message_to_acs_model_1_campaign_c_domain():
    file_model = "./tests/test_common/test_converter_data/2P_00_10_0.json"
    _convert_return_true(file_model)

def test_convert_grpc_message_to_acs_model_1_campaign_b_network():
    file_model = "./tests/test_common/test_converter_data/2P_01_00_0.json"
    _convert_return_true(file_model)

def test_convert_grpc_message_to_acs_model_1_campaign_c_network():
    file_model = "./tests/test_common/test_converter_data/2P_10_00_0.json"
    _convert_return_true(file_model)

def test_convert_grpc_message_to_acs_model_1_campaign_c_network_1_campaign_c_domain():
    file_model = "./tests/test_common/test_converter_data/2P_10_10_0.json"
    _convert_return_true(file_model)

def test_convert_grpc_message_to_acs_model_1_campaign_c_network_1_campaign_b_domain():
    file_model = "./tests/test_common/test_converter_data/2P_10_01_0.json"
    _convert_return_true(file_model)

def test_convert_grpc_message_to_acs_model_1_campaign_c_network_1_campaign_b_network():
    file_model = "./tests/test_common/test_converter_data/2P_11_00_0.json"
    _convert_return_true(file_model)

def test_convert_grpc_message_to_acs_model_1_campaign_b_network_1_campaign_c_domain():
    file_model = "./tests/test_common/test_converter_data/2P_01_10_0.json"
    _convert_return_true(file_model)

def test_convert_grpc_message_to_acs_model_1_campaign_b_network_1_campaign_b_domain():
    file_model = "./tests/test_common/test_converter_data/2P_01_01_0.json"
    _convert_return_true(file_model)

def test_convert_grpc_message_to_acs_model_1_campaign_c_domain_1_campaign_b_domain():
    file_model = "./tests/test_common/test_converter_data/2P_00_11_0.json"
    _convert_return_true(file_model)

def test_convert_grpc_message_to_acs_model_1_campaign_c_domain_1_campaign_b_domain_1_campaign_c_network():
    file_model = "./tests/test_common/test_converter_data/2P_11_10_0.json"
    _convert_return_true(file_model)

def test_convert_grpc_message_to_acs_model_1_campaign_c_network_1_campaign_b_network_1_campaign_b_domain():
    file_model = "./tests/test_common/test_converter_data/2P_11_01_0.json"
    _convert_return_true(file_model)

def test_convert_grpc_message_to_acs_model_1_campaign_c_network_1_campaign_c_domain_1_campaign_b_domain():
    file_model = "./tests/test_common/test_converter_data/2P_10_11_0.json"
    _convert_return_true(file_model)

def test_convert_grpc_message_to_acs_model_1_campaign_b_network_1_campaign_c_domain_1_campaign_b_domain():
    file_model = "./tests/test_common/test_converter_data/2P_01_11_0.json"
    _convert_return_true(file_model)

def test_convert_grpc_message_to_acs_model_1_campaign_c_network_1_campaign_b_network_1_campaign_c_domain_1_campaign_b_domain():
    file_model = "./tests/test_common/test_converter_data/2P_11_11_0.json"
    _convert_return_true(file_model)

def test_convert_grpc_message_to_acs_model_1_campaign_c_network_1_campaign_b_network_1_campaign_c_domain_1_campaign_b_domain_1_campaign_a():
    file_model = "./tests/test_common/test_converter_data/2P_11_11_1.json"
    _convert_return_true(file_model)

def _convert_return_true(file_model):
    with open(file_model, encoding='utf_8') as f:  
        json_object = json.load(f)
    for obj in json_object:
        acs_model = json_format.ParseDict(obj["acs_model"], ACSModel())              
        result_dict = Converter.convert_grpc_message_to_paper_model(acs_model).to_dict()
        expected_dict = obj["expected_paper_model"]
        # convert sang dict để so sánh, tránh định dạng numpy khó xử lý
        assert Utils.compare(result_dict, expected_dict) == True