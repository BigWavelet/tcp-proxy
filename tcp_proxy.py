#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Description: main function for tcp-proxy
# Author: bigwavelet

import sys
import socket
import logging
import asyncio

from optparse import OptionParser

from tcp_proxy import config
from tcp_proxy.proxy.processed_socket import ProcessedSocket
from tcp_proxy.local.local import LocalServer
from tcp_proxy.remote.remote import RemoteServer


__Author__ = "bigwavelet"
logger = logging.getLogger(__name__)



log_level = logging.INFO
log_fmt = '[%(levelname)s][%(asctime)s](%(filename)s:%(lineno)d) - %(message)s'
log_datefmt = '%Y-%m-%d %H:%M:%S'
log_stream = sys.stdout
logging.basicConfig(level=log_level, format=log_fmt, datefmt=log_datefmt,
                    stream=log_stream)



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

def run_remote_server():
    loop = asyncio.get_event_loop()

    remote_addr = config.remote_address

    remote_server = RemoteServer(
        loop=loop,
        remote_addr=remote_addr
        )

    asyncio.ensure_future(remote_server.listen())
    loop.run_forever()

if __name__ == "__main__":

    parser = OptionParser(usage='python %prog [optinos]')
    parser.add_option("-l", dest="local", action='store_true', help="run local server.")
    parser.add_option("-r", dest="remote", action='store_true', help="run remote server.")
    parser.add_option('-d', dest='debug', action='store_true', default=False,
                        help='debug')
    options, args = parser.parse_args()

    if options.debug:
        logging.root.setLevel(logging.DEBUG)

    if not options.local and not options.remote:
        logger.info("sorry, you must specify which server to start, local or remote.")
    if options.local and options.remote:
        logger.info("sorry, you can not run local server and remote server at the same time.")
        exit(1)
    if options.local:
        logger.info("start to run local server.")
        run_local_server()
    if options.remote:
        logger.info("start to run remote server.")
        run_remote_server()