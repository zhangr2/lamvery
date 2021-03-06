# -*- coding: utf-8 -*-

from unittest import TestCase
from nose.tools import eq_, raises
from mock import Mock, patch

from lamvery.actions.set_alias import SetAliasAction


def default_args():
    args = Mock()
    args.conf_file = '.lamvery.yml'
    args.dry_run = True
    args.publish = True
    args.alias = None
    args.version = None
    args.target = None
    return args


class SetAliasActionTestCase(TestCase):

    @patch('lamvery.actions.base.LambdaClient')
    @raises(Exception)
    def test_action_not_exists(self, c):
        action = SetAliasAction(default_args())
        action.get_alias_name = Mock(return_value=None)
        action.action()

    @patch('lamvery.actions.base.LambdaClient')
    def test_action(self, c):

        # Dry run
        args = default_args()
        args.alias = 'foo'
        action = SetAliasAction(args)
        action.action()

        # No dry run
        args = default_args()
        args.alias = 'foo'
        args.dry_run = False

        # New
        with patch('lamvery.actions.base.LambdaClient') as c:
            c.get_alias = Mock(return_value={})
            action = SetAliasAction(args)
            action.action()

        # Update
        with patch('lamvery.actions.base.LambdaClient') as c:
            c.get_alias = Mock(return_value={'FunctionVersion': '1'})
            action = SetAliasAction(args)
            action.action()

    def test_print_alias_diff(self):
        action = SetAliasAction(default_args())
        action._print_alias_diff('name', {'FunctionVersion': 1}, 2)

    def test_get_version(self):
        action = SetAliasAction(default_args())
        eq_(action.get_version('foo'), '$LATEST')

        args = default_args()
        args.version = '1'
        action = SetAliasAction(args)
        eq_(action.get_version('foo'), '1')

        c = Mock()
        c.get_alias = Mock(return_value={'FunctionVersion': '2'})
        args = default_args()
        args.target = 'foo'
        action = SetAliasAction(args)
        action.get_lambda_client = Mock(return_value=c)
        eq_(action.get_version('foo'), '2')

    @raises(Exception)
    def test_get_version_target_not_exists(self):
        c = Mock()
        c.get_alias = Mock(return_value={})
        args = default_args()
        args.target = 'foo'
        action = SetAliasAction(args)
        action.get_lambda_client = Mock(return_value=c)
        action.get_version('foo')
