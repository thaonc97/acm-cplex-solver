
from numpy import ndarray
from cplex_model.paper_model import PaperModel
from cplex_model.class_a_model import ClassAModel


class ClassASolver:
    

    def convert(solve_details, paper_model : PaperModel) -> ndarray:
        """_summary_

        Args:
            solve_details (_type_): _description_
            paper_model (PaperModel): _description_

        Returns:
            ndarray: n[u,k] = ClassAModel của ngày u, địa điểm k
        """
        pass


    def solve(class_a, resources):
        """_summary_

        Args:
            class_a (_type_): danh sách class a
            resources (_type_): mảng 2 chiều chứa ClassAModel tại ngày u, địa điểm k
        """
        pass

