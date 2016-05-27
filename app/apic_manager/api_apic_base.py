"""
*************************************************************************
 Copyright (c) 2016 Cisco Systems, Inc.  All rights reserved.
*************************************************************************
Sets connections with APIC controller using the API. This class is for operations
that are not supported in the Cobra SDK
"""


class apic_base:
    def __init__(self):
        self.session = None
        self.moDir = None
        self.configReq = None
        self.uniMo = None


