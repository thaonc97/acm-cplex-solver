import json
import numpy as np
import pandas as pd
import os
import sys
sys.path.append('./')
sys.path.append('./acm_cplex_solver')
# sys.path.append('./acm_cplex_solver/test_common')
# sys.path.append('../acm_cplex_solver/generated_protobuf')
import acm_cplex_solver.config as config
from acm_cplex_solver.paper_model.paper_model import PaperModel
from acm_cplex_solver.paper_model.paper_model_solver import PaperModelSolver
from acm_cplex_solver.solver_parameter import SolverParameter
from acm_cplex_solver.class_a_model.class_a_model_solver import ClassAModelSolver


class MockedACSParameter():
    def __init__(self): 
        self.lower_ratio = 0
        self.alpha_formula = 3
        self.evenness_priority = 1
        self.solve_method = 0
        self.time_limit_in_seconds = 3600
        self.include_class_a_option = True


def correct_data_bc_from_json(data):
    data['ratio'] = data['share_rate']
    del data['share_rate']
    data['w'] = np.array(data['w'])
    data['r'] = np.array(data['r'])
    data['CTR'] = np.array(data['CTR'])
    return data

def test_CplexModelSolver_solve_preset_data_two_steps_ok():
    problem_ids = ['1','2','3','6','7','8','9','10','1_b_domain_1_c_network','1_b_network_1_c_domain',
    '1_domain_campaign_share_rate_1','1_network_campaign_share_rate_0','1c','2c','3c','hard_nw_1','group1','group2']

    for problem_id in problem_ids:
        TEST_DATA_PATH = f'./tests/test_paper_model/data/{problem_id}.json'
        try:

            with open(TEST_DATA_PATH, encoding='utf_8') as f:
                data = json.load(f)

            raw_input = data['input']
            input = correct_data_bc_from_json(raw_input)
            expected_x_bc_df = pd.DataFrame(data['output'])
            paper_model = PaperModel(**input)
            mocked_acs_param = MockedACSParameter()
            parameter = SolverParameter(mocked_acs_param)
            bc_solver = PaperModelSolver(paper_model, parameter, )
            
            actual_x_bc_df, z_df = bc_solver.solve()
            
            pd.testing.assert_frame_equal(expected_x_bc_df, actual_x_bc_df, check_dtype= False, check_like= True, check_exact= False,atol = 0.01)
        
        except Exception as e:         
            print("problem_id: ",problem_id)
            e.args += ("problem_id: ",problem_id)
            raise