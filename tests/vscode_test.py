#!/usr/bin/env python

import json
import unittest
from unittest.mock import patch
from test.support import captured_stdout
from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
from ansible.module_utils.basic import AnsibleModule
from library.vscode import VSCodeModule


def set_module_args(args):
    """
    prepare arguments so that they will be picked up during module creation
    """
    value = json.dumps({"ANSIBLE_MODULE_ARGS": args})
    basic._ANSIBLE_ARGS = to_bytes(value)


class TestVSCodeModule(unittest.TestCase):
    def test_is_extension_installed(self):
        with patch.object(AnsibleModule, "run_command") as mocked_run_command:
            cases = [
                ("hoge", True),
                ("fuga", True),
                ("piyo", True),
                ("not_installed_extension", False),
            ]
            mocked_run_command.return_value = (0, "piyo\nfuga\nhoge", "")

            for case in cases:
                name, installed = case
                set_module_args({"name": name})
                vscode = VSCodeModule()

                expected = (0, installed)
                actual = vscode.is_extension_installed(name)
                self.assertTupleEqual(expected, actual)

    def test_is_extension_installed_when_fail(self):
        with patch.object(AnsibleModule, "run_command") as mocked_run_command:
            name = "hoge"
            mocked_run_command.return_value = (1, "", "error detail")
            set_module_args({"name": name})
            vscode = VSCodeModule()

            expected = (1, False)
            actual = vscode.is_extension_installed(name)
            self.assertTupleEqual(expected, actual)

    def test_extension_install_when_installed(self):
        with patch.object(
            VSCodeModule, "is_extension_installed"
        ) as mocked_is_extension_installed:
            name = "hoge"
            mocked_is_extension_installed.return_value = (0, True)
            set_module_args({"name": name})
            vscode = VSCodeModule()

            expected = (0, False)
            actual = vscode.extension_install(name)
            self.assertTupleEqual(expected, actual)

    def test_extension_install_when_not_installed(self):
        with patch.object(AnsibleModule, "run_command") as mocked_run_command:
            with patch.object(
                VSCodeModule, "is_extension_installed"
            ) as mocked_is_extension_installed:
                name = "hoge"
                stdout = "Found '{0}' in the marketplace.\nInstalling...\nExtension '{0}' is already installed."  # noqa E501
                mocked_run_command.return_value = (0, stdout.format(name), "")
                mocked_is_extension_installed.return_value = (0, False)
                set_module_args({"name": name})
                vscode = VSCodeModule()

                expected = (0, True)
                actual = vscode.extension_install(name)
                self.assertTupleEqual(expected, actual)

    def test_extension_uninstall_when_installed(self):
        with patch.object(AnsibleModule, "run_command") as mocked_run_command:
            with patch.object(
                VSCodeModule, "is_extension_installed"
            ) as mocked_is_extension_installed:
                name = "hoge"
                stdout = "Uninstalling {0}...\nExtension '{0}' was successfully uninstalled!"  # noqa E501
                mocked_run_command.return_value = (0, stdout.format(name), "")
                mocked_is_extension_installed.return_value = (0, True)
                set_module_args({"name": name})
                vscode = VSCodeModule()

                expected = (0, True)
                actual = vscode.extension_uninstall(name)
                self.assertTupleEqual(expected, actual)

    def test_extension_uninstall_when_not_installed(self):
        with patch.object(
            VSCodeModule, "is_extension_installed"
        ) as mocked_is_extension_installed:
            name = "hoge"
            mocked_is_extension_installed.return_value = (0, False)
            set_module_args({"name": name})
            vscode = VSCodeModule()

            expected = (0, False)
            actual = vscode.extension_uninstall(name)
            self.assertTupleEqual(expected, actual)

    def test_main_when_state_present_and_changed(self):
        with captured_stdout() as stdout:
            with patch.object(
                VSCodeModule, "extension_install"
            ) as mocked_extension_install:
                mocked_extension_install.return_value = (0, True)
                name = "hoge"

                try:
                    set_module_args({"name": name, "state": "present"})
                    vscode = VSCodeModule()
                    vscode.main()
                except SystemExit:
                    actual = json.loads(stdout.getvalue())
                    mocked_extension_install.assert_called_with(name)
                    self.assertEqual(True, actual["changed"])
                    self.assertEqual(0, actual["rc"])
                    self.assertEqual(vscode.stderr, actual["stderr"])
                    self.assertEqual(vscode.stdout, actual["stdout"])

    def test_main_when_state_present_and_not_changed(self):
        with captured_stdout() as stdout:
            with patch.object(
                VSCodeModule, "extension_install"
            ) as mocked_extension_install:
                mocked_extension_install.return_value = (0, False)
                name = "hoge"

                try:
                    set_module_args({"name": name, "state": "present"})
                    vscode = VSCodeModule()
                    vscode.main()
                except SystemExit:
                    actual = json.loads(stdout.getvalue())
                    mocked_extension_install.assert_called_with(name)
                    self.assertEqual(False, actual["changed"])
                    self.assertEqual(0, actual["rc"])
                    self.assertEqual(vscode.stderr, actual["stderr"])
                    self.assertEqual(vscode.stdout, actual["stdout"])

    def test_main_when_state_absent_and_changed(self):
        with captured_stdout() as stdout:
            with patch.object(
                VSCodeModule, "extension_uninstall"
            ) as mocked_extension_uninstall:
                mocked_extension_uninstall.return_value = (0, True)
                name = "hoge"

                try:
                    set_module_args({"name": name, "state": "absent"})
                    vscode = VSCodeModule()
                    vscode.main()
                except SystemExit:
                    actual = json.loads(stdout.getvalue())
                    mocked_extension_uninstall.assert_called_with(name)
                    self.assertEqual(True, actual["changed"])
                    self.assertEqual(0, actual["rc"])
                    self.assertEqual(vscode.stderr, actual["stderr"])
                    self.assertEqual(vscode.stdout, actual["stdout"])

    def test_main_when_state_absent_and_not_changed(self):
        with captured_stdout() as stdout:
            with patch.object(
                VSCodeModule, "extension_uninstall"
            ) as mocked_extension_uninstall:
                mocked_extension_uninstall.return_value = (0, False)
                name = "hoge"

                try:
                    set_module_args({"name": name, "state": "absent"})
                    vscode = VSCodeModule()
                    vscode.main()
                except SystemExit:
                    actual = json.loads(stdout.getvalue())
                    mocked_extension_uninstall.assert_called_with(name)
                    self.assertEqual(False, actual["changed"])
                    self.assertEqual(0, actual["rc"])
                    self.assertEqual(vscode.stderr, actual["stderr"])
                    self.assertEqual(vscode.stdout, actual["stdout"])

    def test_run_when_name_not_set(self):
        with captured_stdout() as stdout:

            try:
                set_module_args({})
                VSCodeModule()
            except SystemExit:
                actual = json.loads(stdout.getvalue())
                self.assertEqual(True, actual["failed"])

    def test_run_when_state_1_present(self):
        with captured_stdout() as stdout:

            try:
                set_module_args({"name": "ms-vscode.node-debug2", "state": "present"})
                vscode = VSCodeModule()
                vscode.main()
            except SystemExit:
                actual = json.loads(stdout.getvalue())
                self.assertEqual(True, actual["changed"])
                self.assertEqual(0, actual["rc"])

    def test_run_when_state_2_absent(self):
        with captured_stdout() as stdout:

            try:
                set_module_args({"name": "ms-vscode.node-debug2", "state": "absent"})
                vscode = VSCodeModule()
                vscode.main()
            except SystemExit:
                actual = json.loads(stdout.getvalue())
                self.assertEqual(True, actual["changed"])
                self.assertEqual(0, actual["rc"])


if __name__ == "__main__":
    unittest.main()
