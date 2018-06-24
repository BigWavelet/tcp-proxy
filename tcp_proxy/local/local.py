#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Description: local server for tcp-proxy
# Author: bigwavelet

import socket
import logging
import asyncio

from tcp_proxy.proxy.processed_socket import ProcessedSocket

__Author__ = "bigwavelet"
logger = logging.getLogger(__name__)

class LocalServer(ProcessedSocket):
    """
    @Description:
        LocalServer, listening on local_addr, and send data to remoteServer.
    @params:
        loop: asyncio.AbstractEventLoop
        local_addr: local listening address
        remote_addr: remote address
    @returns:
        None
    """
    def __init__(self, local_addr, remote_addr, loop=None):
        super().__init__(loop=loop)
        self.local_addr = local_addr
        self.remote_addr = remote_addr


    def __str__(self):
        return "LocalServer->loop: %s; LocalServer->local_addr: %s; LocalServer->remote_addr: %s" % (
            self.loop, sef.local_addr, self.remote_addr
            )

    async  def listen(self, didListen):
        """
        @Description:
            listening on local address
        @params:
            didListen: callback function
        @returns:
            None
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
            listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            listener.bind(self.local_addr)
            listener.listen(socket.SOMAXCONN)
            listener.setblocking(False)

            logger.info("Listen on %s:%d" % *self.local_addr)

            while True:
                local_conn, address = await self.loop.sock_accept(listener)
                logger.info("Receive from %s:%d" % *address)
                asyncio.ensure_future(self.handle(local_conn))

    async def handle(self, local_conn):
        """
        @Description:
            handle the connection
        @params:
            conn:  socket connection
        """
        remote_conn = await self.connect_remote()

        local2remote = asyncio.ensure_future(
            self.forward(local_conn, remote_conn)
            )

        remote2local = asyncio.ensure_future(
            self.forward(remote_conn, local_conn)
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
            local_conn.close()

        task = asyncio.ensure_future(
            asyncio.gather(local2remote,
                remote2local,
                loop=self.loop,
                return_exceptions=True)
            )

        task.add_done_callback(clean_up)



    async def connect_remote(self):
        """
        @Description:
            create a socket connection that connects to the remote LocalServer
        @params:
            None
        @returns:
            conn: socket connection
        """

        try:
            conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            conn.setblocking(False)
            await self.loop.sock_connect(conn, self.remote_addr)
        except Exception,e:
            raise ConnectionError("failed to connect to the remote server: %s:%d; reason: %s" % (*self.remote_addr, e))

        return conn










