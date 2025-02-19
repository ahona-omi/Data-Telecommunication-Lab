import os
import socket
import threading
import struct

IP = '127.0.0.1'
PORT = 4489
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"
SERVER_DATA_PATH = "server_data"
dic = {
    "www.google.com": ('100.20.8.1', 'A', 86400),
    "www.cse.du.ac.bd": ('192.0.2.3', 'A', 86400),
    "www.yahoo.com": ('1.2.3.9999', "A", 86400)
}


def encode_msg(message):
    try:
        data = message.split()
        name = data[0]
        type = data[1]
        flag = 0
        q = 0
        a = 1
        auth_rr = 0
        add_rr = 0
        ms = (name + ' ' + type + ' ' + data[2] + ' ' + data[3]).encode('utf-8')
        packed_data = struct.pack(f"6H{len(ms)}s", 50, flag, q, a, auth_rr, add_rr, ms)
        return packed_data
    except Exception as e:
        print("Error occurred while encoding message:", e)
        return None


def decode_msg(msg):
    try:
        header = struct.unpack("6H", msg[:12])
        ms = msg[12:].decode('utf-8')
        print('\n After Decoding')
        print({header}, {ms})
        ms = ms.split()
        return ms[1], ms[4]
    except Exception as e:
        print("Error occurred while decoding message:", e)
        return None, None


def handle_client(data, addr, server):
    try:
        print(data)
        msg = encode_msg(str(data + ' ' + dic[data][0] + ' ' + dic[data][1] + ' ' + str(dic[data][2])))
        if msg:
            server.sendto(msg, addr)
    except KeyError:
        print(f"Requested domain '{data}' not found in authoritative DNS.")
    except Exception as e:
        print("ERROR: ", str(e))


def main():
    print("[STARTING] auth Server is starting")
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind(ADDR)
    print(f"[LISTENING] auth Server is listening on {IP}:{PORT}.")

    while True:
        try:
            data, addr = server.recvfrom(SIZE)
            data = data.decode(FORMAT)
            handle_client(data, addr, server)
            print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")
        except KeyboardInterrupt:
            print("Server terminated by user.")
            break
        except Exception as e:
            print("Error occurred:", e)

    server.close()


if __name__ == "__main__":
    main()
