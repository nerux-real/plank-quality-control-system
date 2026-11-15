#connect AI model + vision
#Right now for test just manual input
from s7 import Client

client = Client()
i=1
try:
    client.connect("127.0.0.1", 0, 1, tcp_port=1102)
    print("Savienojums ar PLC serveri izveidots.")
    while True:
        user_input = input("Ievadiet dēļa rezultātu (1 vai 2), lai ierakstītu PLC atmiņā (vai 'exit' lai izietu): ") #laikus kmr nav ai model un vision pieslēgts
        if user_input.lower() == 'exit':
            break
        if user_input not in ['1', '2']:
            print("Nederīga ievade. Lūdzu, ievadiet 1 vai 2.")
            continue
        client.db_write(1, 0, int(user_input).to_bytes(2, byteorder='big')) #ierakstīt datus PLC atmiņā DB1, sākot no 0 baita
        client.db_write(1, 2, int(i).to_bytes(2, byteorder='big'))
        client.db_write(1, 4, (1).to_bytes(1, byteorder='big'))
        print("Dati ierakstīti PLC atmiņā.")
        result = client.db_read(1, 0, 2)
        print("Nolasītie dati no PLC atmiņas - Rezultāts: ", result, "Verdict: ", "PASS" if result == b'\x00\x01' else "DROP")
        print("Nolasītie dati no PLC atmiņas - Numurs: ", int.from_bytes(client.db_read(1, 2, 2), byteorder='big'))
        print("Nolasītie dati no PLC atmiņas - Statuss: ", int.from_bytes(client.db_read(1, 4, 1), byteorder='big'))
        i += 1
except Exception as e:
    print(f"Kļūda savienojoties ar PLC serveri: {e}")
except KeyboardInterrupt:
    print("Savienojums ar PLC serveri tiek pārtraukts.")
finally:
    client.disconnect()
