Validate

function index_continous_check(list: int[], start : int = 0) -> end : int
Kiểm tra xem 1 list có liên tục không, bắt đầu từ start = 0 default, trả về int là số cuối cùng, -1 nếu ko liên tục

-campaigns
class_b_c
total >= 0, nearly equal
t0-1 = index_continous_check(class_b_c if network) >= 0
T-1 =  index_continous_check(class_b_c if domain, t0) >= 0

class_a 
index_continous_check(class_a, T) >= T

cả 2 :

weights.weight >= 0, weights[i].date <= U
dates có 2 phần tử, dates[0]<= dates[1]
min(dates[0]) = 0, max(dates[1]) = U-1
max(place_ids[i]) <= K, min(place_ids[i]) >= 0, place_ids ko duplicate id




- places
+ max(id) = K-1
views[i]>=0, len(views) = U, đủ views của U ngày
ctrs[i] thuộc đoạn [0,1], len(ctrs) >= max(campaigns.type)
share_rate thuộc đoạn [0,1]


- kết hợp
, 