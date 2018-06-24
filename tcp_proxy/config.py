#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Description: config file for tcp-proxy
# Author: bigwavelet

__Author__ = "bigwavelet"

from collections import namedtuple

Config = namedtuple('Config',
                    'remoteHost remotePort localHost localPort')


Address = namedtuple('Host', 'Port')


class InvalidAddrError(Exception):
    """无效的config Addr"""


class InvalidPortError(Exception):
    """无效的config Port"""



remoteHost = "0.0.0.0"
remotePort = 6789


localHost = "0.0.0.0"
localPort = 5678

remoteAddress = Address(remoteHost, remotePort)
localAddress = Address(localHost, localPort)



