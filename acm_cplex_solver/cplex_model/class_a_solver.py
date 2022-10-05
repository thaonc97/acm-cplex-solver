from typing import List
import numpy as np
import pandas as pd
from copy import deepcopy
from acm_cplex_solver.generated_protobuf.acm_cplex_solver_pb2 import ACSCampaign
from cplex_model.class_a_model import ClassAModel
from cplex_model.paper_model import PaperModel

class ClassASolver():

    

    def _solve(classed_a_added_campaigns):
        for date in range(len(classed_a_added_campaigns)):
            for place in range(len(date)):
                pass #TODO

    def solve(solve_details,paper_model, resource):
        classes_a = ClassASolver._convert(solve_details, paper_model)
        classed_a_added_campaigns = ClassASolver._get_running_a(classes_a, resource)
        class_a_result = ClassASolver._solve(classed_a_added_campaigns, resource)
        return class_a_result
    
