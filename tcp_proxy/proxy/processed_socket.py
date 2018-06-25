#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Description: processed socket for tcp server, i.e. data modified...
# Author: ydbn2153

import socket
import logging
import asyncio

from tcp_proxy import config


__Author__ = "bigwavelet"

BUFFER_SIZE = config.BUFFER_SIZE
logger = logging.getLogger(__name__)


class ProcessedSocket(object):
    """
    @Description:
        ProcessedSocket is a socket, 
        which has the ability to modified the data, for upload(UL) and download(DL) both.

    @params:
        loop: asyncio.AbstractEventLoop
    """

    def __init__(self, loop=None):
        self.loop = loop or asyncio.get_event_loop()


    def __str__(self):
        return "ProcessedSocket->loop:%s" % self.loop

    async def process(self, data, process_type=0):
        '''
        @Description:
            process data, add modify method, cipher here.  ##Todo
        @params:
            data: sock_recv returned data
            process_type: todo
        @returns
            processed_data: bytearray
        '''
        processed_data = bytearray(data)
        processed_data = processed_data.copy()
        return processed_data      


    async def forward(self, src, dst, process_type=0):
        '''
        @Description:
            get data from src, then process data, then forward to dst
        @params:
            src: source socket.socket
            dst: destination socket.socket
            process_type: process type: Todo
        @return:
            None
        ''' 
        logger.debug("process data: %s:%d => %s:%d", *src.getsockname(), *dst.getsockname())

        while True:
            # get raw data from src
            data = await self.receive(src)
            if not data:
                break

            logger.debug("received raw data is: %s", data)
            # process data
            processed_data = await self.process(data, process_type=0)

            logger.debug("processed data is: %s", processed_data)
            # forward processed data to dst
            await self.send(dst, processed_data)

    async def receive(self, conn):
        """
        @Description:
            receive data from the socket connection
        @params:
            conn: socket connection
        @returns:
            recv_data: bytearray
        """
        data = await self.loop.sock_recv(conn, BUFFER_SIZE)
        #logger.debug('receive data from %s:%d, data: %r', *conn.getsockname(), data)
        recv_data = bytearray(data)
        return recv_data

    async def send(self, conn, data):
        """
        @Description:
            send data to the socket connection
        @params:
            conn: socket connection
            data: bytearray data to be sended
        @returns
            None
        """
        await self.loop.sock_sendall(conn, data)
        #logger.debug("send data: %r to %s:%d", data, *conn.getsockname())
