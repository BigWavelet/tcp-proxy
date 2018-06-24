#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Description: config file for tcp-proxy
# Author: bigwavelet

__Author__ = "bigwavelet"

from collections import namedtuple


Address = namedtuple('Address', 'host port')


class InvalidAddrError(Exception):
    """无效的config Addr"""


class InvalidPortError(Exception):
    """无效的config Port"""



remote_host = "0.0.0.0"
remote_port = 6789


local_host = "0.0.0.0"
local_port = 5678

remote_address = Address(remote_host, remote_port)
local_address = Address(local_host, local_port)

BUFFER_SIZE = 1024



