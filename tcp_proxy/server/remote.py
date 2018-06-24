#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Description: remote server for tcp-proxy
# Author: bigwavelet

import socket
import logging
import asyncio

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

    async def listen(self, didListen):
    """
    @Description:
        listening on remote_addr
    @params:
        didListen: callable function
    @returns:
        None
    """