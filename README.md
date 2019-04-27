# ansible-role-vscode

[![Build Status](https://travis-ci.org/hidoo/ansible-role-vscode.svg?branch=master)](https://travis-ci.org/hidoo/ansible-role-vscode)

> Ansible role that setup Visual Studio Code.

## Installation

```sh
$ ansible-galaxy install git+https://github.com/hidoo/ansible-role-vscode
```

## Usage

```yml
roles:
  - ansible-role-vscode

vars:
  vscode:

    # skip install visual studio code or not (default: no)
    skip_install: yes

    # list of extensions to install (default state: present)
    extensions:
      - { name: EditorConfig.EditorConfig }
      - { name: file-icons.file-icons, state: absent }
```

## Test

install Visual Studio Code before testting.

```
$ brew install visual-studio-code
```

```sh
$ pipenv run test:lint
$ pipenv run test:unit
```

## License

MIT
