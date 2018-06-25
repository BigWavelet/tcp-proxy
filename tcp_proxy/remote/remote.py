#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Description: remote server for tcp-proxy
# Author: bigwavelet

import socket
import logging
import asyncio

from tcp_proxy import config
from tcp_proxy.proxy.processed_socket import ProcessedSocket

__Author__ = "bigwavelet"
logger = logging.getLogger(__name__)


class RemoteServer(ProcessedSocket):
    """
    @Description:
        RemoteServer, listening on remote_addr, and send data to localServer.
    @params:
        loop: asyncio.AbstractEventLoop
        remote_addr: remote  listening address
    @returns:
        None
    """

    def __init__(self, loop, remote_addr):
        super().__init__(loop=loop)
        self.remote_addr = remote_addr

    async def listen(self):
        """
        @Description:
            listening on remote_addr
        @params:
            None
        @returns:
            None
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
            listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            listener.setblocking(False)
            listener.bind(self.remote_addr)
            listener.listen(socket.SOMAXCONN)

            logger.info("Listen on %s:%d" % self.remote_addr)

            while True:
                remote_conn, address = await self.loop.sock_accept(listener)
                #logger.info("Receive from %s", address)
                asyncio.ensure_future(self.handle(remote_conn))


    async def handle(self, remote_conn):
        """
        @Description:
            handle data from local server, should handle SOCKS5 protocol
            More information about SOCK5 protocol, please refer to https://www.ietf.org/rfc/rfc1928.txt
        @params:
            remote_conn: socket connection
        @returns:
            None
        """
        
        ## receive data from local server 
        data = await self.receive(remote_conn)

        ## check protocol version, 1st byte
        """
        +----+----------+----------+
        |VER | NMETHODS | METHODS  |
        +----+----------+----------+
        | 1  |    1     | 1 to 255 |
        +----+----------+----------+
        """
        if not data or not (data[0] == 0x05):
            remote_conn.close()
            logger.debug("socks5 protocol error: the first byte is %s", data[0])
            return

        ## then send the (protocol version, method) to the local server
        #  here method is 0x00: No Authentication required
        """
        +----+--------+
        |VER | METHOD |
        +----+--------+
        | 1  |   1    |
        +----+--------+
        """
        await self.send(remote_conn, bytearray((0x05, 0x00)))

        ## handle message body
        """
        The SOCKS request is formed as follows:
            +----+-----+-------+------+----------+----------+
            |VER | CMD |  RSV  | ATYP | DST.ADDR | DST.PORT |
            +----+-----+-------+------+----------+----------+
            | 1  |  1  | X'00' |  1   | Variable |    2     |
            +----+-----+-------+------+----------+----------+
        Where:

          o  VER    protocol version: X'05'
          o  CMD
             o  CONNECT X'01'
             o  BIND X'02'
             o  UDP ASSOCIATE X'03'
          o  RSV    RESERVED
          o  ATYP   address type of following address
             o  IP V4 address: X'01'
             o  DOMAINNAME: X'03'
             o  IP V6 address: X'04'
          o  DST.ADDR       desired destination address
          o  DST.PORT desired destination port in network octet
             order
        """
        data = await self.receive(remote_conn)
        if len(data) < 7:
            remote_conn.close()
            logger.debug("socks5 protocol error, data length is :%d", len(data))
            return

        VER, CMD, RSV, ATYP, DST_PORT = data[0], data[1], data[2], data[3], data[-2:]

        if VER != 0x5:
            remote_conn.close()
            return

        if CMD != 0x1:
            remote_conn.close()
            return

        real_port = int(DST_PORT.hex(), 16)
        real_host = None
        real_addr_family = None
        if ATYP == 0x01:  # ipv4
            start = 4
            length = 4
            real_host = socket.inet_ntop(socket.AF_INET, data[start:start+length])
            real_addr = config.Address(host=real_host, port=real_port)
            real_addr_family = socket.AF_INET
        elif data[3] == 0x03: # ipv4, domain
            real_host = data[5:-2].decode()
            real_addr = config.Address(host=real_host, port=real_port)
        elif data[3] == 0x04: # ipv6
            start = 4
            length = 16
            real_host = socket.inet_ntop(socket.AF_INET6, data[start:start+length])
            real_addr = (real_host, real_port, 0, 0)
            real_addr_family = socket.AF_INET6
        else:
            connection.close()
            return
        logger.debug("Real Address info: %s:%d; address family: %s", real_addr, real_addr_family)

        if real_addr_family:
            try:
                real_conn = socket.socket(family=real_addr_family, type=socket.SOCK_STREAM)
                real_conn.setblocking(False)
                await self.loop.sock_connect(real_conn, real_addr)
            except Exception as err:
                if real_conn is not None:
                    real_conn.close()
                    real_conn = None
                    logger.error("fail to create real connection socket:%s:%d; Reason:%s", real_addr, err)
        else:
            for item in await self.loop.getaddrinfo(real_addr.host, real_addr.port):
                real_addr_family, socket_type, protocol, _, real_addr = item
                try:
                    real_conn = socket.socket(real_addr_family, socket_type, protocol)
                    real_conn.setblocking(False)
                    await self.loop.sock_connect(real_conn, real_addr)
                except Exception as err:
                    if real_conn is not None:
                        real_conn.close()
                        real_conn = None
                        logger.error("fail to create real connection socket:%s:%d; Reason:%s", real_addr, err)

        if real_addr_family is None:
            logger.error("fail to create real connection socket:%s:%d; Reason: real_addr_family is None", real_addr)
            return

        ## then the remote server send data to the local server as follows:
        """
            +----+-----+-------+------+----------+----------+
            |VER | REP |  RSV  | ATYP | BND.ADDR | BND.PORT |
            +----+-----+-------+------+----------+----------+
            | 1  |  1  | X'00' |  1   | Variable |    2     |
            +----+-----+-------+------+----------+----------+

        Where:

            o  VER    protocol version: X'05'
            o  REP    Reply field:
                o  X'00' succeeded
                o  X'01' general SOCKS server failure
                o  X'02' connection not allowed by ruleset
                o  X'03' Network unreachable
                o  X'04' Host unreachable
                o  X'05' Connection refused
                o  X'06' TTL expired
                o  X'07' Command not supported
                o  X'08' Address type not supported
                o  X'09' to X'FF' unassigned
            o  RSV    RESERVED
            o  ATYP   address type of following address
        """

        data = bytearray((0x05, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00))
        await self.send(remote_conn, data)


        remote2real = asyncio.ensure_future(
            self.forward(remote_conn, real_conn)
            )

        real2remote = asyncio.ensure_future(
            self.forward(real_conn, remote_conn)
            )

        def clean_up(task):
            """
            @Description:
                clean up the socket connection after connected.
            @params:
                task: asyncio task
            @returns:
                None
            """
            remote_conn.close()
            real_conn.close()

        task = asyncio.ensure_future(
            asyncio.gather(remote2real,
                remote2real,
                loop=self.loop,
                return_exceptions=True)
            )

        task.add_done_callback(clean_up)













