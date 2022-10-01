from typing import List, Tuple


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
