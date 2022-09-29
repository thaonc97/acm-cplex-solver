
from typing import List, Tuple


class Utils:

    @staticmethod 
    def check_continous_list(list_a : List[int], start = 0) -> Tuple[bool, int]:
        """ Hàm kiểm tra xem 1 list số nguyên có phải liên tục hay không 

        Args:
            listA (List[int]): list int
            start (int, optional): giá trị đầu tiên của chuỗi, mặc định bằng 0

        Returns:
            bool: list có liên tục hay không
            int: chỉ số tiếp theo sau chỉ mục cuối cùng
        """

        if(len(list_a)==0 and start==0):
            return True, 0

        max_a = max(list_a)
        len_a = len(list_a)

        if(list_a[0]!= start or list_a[len_a-1]!=max_a):
            return False, -1
        
        if(max_a-start+1 != len_a):
            return False, -1
        
        return True, max_a+1

    
    @staticmethod 
    def check_duplicate(list_a : list) -> bool:
        seen = set()
        uniq = []
        for x in list_a:
            if x not in seen:
                uniq.append(x)
                seen.add(x)
        
        return len(list_a)!=len(seen)
