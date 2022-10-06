import json
from bson.json_util import loads
import sys
import numpy as np
# sys.path.append('../../')
# sys.path.append('../../acm_cplex_solver')
# sys.path.append('../../acm_cplex_solver/generated_protobuf')
sys.path.append('../')
sys.path.append('../acm_cplex_solver')
sys.path.append('../acm_cplex_solver/generated_protobuf')
import acm_cplex_solver.config as config
from acm_cplex_solver.cplex_model.paper_model import PaperModel
def test_CplexModelSolver_solve_preset_data_two_steps_ok():
    DATA_PATH = './cplex_model/test_model_data/data_2.json'
    with open(DATA_PATH) as f:  
        file_data = json.load(f)
        data  = loads(json.dumps(file_data))
        if 'share_rate' in data:
            data['ratio'] = data['share_rate']
            del data['share_rate']
    T,U,K,priority = data['T'],data['U'], data['K'], data['priority']
    cl = np.zeros([T, U, K])
    for t in range(T):
        if priority[t] == "CLASS_C":
            for u in range(D[t][0], D[t][1]+1):
                for k in L[t]:
                    cl[t, u, k] = 1
    data['cl'] = cl
    print(cl)
    paper_model = PaperModel(**data)
    #WIP TODO
    assert False