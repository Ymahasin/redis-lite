# Redis-Lite Implementation in Python

This is a lite implementation of a Redis Client/Server with some of the core commands such as GET, SET, and EXPIRE.

Link to demonstration: TODO

## How to use:
1. Open the command line and change directory to redis/server
2. Run the server with ```$ python3 server.py```

3. Open another Terminal and change directory to redis/client and run the Client with ```$ python3 client.py```
4. Now you can run the commands in the client(s)

## Commmands:

### Ping 
Hit the redis server to check responsiveness
```
$ PING
```

### Echo
Test a get response from the server
```
$ ECHO <value>
```

### Get
Get value for the provided key
```
$ GET <key>
```

### Set
Set a key/value entry within the redis cache
```
$ SET <key> <value>
```

### Expires
Set an expiration time (in seconds) for an entry
```
$ SET <key> <value> EXPIRES <int>
```

### Incr
Increment a numeric value for the provided key
```
$ INCR <key>
```

### Del
Deletes an entry based on the provided key
```
$ DEL <key>
```

### flushall
Clear all entries for this client entry
```
$ flushAll
```

### Exit
Gracefully disconnect the client
```
$ exit
```