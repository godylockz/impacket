#!/usr/bin/env python3
# -- coding: utf-8 --
# Impacket - Collection of Python classes for working with network protocols.
#
# Copyright Fortra, LLC and its affiliated companies
#
# All rights reserved.
#
# This software is provided under a slightly modified version
# of the Apache Software License. See the accompanying LICENSE file
# for more information.

# Imports
import unittest
from unittest.mock import Mock

from impacket.dcerpc.v5 import rprn


class RPRNHelperTests(unittest.TestCase):
    def test_xcv_data_helper_builds_request(self):
        dce = Mock()
        handle = rprn.PRINTER_HANDLE()
        handle['Data'] = b'A' * 20

        response = rprn.hRpcXcvData(
            dce,
            handle,
            'AssocIppDirected',
            b'i\x00p\x00p\x00\x00\x00',
            cbOutputData=128,
        )

        self.assertIs(response, dce.request.return_value)
        request = dce.request.call_args[0][0]
        self.assertIsInstance(request, rprn.RpcXcvData)
        self.assertEqual(request['hXcv'], b'A' * 20)
        self.assertEqual(request['pszDataName'], 'AssocIppDirected\x00')
        self.assertEqual(request['cbInputData'], 8)
        self.assertEqual(request['cbOutputData'], 128)
        self.assertEqual(bytes(request['pInputData']), b'i\x00p\x00p\x00\x00\x00')

    def test_xcv_data_opnum_round_trip(self):
        request = rprn.RpcXcvData()
        request['hXcv'] = b'B' * 20
        request['pszDataName'] = 'AssocIppDirected\x00'
        request['pInputData'] = b'x\x00\x00\x00'
        request['cbInputData'] = 4
        request['cbOutputData'] = 0
        request['pdwStatus'] = 0

        parsed = rprn.RpcXcvData(request.getData())

        self.assertEqual(rprn.OPNUMS[88], (rprn.RpcXcvData, rprn.RpcXcvDataResponse))
        self.assertEqual(parsed['hXcv'], b'B' * 20)
        self.assertEqual(parsed['pszDataName'], 'AssocIppDirected\x00')
        self.assertEqual(parsed['cbInputData'], 4)
        self.assertEqual(b''.join(parsed['pInputData']), b'x\x00\x00\x00')


if __name__ == '__main__':
    unittest.main()
