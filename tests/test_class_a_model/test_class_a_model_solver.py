import json
import numpy as np
import pandas as pd
import sys
sys.path.append('./')
sys.path.append('./acm_cplex_solver')
from acm_cplex_solver.class_a_model.class_a_model_solver import ClassAModelSolver


def correct_class_a_fromm_json(data):
    data['r']= np.array(data['r'])
    data['total_b_c_network'] = np.array(data['total_b_c_network'])
    data['total_b_c_domain'] = np.array(data['total_b_c_domain'])
    return data


def test_solve_a_preset_data_ok():
    problem_ids = [
        '1_a_domain_1_a_network',
        '2_campaign_a_network',
        '2_campaign_a_domain',
        'no_campaign_a']

    for problem_id in problem_ids:
        TEST_DATA_PATH = f'./tests/test_class_a_model/data/{problem_id}.json'
        with open(TEST_DATA_PATH) as f:  
            data = json.load(f)
        input = correct_class_a_fromm_json(data['input'])
        a_model_solver = ClassAModelSolver(**input)
        actual_df_x_a_unsorted = pd.DataFrame(a_model_solver.solve())
        actual_df_x_a = actual_df_x_a_unsorted.sort_values(
            by = ['campaign_id', 'date', 'place_id']).reset_index(drop = True)
        expected_df_x_a = pd.DataFrame(data['output'])
        pd.testing.assert_frame_equal(
            expected_df_x_a, 
            actual_df_x_a, 
            check_dtype= False, 
            check_like= True, 
            check_exact= False,
            atol = 0.01)