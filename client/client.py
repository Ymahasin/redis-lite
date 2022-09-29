import asyncio

class RedisClient:
    async def connect(self, host, port):
        # read / write to and from TCP stream
        self.r, self.w = await asyncio.open_connection(host, port)

    # set within Redis 
    async def set(self, key, value, exp):        
        self.w.write(f"set {key} {value} {exp}\r\n".encode())
        await self.w.drain()
        return await self._read_reply()

    # get within Redis
    async def get(self, key):
        self.w.write(f"get{key}\r\n".encode())
        await self.w.drain()
        return await self._read_reply()

    # increment an integer value for the corresponding key
    async def increment(self, key):
        self.w.write(f"incr{key}\r\n".encode())
        await self.w.drain()
        return await self._read_reply()

    # helper method that takes any number of args
    async def send(self, *args):
        # for x in args, shorthand
        # convert our array into a string
        resp_args = "".join([f"${len(x)}\r\n{x}\r\n" for x in args])
        # how many items are in the string array
        self.w.write(f"*{len(args)}\r\n{resp_args}".encode())
        await self.w.drain()

        return await self._read_reply()


    # private method to read the Redis server response
    async def _read_reply(self):
        # first look at the prepended tag (+, *, etc.)
        tag = await self.r.read(1) # read 1 byte        

        # Handle bulk string
        if tag == b"$":
            length = b''
            char = b''
            while char != b'\n':
                char = await self.r.read(1)
                length += char
                        
            total_length = int(length[:-1]) + 2

            result = b''
            while len(result) < total_length:                
                result += await self.r.read(total_length-len(result))

            return result[:-2].decode()
        
        # Handle integer
        if tag == b':':            
            result = b''
            char = b''

            while char != b'\n':
                char = await self.r.read(1)
                result += char                                
            return int(result[:-1].decode())
         # Error   
        if tag == b'-':            
            result = b''
            char = b''

            while char != b'\n':
                char = await self.r.read(1)
                result += char                                
            raise Exception(result[:-1].decode())
        # simple string
        if tag == b'+':            
            result = b''
            char = b''

            while char != b'\n':
                char = await self.r.read(1)
                result += char                
                # theres a carridge return char, so we will exclude that from the result
            return result[:-1].decode()
        else:
            message = await self.r.read(100)
            raise Exception(f"Unknown tag: {tag}, message: {message}")


async def main():
    print('Welcome new Redis Client')
    client = RedisClient()    
    HOST = "Yings-MBP.com"
    PORT = 6379
    try:
        await client.connect(HOST, PORT)
    except Exception as e:
        raise SystemExit(f"Could not bind server on host: {HOST} to port: {PORT} because: {e}")

    while True:
        message = input("> ")        
        message = message.lower()
        
        if message == 'exit':            
            print(await client.get(message))
            break   
        elif message == 'ping':            
            print(await client.get(message))
        elif message[0:4] == "echo":              
            print(await client.get(message))   
        elif message[0:3] == "del":              
            print(await client.get(message))
        elif message[0:8] == "flushall":            
            print(await client.get(message))
        elif message[0:3] == "get":                     
            print(await client.get(message[3:]))
        elif message[0:3] == "set":            
            message = message.split(' ')            
            key = message[1]
            val = message[2]                        
            exp = "0"
            if len(message) == 5 and message[3] == 'expires':                
                exp = message[4]
            print(await client.set(key, val, exp)) 
        elif message[0:4] == "incr":            
            print(await client.increment(message[5:]))
        else:            
            print(await client.get(message))


if __name__ == '__main__':
    asyncio.run(main())