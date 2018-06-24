#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Description: main function for tcp-proxy
# Author: bigwavelet

import socket
import logging
import asyncio

from tcp_proxy import config
from tcp_proxy.proxy.processed_socket import ProcessedSocket
from tcp_proxy.local.local import LocalServer
from tcp_proxy.remote.remote import RemoteServer


__Author__ = "bigwavelet"
logger = logging.getLogger(__name__)



def run_local_server():
    loop = asyncio.get_event_loop()

    local_addr = config.local_address
    remote_addr = config.remote_address

    local_server = LocalServer(
        loop=loop,
        local_addr=local_addr,
        remote_addr=remote_addr)

    asyncio.ensure_future(local_server.listen())
    loop.run_forever()

if __name__ == "__main__":
	run_local_server()
