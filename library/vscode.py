#!/usr/bin/env python

from ansible.module_utils.basic import AnsibleModule


class VSCodeModule:
    def __init__(self):
        self.module = AnsibleModule(
            argument_spec={
                "name": {"type": "str", "required": True},
                "state": {"choices": ["present", "absent"], "default": "present"},
            },
            supports_check_mode=True,
        )
        self.stdout = ""
        self.stderr = ""

    def is_extension_installed(self, name):
        rc, stdout, stderr, installed = (0, "", "", False)
        command = "code --list-extensions"
        rc, stdout, stderr = self.module.run_command(command)

        if rc == 0 and stdout.find(name) >= 0:
            installed = True

        self.stdout, self.stderr = stdout, stderr
        return (rc, installed)

    def extension_install(self, name):
        rc, stdout, stderr, changed = (0, "", "", False)
        command = "code --install-extension {0}".format(name)
        rc, installed = self.is_extension_installed(name)

        if rc == 0 and not installed:
            rc, stdout, stderr = self.module.run_command(command)
            changed = True

        self.stdout, self.stderr = stdout, stderr
        return (rc, changed)

    def extension_uninstall(self, name):
        rc, stdout, stderr, changed = (0, "", "", False)
        command = "code --uninstall-extension {0}".format(name)
        rc, installed = self.is_extension_installed(name)

        if rc == 0 and installed:
            rc, stdout, stderr = self.module.run_command(command)
            changed = True

        self.stdout, self.stderr = stdout, stderr
        return (rc, changed)

    def main(self):
        rc, changed = (0, False)
        is_check_mode = self.module.check_mode

        # skip processing when check_mode is yes
        if is_check_mode:
            self.module.exit_json(changed=False)

        name = self.module.params["name"]
        state = self.module.params["state"]

        if state == "present":
            rc, changed = self.extension_install(name)
        if state == "absent":
            rc, changed = self.extension_uninstall(name)

        if rc == 0:
            self.module.exit_json(
                changed=changed, rc=rc, stdout=self.stdout, stderr=self.stderr
            )
        else:
            self.module.fail_json(
                msg="error", rc=rc, stdout=self.stdout, stderr=self.stderr
            )


# run main when main scope
if __name__ == "__main__":
    vscode = VSCodeModule()
    vscode.main()
