import socket 
import argparse
import threading
import time
import math

parser = argparse.ArgumentParser(description = "Server for Redis app")

parser.add_argument('--host', metavar = 'host', type = str, nargs = '?', default = socket.gethostname())
parser.add_argument('--port', metavar = "port", type = int, nargs = "?", default = 6379)
args = parser.parse_args()

print(f"Reddis Server is running on: {args.host} on port: {args.port}")

sck = socket.socket()
sck.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

try:
    sck.bind((args.host, args.port))
    sck.listen(5)    
except Exception as e:
    raise SystemExit(f"Could not bind server on host: {args.host} to port: {args.port} because: {e}")

cache = {}
timers = []

def onNewClient(client, connection):
    ip = connection[0]
    port = connection[1]

    print(f"New connection made from IP: {ip} and PORT: {port}")    
        
    while True:                        
        message = client.recv(1024)        
        req = message.decode('utf-8')
        print(f"{port}: {req}")         
        if len(timers) > 0:     
            check_timers(port)
        end = read_request(req, port, client)

        if end == 1:
            break

    print(f"{port} has gracefully disconnected")
    client.close()


def check_timers(port):            
    for timer in range(len(timers)):
        entry = timers[timer]        
        for port, key in entry.items():                        
            exp = cache[port][key]["expires"]                    
            startTime = cache[port][key]["startTime"]                          
            timeLeft = math.floor(time.time()) - math.floor(int(startTime))                                        
            if timeLeft > int(exp):
                del cache[port][key]
                del timers[timer]            


def read_request(req, port, client):    
    if req[3:7] == "exit":
        client.sendall("+Goodbye\r\n".encode('utf-8'))
        return 1

    elif req[3:7] == "ping":             
        client.sendall("+pong\r\n".encode('utf-8'))            

    elif req[3:11] == 'flushall':        
        cache[port] = {}
        client.sendall("+OK\r\n".encode('utf-8'))

    elif req[3:7] == "echo":                             
        res = req[8:].strip()                             
        length = len(res)
        client.sendall(f"${length}\r\n{res}\r\n".encode('utf-8'))
    
    elif req[3:6] == "del":                  
        entry = req[7:].strip()                             
        handle_delete(entry, port, client)        
    
    # handle array - .send()
    elif req[0:1] == "*":                                            
        handle_array(req.split(' '), client)        

    elif req[0:3] == "get":                        
        res = req[4:len(req)-2]             
        handle_get(res, port, client)
    
    # set with simple string
    elif req[0:3] == "set":             
        key = req.split(' ')[1]
        val = req.split(' ')[2]                
        exp = req.split(' ')[3]           
        handle_set(key, val, exp[:len(exp)-2], port, client)                                                      

    # handle increment integer   
    elif req[0:4] == "incr":            
        res = req[4:].strip()                    
        handle_incr(res, port, client)
 
    else:                     
        client.sendall("+No match\r\n".encode('utf-8'))


def handle_delete(key, port, client):
    if port in cache:
        if key in cache[port]:    
            del cache[port][key]
            client.sendall(f"+OK\r\n".encode('utf-8'))
    else:
        client.sendall(":-1\r\n".encode('utf-8'))


def handle_array(array, client):
    # TODO: complete array implementation
    client.sendall(f"$5\r\narray\r\n".encode('utf-8'))


def handle_incr(res, port, client):
    if port in cache:                
        if res in cache[port]:            
            try:
                val = int(cache[port][res][res]) + 1  
                cache[port][res][res] = str(val)
                client.sendall(f":{val}\r\n".encode('utf-8'))
            except ValueError as e:
                client.sendall(f"+Cannot increment non-integer entries\r\n".encode('utf-8'))
        else:                    
            client.sendall(f"+Entry does not exist\r\n".encode('utf-8'))    
    else:                
        client.sendall(f"+Entry does not exist\r\n".encode('utf-8'))


def handle_set(key, val, expires, port, client):
    if int(expires) > 0:
        timers.append({port: key})

    if port in cache:        
        cache[port][key] = {key: val.strip(), "expires": expires, "startTime": time.time()}        
    else:
        cache[port] = {            
            key : {key: val.strip(), "expires": expires, "startTime": time.time()}
        }        
    client.sendall(f"+OK\r\n".encode('utf-8'))     


def handle_get(res, port, client):    
    if port in cache:                                                         
        if res in cache[port]:                         
            valLength = len(cache[port][res][res])
            client.sendall(f"${valLength}\r\n{cache[port][res][res]}\r\n".encode('utf-8'))    
        else: 
            client.sendall(":-1\r\n".encode('utf-8'))                                   
    else:        
        client.sendall(":-1\r\n".encode('utf-8'))

while True:
    try:
        client, ip = sck.accept()            
        threading._start_new_thread(onNewClient, (client, ip))
    except KeyboardInterrupt as e:
        print(f"Gracefully shutting down the server")
        break        
    except Exception as e:
        print(f"Server crashed. {e}")
        break

sck.close()

