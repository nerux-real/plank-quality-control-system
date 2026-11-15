#Ļauj viegli nolasīt visus datu blokus (DB1, DB2) no PLC servera, izmantojot S7 protokolu.
from s7 import Client, util

client = Client()
try:
    client.connect("127.0.0.1", 0, 1, tcp_port=1102)
    print("Savienojums ar PLC serveri izveidots.")
    print("DB1 Data: ", client.db_read(1, 0, 5))
    print("DB2 Data: ", client.db_read(2, 0, 32))
    print("============================================")
    data = client.db_read(1, 0, 5)
    print(f"""DB1 data decoded:
    cmd_code: {util.get_int(data, 0)}
    part_id: {util.get_int(data, 2)}
    new_cmd: {util.get_bool(data, 4, 0)}""")
    print("============================================")
    data = client.db_read(2, 0, 22)
    print(f"""DB2 data decoded:
    heartbeat: {util.get_int(data, 0)}
    line_state: {util.get_int(data, 2)}
    cmd_ack: {util.get_bool(data, 4, 0)}
    part_at_inspection: {util.get_bool(data, 4, 1)}
    part_at_gate: {util.get_bool(data, 4, 2)}
    pusher_active: {util.get_bool(data, 4, 3)}
    waiting_part_id: {util.get_int(data, 6)}
    last_part_id: {util.get_int(data, 8)}
    last_result: {util.get_int(data, 10)}
    count_passed: {util.get_dint(data, 12)}
    count_rejected: {util.get_dint(data, 16)}
    fault_code: {util.get_int(data, 20)}""")
    print("============================================")
except Exception as e:
    print(f"Kļūda savienojoties ar PLC serveri: {e}")
except KeyboardInterrupt:
    print("Savienojums ar PLC serveri tiek pārtraukts.")
finally:
    client.disconnect()
