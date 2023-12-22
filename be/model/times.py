from be.model.order import Order
import time

def get_time_stamp(): #get timestamp for auto cancelling orders that are not paid in time
    cur_time_stamp = time.time()
    return int(cur_time_stamp)

time_limit = 20 # 订单存活时间
unpaid_orders = {}

def add_unpaid_order(orderID):
    unpaid_orders[orderID] = get_time_stamp()
    return 200, "ok"

def delete_unpaid_order(orderID):
    try:
        unpaid_orders.pop(orderID)
    except BaseException as e:
        return 530, "{}".format(str(e))
    return 200, "ok"

def check_order_time(order_time):
    cur_time = get_time_stamp()
    time_diff = cur_time - order_time
    if time_diff > time_limit:
        return False
    else:
        return True
    
def time_exceed_delete():
    del_temp=[]
    order = Order()
    for (oid,tim) in unpaid_orders.items():
        if check_order_time(tim) == False:
            del_temp.append(oid)  
    for oid in del_temp:
        delete_unpaid_order(oid)
        order.cancel_order(oid)
    return 0