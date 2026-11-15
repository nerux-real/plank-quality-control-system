# Programma, kura izveido PLC serveri, izmantojot klasisko S7 protokolu. Pieņem ienākošus savienojumus un ļauj klientiem lasīt un rakstīt datus PLC atmiņā.
from s7 import Server, SrvArea, util
import time

server_port=1102

server = Server()

def increment(data, offset, size):
    value = int.from_bytes(data[offset:offset+size], byteorder='big')
    data[offset:offset+size] = (value+1).to_bytes(size, byteorder='big')

try:
    db1_size=5 #5 baiti
    db1_data=bytearray(db1_size) #datu baitu masīvs 5 baitu garumā
    server.register_area(SrvArea.DB, 1, db1_data) #reģistrē datu bloku DB1 ar 5 baitu lielu masīvu
    db2_size=32 #32 baiti
    db2_data=bytearray(db2_size) #datu baitu masīvs 32 baitu garumā
    server.register_area(SrvArea.DB, 2, db2_data) #reģistrē datu bloku DB2 ar 32 baitu lielu masīvu

    server.start(tcp_port=server_port)
    print(f"PLC simulācijas serveris klausās portu: {server_port}.")
    while True:
        time.sleep(0.05)
        heartbeat = int.from_bytes(db2_data[0:2], byteorder='big')
        db2_data[0:2] = ((heartbeat+1)%32768).to_bytes(2, byteorder='big')
        status = db1_data[4]
        if status == 1:
            util.set_bool(db2_data, 4, 0, False) #reset ack
            command = int.from_bytes(db1_data[0:2], byteorder='big')
            detail_num = int.from_bytes(db1_data[2:4], byteorder='big')
            db1_data[4] = 0
            db2_data[8:10] = detail_num.to_bytes(2, byteorder='big')
            if command==1:
                print("PASS")
                increment(db2_data, 12, 4)
                db2_data[10:12] = command.to_bytes(2, byteorder='big')
            elif command==2:
                print("REJECT")
                increment(db2_data, 16, 4)
                db2_data[10:12] = command.to_bytes(2, byteorder='big')
            else:
                print("UNKNOWN COMMAND")
                db2_data[20:22] = (4).to_bytes(2, byteorder='big')
            util.set_bool(db2_data, 4, 0, True) #ack
except Exception as e:
    print(f"Kļūda PLC simulācijas serverī: {e}")
except KeyboardInterrupt:
    print("PLC simulācijas serveris tiek apturēts.")
finally:
    server.stop()