#!/usr/bin/env python3
# -- coding: utf-8 --
# Impacket - Collection of Python classes for working with network protocols.
#
# This software is provided under a slightly modified version
# of the Apache Software License. See the accompanying LICENSE file
# for more information.
#
# Imports
import unittest

from impacket.krb5.constants import ChecksumTypes, KDCOptions, PreAuthenticationDataTypes, etype_display_name


class KerberosConstantsTests(unittest.TestCase):
    def test_checksum_identifiers(self):
        self.assertEqual(ChecksumTypes.rsa_md4_des.value, 3)
        self.assertEqual(ChecksumTypes.des_mac.value, 4)
        self.assertEqual(ChecksumTypes.hmac_sha256_128_aes128.value, 19)
        self.assertEqual(ChecksumTypes.hmac_sha384_192_aes256.value, 20)

    def test_preauthentication_identifiers_and_alias(self):
        self.assertEqual(PreAuthenticationDataTypes.PA_SVR_REFERRAL_INFO, PreAuthenticationDataTypes.PA_USE_SPECIFIED_KVNO)
        self.assertEqual(PreAuthenticationDataTypes.PA_SERVER_REFERRAL.value, 25)
        self.assertEqual(PreAuthenticationDataTypes.PA_OTP_CHALLENGE.value, 141)
        self.assertEqual(KDCOptions.anonymous.value, 16)

    def test_display_names_preserve_fork_extensions(self):
        self.assertEqual(etype_display_name(20), 'aes256-cts-hmac-sha384-192')
        self.assertEqual(etype_display_name(-135), 'rc4-hmac-old-exp')
        self.assertEqual(etype_display_name(0xffffff79), 'rc4-hmac-old-exp')
