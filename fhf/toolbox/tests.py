import doctest
import unittest

from Testing import ZopeTestCase as ztc

from Products.Five import zcml
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite
from Products.PloneTestCase.layer import onsetup

import fhf.toolbox

OPTION_FLAGS = doctest.NORMALIZE_WHITESPACE | \
               doctest.ELLIPSIS

ptc.setupPloneSite(products=['fhf.toolbox'])


class TestCase(ptc.PloneTestCase):

    class layer(PloneSite):

        @classmethod
        def setUp(cls):
            zcml.load_config('configure.zcml',
              fhf.toolbox)

        @classmethod
        def tearDown(cls):
            pass


def test_suite():
    return unittest.TestSuite([

        # Unit tests
        #doctestunit.DocFileSuite(
        #    'README.txt', package='fhf.toolbox',
        #    setUp=testing.setUp, tearDown=testing.tearDown),

        #doctestunit.DocTestSuite(
        #    module='fhf.toolbox.mymodule',
        #    setUp=testing.setUp, tearDown=testing.tearDown),


        # Integration tests that use PloneTestCase
        ztc.ZopeDocFileSuite(
            'INTEGRATION.txt',
            package='fhf.toolbox',
            optionflags = OPTION_FLAGS,
            test_class=TestCase),

        # -*- extra stuff goes here -*-

        # Integration tests for Tool
        ztc.ZopeDocFileSuite(
            'Tool.txt',
            package='fhf.toolbox',
            optionflags = OPTION_FLAGS,
            test_class=TestCase),


        # Integration tests for Toolbox
        ztc.ZopeDocFileSuite(
            'Toolbox.txt',
            package='fhf.toolbox',
            optionflags = OPTION_FLAGS,
            test_class=TestCase),


        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
