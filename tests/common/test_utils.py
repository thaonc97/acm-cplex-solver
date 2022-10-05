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


def test_compare_nok_diff_type():
    a = '112'
    b = 1
    assert not Utils.compare(a, b)


def test_compare_ok_primitive_type():
    assert Utils.compare("test", "test") == True
    assert Utils.compare(1, 1) == True
    assert Utils.compare(1.1, 1.10000000001) == True


def test_compare_nok_primitive_type():
    assert not Utils.compare("test", "test1")
    assert not Utils.compare(1, 2)
    assert not Utils.compare(1.1, 1.101)



def test_compare_nok_array():
    a = [1, 1, 2.10000000001]
    b = [1.0000000001, 1.1, 2.1]
    c = []
    assert not Utils.compare(a, b)
    assert not Utils.compare(c, a)


def test_compare_nok_dict():
    a = {
            "key1" : [1, 1.1, 2.10000000001],
            "key2": "test1",
            "key3" : 0.5
        }
    b = {
            "key1" : [1.0000000001, 1.1, 2.1],
            "key2": "test",
            "key3" : 0.5000000001
        }
    assert not Utils.compare(a, b)


def test_compare_ok_array():
    a = [1, 1.1, 2.10000000001]
    b = [1.0000000001, 1.1, 2.1]    
    assert Utils.compare(a, b) == True
    c,d = [], []
    assert Utils.compare(c, d) == True


def test_compare_ok_dict():
    a = {
            "key1" : [1, 1.1, 2.10000000001],
            "key2": "test",
            "key3" : 0.5
        }
    b = {
            "key1" : [1.0000000001, 1.1, 2.1],
            "key2": "test",
            "key3" : 0.5000000001
        }
    assert Utils.compare(a, b) == True