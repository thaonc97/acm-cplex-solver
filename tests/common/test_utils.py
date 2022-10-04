from acm_cplex_solver.common.utils import Utils

import sys

sys.path.append('/Projects/acm/acm/acmcplexsolver/acm_cplex_solver/')

#sys.path.append('../acm_cplex_solver/')

def test_check_continuous_list_empty():
    """ Case list rỗng
    """

    result, value = Utils.check_continuous_list([],0)
    assert result==2 and value==0



def test_check_continuous_list_ok():
    """ Case liên tục
    """

    result, value = Utils.check_continuous_list([0],)
    assert result==0 and value==1

    result, value = Utils.check_continuous_list([1,2,3,4],1)
    assert result==0 and value==5



def test_check_continuous_list_nok():
    """ Case không liên tục
    """

    result, value = Utils.check_continuous_list([1],)
    assert result==1 and value==0

    result, value = Utils.check_continuous_list([1,3,2,4],1)
    assert result==1 and value==1


def test_check_duplicate_not_duplicate():
    """Test case không trùng
    """
    assert Utils.check_duplicate([])==False
    assert Utils.check_duplicate([1,3,4])==False



def test_check_duplicate_duplicate():
    """Test case trùng
    """
    assert Utils.check_duplicate([1,1])==True
    assert Utils.check_duplicate([1,3,4,2,3])==True


