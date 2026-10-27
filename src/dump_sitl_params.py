import time, json, sys
from pymavlink import mavutil
m=mavutil.mavlink_connection('tcp:127.0.0.1:5760'); m.wait_heartbeat(timeout=30)
m.mav.param_request_list_send(m.target_system,m.target_component)
p={}; total=None; last=time.time()
while time.time()-last<8:
    msg=m.recv_match(type='PARAM_VALUE',blocking=True,timeout=1)
    if msg:
        p[msg.param_id]=msg.param_value; total=msg.param_count; last=time.time()
print(len(p),total)
json.dump(p,open(sys.argv[1],'w'),indent=0)
