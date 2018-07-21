###############################################
# import from CPython's "Lib/test/test_uuid.py"
#
# modification
#
# * comment out test for "py_uuid" and "c_uuid"
# * add test for "rs_uuid"
# * disable "uuid safe" related test cases
# * disable test_uuid1_eui64
# * change some exception check
#
###############################################

import unittest.mock
from test import support
import builtins
import contextlib
import io
import os
import shutil
import subprocess

# py_uuid = support.import_fresh_module('uuid', blocked=['_uuid'])
# c_uuid = support.import_fresh_module('uuid', fresh=['_uuid'])
rs_uuid = support.import_fresh_module('su_uuid', fresh=['_uuid'])


def importable(name):
    try:
        __import__(name)
        return True
    except:
        return False


class BaseTestUUID:
    uuid = None

    def test_UUID(self):
        equal = self.assertEqual
        ascending = []
        for (string, curly, hex, bytes, bytes_le, fields, integer, urn,
             time, clock_seq, variant, version) in [
            ('00000000-0000-0000-0000-000000000000',
             '{00000000-0000-0000-0000-000000000000}',
             '00000000000000000000000000000000',
             b'\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0',
             b'\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0',
             (0, 0, 0, 0, 0, 0),
             0,
             'urn:uuid:00000000-0000-0000-0000-000000000000',
             0, 0, self.uuid.RESERVED_NCS, None),
            ('00010203-0405-0607-0809-0a0b0c0d0e0f',
             '{00010203-0405-0607-0809-0a0b0c0d0e0f}',
             '000102030405060708090a0b0c0d0e0f',
             b'\0\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\x0d\x0e\x0f',
             b'\x03\x02\x01\0\x05\x04\x07\x06\x08\t\n\x0b\x0c\x0d\x0e\x0f',
             (0x00010203, 0x0405, 0x0607, 8, 9, 0x0a0b0c0d0e0f),
             0x000102030405060708090a0b0c0d0e0f,
             'urn:uuid:00010203-0405-0607-0809-0a0b0c0d0e0f',
             0x607040500010203, 0x809, self.uuid.RESERVED_NCS, None),
            ('02d9e6d5-9467-382e-8f9b-9300a64ac3cd',
             '{02d9e6d5-9467-382e-8f9b-9300a64ac3cd}',
             '02d9e6d59467382e8f9b9300a64ac3cd',
             b'\x02\xd9\xe6\xd5\x94\x67\x38\x2e\x8f\x9b\x93\x00\xa6\x4a\xc3\xcd',
             b'\xd5\xe6\xd9\x02\x67\x94\x2e\x38\x8f\x9b\x93\x00\xa6\x4a\xc3\xcd',
             (0x02d9e6d5, 0x9467, 0x382e, 0x8f, 0x9b, 0x9300a64ac3cd),
             0x02d9e6d59467382e8f9b9300a64ac3cd,
             'urn:uuid:02d9e6d5-9467-382e-8f9b-9300a64ac3cd',
             0x82e946702d9e6d5, 0xf9b, self.uuid.RFC_4122, 3),
            ('12345678-1234-5678-1234-567812345678',
             '{12345678-1234-5678-1234-567812345678}',
             '12345678123456781234567812345678',
             b'\x12\x34\x56\x78'*4,
             b'\x78\x56\x34\x12\x34\x12\x78\x56\x12\x34\x56\x78\x12\x34\x56\x78',
             (0x12345678, 0x1234, 0x5678, 0x12, 0x34, 0x567812345678),
             0x12345678123456781234567812345678,
             'urn:uuid:12345678-1234-5678-1234-567812345678',
             0x678123412345678, 0x1234, self.uuid.RESERVED_NCS, None),
            ('6ba7b810-9dad-11d1-80b4-00c04fd430c8',
             '{6ba7b810-9dad-11d1-80b4-00c04fd430c8}',
             '6ba7b8109dad11d180b400c04fd430c8',
             b'\x6b\xa7\xb8\x10\x9d\xad\x11\xd1\x80\xb4\x00\xc0\x4f\xd4\x30\xc8',
             b'\x10\xb8\xa7\x6b\xad\x9d\xd1\x11\x80\xb4\x00\xc0\x4f\xd4\x30\xc8',
             (0x6ba7b810, 0x9dad, 0x11d1, 0x80, 0xb4, 0x00c04fd430c8),
             0x6ba7b8109dad11d180b400c04fd430c8,
             'urn:uuid:6ba7b810-9dad-11d1-80b4-00c04fd430c8',
             0x1d19dad6ba7b810, 0xb4, self.uuid.RFC_4122, 1),
            ('6ba7b811-9dad-11d1-80b4-00c04fd430c8',
             '{6ba7b811-9dad-11d1-80b4-00c04fd430c8}',
             '6ba7b8119dad11d180b400c04fd430c8',
             b'\x6b\xa7\xb8\x11\x9d\xad\x11\xd1\x80\xb4\x00\xc0\x4f\xd4\x30\xc8',
             b'\x11\xb8\xa7\x6b\xad\x9d\xd1\x11\x80\xb4\x00\xc0\x4f\xd4\x30\xc8',
             (0x6ba7b811, 0x9dad, 0x11d1, 0x80, 0xb4, 0x00c04fd430c8),
             0x6ba7b8119dad11d180b400c04fd430c8,
             'urn:uuid:6ba7b811-9dad-11d1-80b4-00c04fd430c8',
             0x1d19dad6ba7b811, 0xb4, self.uuid.RFC_4122, 1),
            ('6ba7b812-9dad-11d1-80b4-00c04fd430c8',
             '{6ba7b812-9dad-11d1-80b4-00c04fd430c8}',
             '6ba7b8129dad11d180b400c04fd430c8',
             b'\x6b\xa7\xb8\x12\x9d\xad\x11\xd1\x80\xb4\x00\xc0\x4f\xd4\x30\xc8',
             b'\x12\xb8\xa7\x6b\xad\x9d\xd1\x11\x80\xb4\x00\xc0\x4f\xd4\x30\xc8',
             (0x6ba7b812, 0x9dad, 0x11d1, 0x80, 0xb4, 0x00c04fd430c8),
             0x6ba7b8129dad11d180b400c04fd430c8,
             'urn:uuid:6ba7b812-9dad-11d1-80b4-00c04fd430c8',
             0x1d19dad6ba7b812, 0xb4, self.uuid.RFC_4122, 1),
            ('6ba7b814-9dad-11d1-80b4-00c04fd430c8',
             '{6ba7b814-9dad-11d1-80b4-00c04fd430c8}',
             '6ba7b8149dad11d180b400c04fd430c8',
             b'\x6b\xa7\xb8\x14\x9d\xad\x11\xd1\x80\xb4\x00\xc0\x4f\xd4\x30\xc8',
             b'\x14\xb8\xa7\x6b\xad\x9d\xd1\x11\x80\xb4\x00\xc0\x4f\xd4\x30\xc8',
             (0x6ba7b814, 0x9dad, 0x11d1, 0x80, 0xb4, 0x00c04fd430c8),
             0x6ba7b8149dad11d180b400c04fd430c8,
             'urn:uuid:6ba7b814-9dad-11d1-80b4-00c04fd430c8',
             0x1d19dad6ba7b814, 0xb4, self.uuid.RFC_4122, 1),
            ('7d444840-9dc0-11d1-b245-5ffdce74fad2',
             '{7d444840-9dc0-11d1-b245-5ffdce74fad2}',
             '7d4448409dc011d1b2455ffdce74fad2',
             b'\x7d\x44\x48\x40\x9d\xc0\x11\xd1\xb2\x45\x5f\xfd\xce\x74\xfa\xd2',
             b'\x40\x48\x44\x7d\xc0\x9d\xd1\x11\xb2\x45\x5f\xfd\xce\x74\xfa\xd2',
             (0x7d444840, 0x9dc0, 0x11d1, 0xb2, 0x45, 0x5ffdce74fad2),
             0x7d4448409dc011d1b2455ffdce74fad2,
             'urn:uuid:7d444840-9dc0-11d1-b245-5ffdce74fad2',
             0x1d19dc07d444840, 0x3245, self.uuid.RFC_4122, 1),
            ('e902893a-9d22-3c7e-a7b8-d6e313b71d9f',
             '{e902893a-9d22-3c7e-a7b8-d6e313b71d9f}',
             'e902893a9d223c7ea7b8d6e313b71d9f',
             b'\xe9\x02\x89\x3a\x9d\x22\x3c\x7e\xa7\xb8\xd6\xe3\x13\xb7\x1d\x9f',
             b'\x3a\x89\x02\xe9\x22\x9d\x7e\x3c\xa7\xb8\xd6\xe3\x13\xb7\x1d\x9f',
             (0xe902893a, 0x9d22, 0x3c7e, 0xa7, 0xb8, 0xd6e313b71d9f),
             0xe902893a9d223c7ea7b8d6e313b71d9f,
             'urn:uuid:e902893a-9d22-3c7e-a7b8-d6e313b71d9f',
             0xc7e9d22e902893a, 0x27b8, self.uuid.RFC_4122, 3),
            ('eb424026-6f54-4ef8-a4d0-bb658a1fc6cf',
             '{eb424026-6f54-4ef8-a4d0-bb658a1fc6cf}',
             'eb4240266f544ef8a4d0bb658a1fc6cf',
             b'\xeb\x42\x40\x26\x6f\x54\x4e\xf8\xa4\xd0\xbb\x65\x8a\x1f\xc6\xcf',
             b'\x26\x40\x42\xeb\x54\x6f\xf8\x4e\xa4\xd0\xbb\x65\x8a\x1f\xc6\xcf',
             (0xeb424026, 0x6f54, 0x4ef8, 0xa4, 0xd0, 0xbb658a1fc6cf),
             0xeb4240266f544ef8a4d0bb658a1fc6cf,
             'urn:uuid:eb424026-6f54-4ef8-a4d0-bb658a1fc6cf',
             0xef86f54eb424026, 0x24d0, self.uuid.RFC_4122, 4),
            ('f81d4fae-7dec-11d0-a765-00a0c91e6bf6',
             '{f81d4fae-7dec-11d0-a765-00a0c91e6bf6}',
             'f81d4fae7dec11d0a76500a0c91e6bf6',
             b'\xf8\x1d\x4f\xae\x7d\xec\x11\xd0\xa7\x65\x00\xa0\xc9\x1e\x6b\xf6',
             b'\xae\x4f\x1d\xf8\xec\x7d\xd0\x11\xa7\x65\x00\xa0\xc9\x1e\x6b\xf6',
             (0xf81d4fae, 0x7dec, 0x11d0, 0xa7, 0x65, 0x00a0c91e6bf6),
             0xf81d4fae7dec11d0a76500a0c91e6bf6,
             'urn:uuid:f81d4fae-7dec-11d0-a765-00a0c91e6bf6',
             0x1d07decf81d4fae, 0x2765, self.uuid.RFC_4122, 1),
            ('fffefdfc-fffe-fffe-fffe-fffefdfcfbfa',
             '{fffefdfc-fffe-fffe-fffe-fffefdfcfbfa}',
             'fffefdfcfffefffefffefffefdfcfbfa',
             b'\xff\xfe\xfd\xfc\xff\xfe\xff\xfe\xff\xfe\xff\xfe\xfd\xfc\xfb\xfa',
             b'\xfc\xfd\xfe\xff\xfe\xff\xfe\xff\xff\xfe\xff\xfe\xfd\xfc\xfb\xfa',
             (0xfffefdfc, 0xfffe, 0xfffe, 0xff, 0xfe, 0xfffefdfcfbfa),
             0xfffefdfcfffefffefffefffefdfcfbfa,
             'urn:uuid:fffefdfc-fffe-fffe-fffe-fffefdfcfbfa',
             0xffefffefffefdfc, 0x3ffe, self.uuid.RESERVED_FUTURE, None),
            ('ffffffff-ffff-ffff-ffff-ffffffffffff',
             '{ffffffff-ffff-ffff-ffff-ffffffffffff}',
             'ffffffffffffffffffffffffffffffff',
             b'\xff'*16,
             b'\xff'*16,
             (0xffffffff, 0xffff, 0xffff, 0xff, 0xff, 0xffffffffffff),
             0xffffffffffffffffffffffffffffffff,
             'urn:uuid:ffffffff-ffff-ffff-ffff-ffffffffffff',
             0xfffffffffffffff, 0x3fff, self.uuid.RESERVED_FUTURE, None),
            ]:
            equivalents = []
            # Construct each UUID in several different ways.
            for u in [self.uuid.UUID(string), self.uuid.UUID(curly), self.uuid.UUID(hex),
                      self.uuid.UUID(bytes=bytes), self.uuid.UUID(bytes_le=bytes_le),
                      self.uuid.UUID(fields=fields), self.uuid.UUID(int=integer),
                      self.uuid.UUID(urn)]:
                # Test all conversions and properties of the UUID object.
                equal(str(u), string)
                equal(int(u), integer)
                equal(u.bytes, bytes)
                equal(u.bytes_le, bytes_le)
                equal(u.fields, fields)
                equal(u.time_low, fields[0])
                equal(u.time_mid, fields[1])
                equal(u.time_hi_version, fields[2])
                equal(u.clock_seq_hi_variant, fields[3])
                equal(u.clock_seq_low, fields[4])
                equal(u.node, fields[5])
                equal(u.hex, hex)
                equal(u.int, integer)
                equal(u.urn, urn)
                equal(u.time, time)
                equal(u.clock_seq, clock_seq)
                equal(u.variant, variant)
                equal(u.version, version)
                equivalents.append(u)

            # Different construction methods should give the same UUID.
            for u in equivalents:
                for v in equivalents:
                    equal(u, v)

            # Bug 7380: "bytes" and "bytes_le" should give the same type.
            equal(type(u.bytes), builtins.bytes)
            equal(type(u.bytes_le), builtins.bytes)

            ascending.append(u)

        # Test comparison of UUIDs.
        for i in range(len(ascending)):
            for j in range(len(ascending)):
                equal(i < j, ascending[i] < ascending[j])
                equal(i <= j, ascending[i] <= ascending[j])
                equal(i == j, ascending[i] == ascending[j])
                equal(i > j, ascending[i] > ascending[j])
                equal(i >= j, ascending[i] >= ascending[j])
                equal(i != j, ascending[i] != ascending[j])

        # Test sorting of UUIDs (above list is in ascending order).
        resorted = ascending[:]
        resorted.reverse()
        resorted.sort()
        equal(ascending, resorted)

    def test_exceptions(self):
        badvalue = lambda f: self.assertRaises(ValueError, f)
        badtype = lambda f: self.assertRaises(TypeError, f)
        badoverflow = lambda f: self.assertRaises(OverflowError, f)
        badattr = lambda f: self.assertRaises(AttributeError, f)


        # Badly formed hex strings.
        badvalue(lambda: self.uuid.UUID(''))
        badvalue(lambda: self.uuid.UUID('abc'))
        badvalue(lambda: self.uuid.UUID('1234567812345678123456781234567'))
        badvalue(lambda: self.uuid.UUID('123456781234567812345678123456789'))
        badvalue(lambda: self.uuid.UUID('123456781234567812345678z2345678'))

        # Badly formed bytes.
        badtype(lambda: self.uuid.UUID(bytes='abc'))
        badtype(lambda: self.uuid.UUID(bytes='\0'*15))
        badtype(lambda: self.uuid.UUID(bytes='\0'*17))

        # Badly formed bytes_le.
        badtype(lambda: self.uuid.UUID(bytes_le='abc'))
        badtype(lambda: self.uuid.UUID(bytes_le='\0'*15))
        badtype(lambda: self.uuid.UUID(bytes_le='\0'*17))

        # Badly formed fields.
        badvalue(lambda: self.uuid.UUID(fields=(1,)))
        badvalue(lambda: self.uuid.UUID(fields=(1, 2, 3, 4, 5)))
        badvalue(lambda: self.uuid.UUID(fields=(1, 2, 3, 4, 5, 6, 7)))

        # Field values out of range.
        badoverflow(lambda: self.uuid.UUID(fields=(-1, 0, 0, 0, 0, 0)))
        badoverflow(lambda: self.uuid.UUID(fields=(0x100000000, 0, 0, 0, 0, 0)))
        badoverflow(lambda: self.uuid.UUID(fields=(0, -1, 0, 0, 0, 0)))
        badoverflow(lambda: self.uuid.UUID(fields=(0, 0x10000, 0, 0, 0, 0)))
        badoverflow(lambda: self.uuid.UUID(fields=(0, 0, -1, 0, 0, 0)))
        badoverflow(lambda: self.uuid.UUID(fields=(0, 0, 0x10000, 0, 0, 0)))
        badoverflow(lambda: self.uuid.UUID(fields=(0, 0, 0, -1, 0, 0)))
        badoverflow(lambda: self.uuid.UUID(fields=(0, 0, 0, 0x100, 0, 0)))
        badoverflow(lambda: self.uuid.UUID(fields=(0, 0, 0, 0, -1, 0)))
        badoverflow(lambda: self.uuid.UUID(fields=(0, 0, 0, 0, 0x100, 0)))
        badoverflow(lambda: self.uuid.UUID(fields=(0, 0, 0, 0, 0, -1)))
        badvalue(lambda: self.uuid.UUID(fields=(0, 0, 0, 0, 0, 0x1000000000000)))

        # Version number out of range.
        badvalue(lambda: self.uuid.UUID('00'*16, version=0))
        badvalue(lambda: self.uuid.UUID('00'*16, version=6))

        # Integer value out of range.
        badoverflow(lambda: self.uuid.UUID(int=-1))
        badoverflow(lambda: self.uuid.UUID(int=1<<128))

        # Must supply exactly one of hex, bytes, fields, int.
        h, b, f, i = '00'*16, b'\0'*16, (0, 0, 0, 0, 0, 0), 0
        self.uuid.UUID(h)
        self.uuid.UUID(hex=h)
        self.uuid.UUID(bytes=b)
        self.uuid.UUID(bytes_le=b)
        self.uuid.UUID(fields=f)
        self.uuid.UUID(int=i)

        # Wrong number of arguments (positional).
        badtype(lambda: self.uuid.UUID())
        badtype(lambda: self.uuid.UUID(h, b))
        badtype(lambda: self.uuid.UUID(h, b, b))
        badtype(lambda: self.uuid.UUID(h, b, b, f))
        badtype(lambda: self.uuid.UUID(h, b, b, f, i))

        # Duplicate arguments.
        for hh in [[], [('hex', h)]]:
            for bb in [[], [('bytes', b)]]:
                for bble in [[], [('bytes_le', b)]]:
                    for ii in [[], [('int', i)]]:
                        for ff in [[], [('fields', f)]]:
                            args = dict(hh + bb + bble + ii + ff)
                            if len(args) != 0:
                                print(h, args)
                                badtype(lambda: self.uuid.UUID(h, **args))
                            if len(args) != 1:
                                print(h, args)
                                badtype(lambda: self.uuid.UUID(**args))

        # Immutability.
        u = self.uuid.UUID(h)
        badattr(lambda: setattr(u, 'hex', h))
        badattr(lambda: setattr(u, 'bytes', b))
        badattr(lambda: setattr(u, 'bytes_le', b))
        badattr(lambda: setattr(u, 'fields', f))
        badattr(lambda: setattr(u, 'int', i))
        badattr(lambda: setattr(u, 'time_low', 0))
        badattr(lambda: setattr(u, 'time_mid', 0))
        badattr(lambda: setattr(u, 'time_hi_version', 0))
        badattr(lambda: setattr(u, 'time_hi_version', 0))
        badattr(lambda: setattr(u, 'clock_seq_hi_variant', 0))
        badattr(lambda: setattr(u, 'clock_seq_low', 0))
        badattr(lambda: setattr(u, 'node', 0))

        # Comparison with a non-UUID object
        badtype(lambda: u < object())
        badtype(lambda: u > object())

    def test_getnode(self):
        node1 = self.uuid.getnode()
        self.assertTrue(0 < node1 < (1 << 48), '%012x' % node1)

        # Test it again to ensure consistency.
        node2 = self.uuid.getnode()
        self.assertEqual(node1, node2, '%012x != %012x' % (node1, node2))

    # # bpo-32502: UUID1 requires a 48-bit identifier, but hardware identifiers
    # # need not necessarily be 48 bits (e.g., EUI-64).
    # def test_uuid1_eui64(self):
    #     # Confirm that uuid.getnode ignores hardware addresses larger than 48
    #     # bits. Mock out each platform's *_getnode helper functions to return
    #     # something just larger than 48 bits to test. This will cause
    #     # uuid.getnode to fall back on uuid._random_getnode, which will
    #     # generate a valid value.
    #     too_large_getter = lambda: 1 << 48
    #     with unittest.mock.patch.multiple(
    #         self.uuid,
    #         _node=None,  # Ignore any cached node value.
    #         _NODE_GETTERS_WIN32=[too_large_getter],
    #         _NODE_GETTERS_UNIX=[too_large_getter],
    #     ):
    #         node = self.uuid.getnode()
    #     self.assertTrue(0 < node < (1 << 48), '%012x' % node)

    #     # Confirm that uuid1 can use the generated node, i.e., the that
    #     # uuid.getnode fell back on uuid._random_getnode() rather than using
    #     # the value from too_large_getter above.
    #     try:
    #         self.uuid.uuid1(node=node)
    #     except ValueError as e:
    #         self.fail('uuid1 was given an invalid node ID')

    def test_uuid1(self):
        equal = self.assertEqual

        # Make sure uuid1() generates UUIDs that are actually version 1.
        for u in [self.uuid.uuid1() for i in range(10)]:
            equal(u.variant, self.uuid.RFC_4122)
            equal(u.version, 1)
            # self.assertIn(u.is_safe, {self.uuid.SafeUUID.safe,
            #                           self.uuid.SafeUUID.unsafe,
            #                           self.uuid.SafeUUID.unknown})

        # Make sure the generated UUIDs are actually unique.
        uuids = {}
        for u in [self.uuid.uuid1() for i in range(1000)]:
            uuids[u] = 1
        equal(len(uuids.keys()), 1000)

        # Make sure the supplied node ID appears in the UUID.
        u = self.uuid.uuid1(0)
        equal(u.node, 0)
        u = self.uuid.uuid1(0x123456789abc)
        equal(u.node, 0x123456789abc)
        u = self.uuid.uuid1(0xffffffffffff)
        equal(u.node, 0xffffffffffff)

        # Make sure the supplied clock sequence appears in the UUID.
        u = self.uuid.uuid1(0x123456789abc, 0)
        equal(u.node, 0x123456789abc)
        equal(((u.clock_seq_hi_variant & 0x3f) << 8) | u.clock_seq_low, 0)
        u = self.uuid.uuid1(0x123456789abc, 0x1234)
        equal(u.node, 0x123456789abc)
        equal(((u.clock_seq_hi_variant & 0x3f) << 8) |
                         u.clock_seq_low, 0x1234)
        u = self.uuid.uuid1(0x123456789abc, 0x3fff)
        equal(u.node, 0x123456789abc)
        equal(((u.clock_seq_hi_variant & 0x3f) << 8) |
                         u.clock_seq_low, 0x3fff)

    # # bpo-29925: On Mac OS X Tiger, self.uuid.uuid1().is_safe returns
    # # self.uuid.SafeUUID.unknown
    # @support.requires_mac_ver(10, 5)
    # @unittest.skipUnless(os.name == 'posix', 'POSIX-only test')
    # def test_uuid1_safe(self):
    #     if not self.uuid._has_uuid_generate_time_safe:
    #         self.skipTest('requires uuid_generate_time_safe(3)')

    #     u = self.uuid.uuid1()
    #     # uuid_generate_time_safe() may return 0 or -1 but what it returns is
    #     # dependent on the underlying platform support.  At least it cannot be
    #     # unknown (unless I suppose the platform is buggy).
    #     self.assertNotEqual(u.is_safe, self.uuid.SafeUUID.unknown)

    # @contextlib.contextmanager
    # def mock_generate_time_safe(self, safe_value):
    #     """
    #     Mock uuid._generate_time_safe() to return a given *safe_value*.
    #     """
    #     if os.name != 'posix':
    #         self.skipTest('POSIX-only test')
    #     self.uuid._load_system_functions()
    #     f = self.uuid._generate_time_safe
    #     if f is None:
    #         self.skipTest('need uuid._generate_time_safe')
    #     with unittest.mock.patch.object(self.uuid, '_generate_time_safe',
    #                                     lambda: (f()[0], safe_value)):
    #         yield

    # @unittest.skipUnless(os.name == 'posix', 'POSIX-only test')
    # def test_uuid1_unknown(self):
    #     # Even if the platform has uuid_generate_time_safe(), let's mock it to
    #     # be uuid_generate_time() and ensure the safety is unknown.
    #     with self.mock_generate_time_safe(None):
    #         u = self.uuid.uuid1()
    #         self.assertEqual(u.is_safe, self.uuid.SafeUUID.unknown)

    # @unittest.skipUnless(os.name == 'posix', 'POSIX-only test')
    # def test_uuid1_is_safe(self):
    #     with self.mock_generate_time_safe(0):
    #         u = self.uuid.uuid1()
    #         self.assertEqual(u.is_safe, self.uuid.SafeUUID.safe)

    # @unittest.skipUnless(os.name == 'posix', 'POSIX-only test')
    # def test_uuid1_is_unsafe(self):
    #     with self.mock_generate_time_safe(-1):
    #         u = self.uuid.uuid1()
    #         self.assertEqual(u.is_safe, self.uuid.SafeUUID.unsafe)

    # @unittest.skipUnless(os.name == 'posix', 'POSIX-only test')
    # def test_uuid1_bogus_return_value(self):
    #     with self.mock_generate_time_safe(3):
    #         u = self.uuid.uuid1()
    #         self.assertEqual(u.is_safe, self.uuid.SafeUUID.unknown)

    def test_uuid3(self):
        equal = self.assertEqual

        # Test some known version-3 UUIDs.
        for u, v in [(self.uuid.uuid3(self.uuid.NAMESPACE_DNS, 'python.org'),
                      '6fa459ea-ee8a-3ca4-894e-db77e160355e'),
                     (self.uuid.uuid3(self.uuid.NAMESPACE_URL, 'http://python.org/'),
                      '9fe8e8c4-aaa8-32a9-a55c-4535a88b748d'),
                     (self.uuid.uuid3(self.uuid.NAMESPACE_OID, '1.3.6.1'),
                      'dd1a1cef-13d5-368a-ad82-eca71acd4cd1'),
                     (self.uuid.uuid3(self.uuid.NAMESPACE_X500, 'c=ca'),
                      '658d3002-db6b-3040-a1d1-8ddd7d189a4d'),
                    ]:
            equal(u.variant, self.uuid.RFC_4122)
            equal(u.version, 3)
            equal(u, self.uuid.UUID(v))
            equal(str(u), v)

    def test_uuid4(self):
        equal = self.assertEqual

        # Make sure uuid4() generates UUIDs that are actually version 4.
        for u in [self.uuid.uuid4() for i in range(10)]:
            equal(u.variant, self.uuid.RFC_4122)
            equal(u.version, 4)

        # Make sure the generated UUIDs are actually unique.
        uuids = {}
        for u in [self.uuid.uuid4() for i in range(1000)]:
            uuids[u] = 1
        equal(len(uuids.keys()), 1000)

    def test_uuid5(self):
        equal = self.assertEqual

        # Test some known version-5 UUIDs.
        for u, v in [(self.uuid.uuid5(self.uuid.NAMESPACE_DNS, 'python.org'),
                      '886313e1-3b8a-5372-9b90-0c9aee199e5d'),
                     (self.uuid.uuid5(self.uuid.NAMESPACE_URL, 'http://python.org/'),
                      '4c565f0d-3f5a-5890-b41b-20cf47701c5e'),
                     (self.uuid.uuid5(self.uuid.NAMESPACE_OID, '1.3.6.1'),
                      '1447fa61-5277-5fef-a9b3-fbc6e44f4af3'),
                     (self.uuid.uuid5(self.uuid.NAMESPACE_X500, 'c=ca'),
                      'cc957dd1-a972-5349-98cd-874190002798'),
                    ]:
            equal(u.variant, self.uuid.RFC_4122)
            equal(u.version, 5)
            equal(u, self.uuid.UUID(v))
            equal(str(u), v)

    @unittest.skipUnless(os.name == 'posix', 'requires Posix')
    def testIssue8621(self):
        # On at least some versions of OSX self.uuid.uuid4 generates
        # the same sequence of UUIDs in the parent and any
        # children started using fork.
        fds = os.pipe()
        pid = os.fork()
        if pid == 0:
            os.close(fds[0])
            value = self.uuid.uuid4()
            os.write(fds[1], value.hex.encode('latin-1'))
            os._exit(0)

        else:
            os.close(fds[1])
            self.addCleanup(os.close, fds[0])
            parent_value = self.uuid.uuid4().hex
            os.waitpid(pid, 0)
            child_value = os.read(fds[0], 100).decode('latin-1')

            self.assertNotEqual(parent_value, child_value)


# class TestUUIDWithoutExtModule(BaseTestUUID, unittest.TestCase):
#     uuid = py_uuid

# @unittest.skipUnless(c_uuid, 'requires the C _uuid module')
# class TestUUIDWithExtModule(BaseTestUUID, unittest.TestCase):
#     uuid = c_uuid

class TestUUIDWithRustExtModule(BaseTestUUID, unittest.TestCase):
    uuid = rs_uuid

class BaseTestInternals:
    uuid = None

    @unittest.skipUnless(os.name == 'posix', 'requires Posix')
    def test_find_mac(self):
        data = '''
fake hwaddr
cscotun0  Link encap:UNSPEC  HWaddr 00-00-00-00-00-00-00-00-00-00-00-00-00-00-00-00
eth0      Link encap:Ethernet  HWaddr 12:34:56:78:90:ab
'''

        popen = unittest.mock.MagicMock()
        popen.stdout = io.BytesIO(data.encode())

        with unittest.mock.patch.object(shutil, 'which',
                                        return_value='/sbin/ifconfig'):
            with unittest.mock.patch.object(subprocess, 'Popen',
                                            return_value=popen):
                mac = self.uuid._find_mac(
                    command='ifconfig',
                    args='',
                    hw_identifiers=[b'hwaddr'],
                    get_index=lambda x: x + 1,
                )

        self.assertEqual(mac, 0x1234567890ab)

    def check_node(self, node, requires=None):
        if requires and node is None:
            self.skipTest('requires ' + requires)
        hex = '%012x' % node
        if support.verbose >= 2:
            print(hex, end=' ')
        self.assertTrue(0 < node < (1 << 48),
                        "%s is not an RFC 4122 node ID" % hex)

    @unittest.skipUnless(os.name == 'posix', 'requires Posix')
    def test_ifconfig_getnode(self):
        node = self.uuid._ifconfig_getnode()
        self.check_node(node, 'ifconfig')

    @unittest.skipUnless(os.name == 'posix', 'requires Posix')
    def test_ip_getnode(self):
        node = self.uuid._ip_getnode()
        self.check_node(node, 'ip')

    @unittest.skipUnless(os.name == 'posix', 'requires Posix')
    def test_arp_getnode(self):
        node = self.uuid._arp_getnode()
        self.check_node(node, 'arp')

    @unittest.skipUnless(os.name == 'posix', 'requires Posix')
    def test_lanscan_getnode(self):
        node = self.uuid._lanscan_getnode()
        self.check_node(node, 'lanscan')

    @unittest.skipUnless(os.name == 'posix', 'requires Posix')
    def test_netstat_getnode(self):
        node = self.uuid._netstat_getnode()
        self.check_node(node, 'netstat')

    @unittest.skipUnless(os.name == 'nt', 'requires Windows')
    def test_ipconfig_getnode(self):
        node = self.uuid._ipconfig_getnode()
        self.check_node(node, 'ipconfig')

    @unittest.skipUnless(importable('win32wnet'), 'requires win32wnet')
    @unittest.skipUnless(importable('netbios'), 'requires netbios')
    def test_netbios_getnode(self):
        node = self.uuid._netbios_getnode()
        self.check_node(node)

    def test_random_getnode(self):
        node = self.uuid._random_getnode()
        # The multicast bit, i.e. the least significant bit of first octet,
        # must be set for randomly generated MAC addresses.  See RFC 4122,
        # $4.1.6.
        self.assertTrue(node & (1 << 40), '%012x' % node)
        self.check_node(node)

        node2 = self.uuid._random_getnode()
        self.assertNotEqual(node2, node, '%012x' % node)

    @unittest.skipUnless(os.name == 'posix', 'requires Posix')
    def test_unix_getnode(self):
        if not importable('_uuid') and not importable('ctypes'):
            self.skipTest("neither _uuid extension nor ctypes available")
        try: # Issues 1481, 3581: _uuid_generate_time() might be None.
            node = self.uuid._unix_getnode()
        except TypeError:
            self.skipTest('requires uuid_generate_time')
        self.check_node(node, 'unix')

    @unittest.skipUnless(os.name == 'nt', 'requires Windows')
    @unittest.skipUnless(importable('ctypes'), 'requires ctypes')
    def test_windll_getnode(self):
        node = self.uuid._windll_getnode()
        self.check_node(node)


# class TestInternalsWithoutExtModule(BaseTestInternals, unittest.TestCase):
#     uuid = py_uuid

# @unittest.skipUnless(c_uuid, 'requires the C _uuid module')
# class TestInternalsWithExtModule(BaseTestInternals, unittest.TestCase):
#     uuid = c_uuid


if __name__ == '__main__':
    unittest.main()
