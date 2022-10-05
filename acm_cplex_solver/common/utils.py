from array import array
import string
from typing import List, Tuple
import numpy as np

class Utils:

    @staticmethod 
    def check_continuous_list(list_a : List[int], start = 0) -> Tuple[int, int]:
        """ Hàm kiểm tra xem 1 list số nguyên có phải liên tục hay không 

        Args:
            listA (List[int]): list int
            start (int, optional): giá trị đầu tiên của chuỗi, mặc định bằng 0

        Returns:
            int: list có liên tục hay không, 0 = liên tục, 1 không liên tục, 2 = list rỗng
            int: chỉ số tiếp theo sau chỉ mục cuối cùng
        """

        len_a = len(list_a)
        if(len_a==0):
            return 2,start

        for i in range(len_a):
            if(i+start!=list_a[i]):
                return 1,start
        
        return 0, list_a[len_a-1]+1

    
    @staticmethod 
    def check_duplicate(list_a : list) -> bool:
        seen = set()
        uniq = []
        for x in list_a:
            if x not in seen:
                uniq.append(x)
                seen.add(x)
        
        return len(list_a)!=len(seen)

    
    @staticmethod 
    def compare(value_a, value_b) -> bool:
        """ So sánh 2 dict, hoặc 2 giá trị float, string, int

        Args:
            value_a (_type_): int, float, string, dict
            value_b (_type_): int, float, string, dict

        Returns:
            bool: True, Flase
        """
        if(type(value_a) != type(value_b)):
            return False
        
        if(type(value_a) == str):
            return value_a == value_b
        elif(type(value_a) == int):
            return value_a==value_b
        elif(type(value_a)==float):
            return np.isclose(value_a, value_b)
        elif(type(value_a)==list):
            if(len(value_a) == 0 and len(value_b) == 0):
                return True     
            try:
                return (not np.any(np.isclose(value_a, value_b) == False))
            except:       
                return False            
        elif(type(value_a)==dict):
            if(value_a.keys()!=value_b.keys()):
                return False
            for key in value_a.keys():
                if(not Utils.compare(value_a[key], value_b[key])):
                    return False
            return True
        else:
            raise Exception("Compare is not support this type !")
