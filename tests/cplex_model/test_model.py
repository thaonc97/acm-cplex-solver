from bson.json_util import loads
import json
import numpy as np
import pandas as pd
import os
import sys
# sys.path.append('../../')
# sys.path.append('../../acm_cplex_solver')
# sys.path.append('../../acm_cplex_solver/generated_protobuf')
sys.path.append('../')
sys.path.append('../acm_cplex_solver')
sys.path.append('../acm_cplex_solver/generated_protobuf')
import acm_cplex_solver.config as config
from acm_cplex_solver.cplex_model.paper_model import PaperModel
from acm_cplex_solver.cplex_model.cplex_model_solver import CplexModelSolver
from acm_cplex_solver.cplex_model.solver_parameter import SolverParameter
from acm_cplex_solver.cplex_model.class_a_model_solver import ClassAModelSolver

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

def correct_class_a_fromm_json(data):
    data['r']= np.array(data['r'])
    data['total_b_c_network'] = np.array(data['total_b_c_network'])
    data['total_b_c_domain'] = np.array(data['total_b_c_domain'])
    return data


def prep_solve_result_json(json_solve_results):
    """Trả về thông dict dạng {problem id : DataFrame tương ứng với problem id}

    Parameters
    ----------
    json_solve_results : 
        _description_

    Returns
    -------
    solve_result_dict: Dict
        dict dạng {problem id : DataFrame tương ứng với problem id}
    """
    problem_ids = list(set([record['problem_id'] for record in json_solve_results]))
    solve_result_dict = {prob_id:[] for prob_id in problem_ids}

    for record in json_solve_results:
        problem_id = record['problem_id']
        solve_result_dict[problem_id].append(record)
        
    for problem_id in solve_result_dict:
        cur_prob_df =  pd.DataFrame(solve_result_dict[problem_id])
        cur_prob_df= cur_prob_df.drop(['_id','createDate','problem_id'], axis =1)
        try:
            cur_prob_df= cur_prob_df.sort_values(by = ['campaign_id', 'date', 'place_id']).reset_index(drop = True)
            cur_prob_df = cur_prob_df[['campaign_id','date','place_id','value']]# Chỉnh thứ tự cột
        except Exception as e:
            print(f'problem id {problem_id}')
            raise e
        solve_result_dict[problem_id] = cur_prob_df

    return solve_result_dict



def test_CplexModelSolver_solve_preset_data_two_steps_ok():
    problem_ids = ['1','2','3','6','7','8','9','10','1_b_domain_1_c_network','1_b_network_1_c_domain',
    '1_domain_campaign_share_rate_1','1_network_campaign_share_rate_0','1c','2c','3c','hard_nw_1']
    SOLVE_PATH = './cplex_model/test_model_data/results/solve_bc_results.json'
    with open(SOLVE_PATH) as f:
        solve_result = json.load(f)
    solve_result = prep_solve_result_json(solve_result)
    
    for problem_id in problem_ids:
        expected_x_bc_df = solve_result[problem_id]
        INPUT_PATH = f'./cplex_model/test_model_data/data_{problem_id}.json'
        with open(INPUT_PATH) as f:  
            input = json.load(f)
        input = correct_data_from_json(input)
        

        paper_model = PaperModel(**input)
        mocked_acs_param = MockedACSParameter()
        parameter = SolverParameter(mocked_acs_param)
        bc_solver = CplexModelSolver(paper_model, parameter, )
        actual_x_bc_df, z_df = bc_solver.solve()

        try:
            pd.testing.assert_frame_equal(expected_x_bc_df, actual_x_bc_df, check_dtype= False, check_like= True, check_exact= False,atol = 0.01)
        except AssertionError as e:
            print("df_expected: \n ", expected_x_bc_df)
            print("df_actual: \n", actual_x_bc_df)
            print("problem_id: ",problem_id)
            e.args += ("problem_id: ",problem_id)
            raise

def test_solve_a_preset_data_ok():
    problem_ids = ['1_campaign_a_each','2_campaign_a_network','2_campaign_a_domain','no_campaign_a']
    SOLVE_PATH = './cplex_model/test_model_data/results/solve_a_results.json'
    with open(SOLVE_PATH) as f:
        solve_result = json.load(f)
    solve_result = prep_solve_result_json(solve_result)
    for problem_id in problem_ids:
        INPUT_PATH = f'./cplex_model/test_model_data/input_solve_a/data_{problem_id}.json'
        with open(INPUT_PATH) as f:  
            input = json.load(f)
        input = correct_class_a_fromm_json(input)
        a_model_solver = ClassAModelSolver(**input)
        actual_df_x_a = pd.DataFrame(a_model_solver.solve())
        actual_df_x_a = actual_df_x_a.sort_values(by = ['campaign_id', 'date', 'place_id']).reset_index(drop = True)
        expected_df_x_a = solve_result[problem_id]
        pd.testing.assert_frame_equal(expected_df_x_a, actual_df_x_a, check_dtype= False, check_like= True, check_exact= False,atol = 0.01)
