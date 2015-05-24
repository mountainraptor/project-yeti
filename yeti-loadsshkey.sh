#!/bin/bash

if [ ! -f "${HOME}/.ssh/id_rsa.pub" ]; then
	echo "No default ssh key found in ~/.ssh/id_rsa.pub"
	exit 0
fi

SSH_KEY="$(cat "${HOME}/.ssh/id_rsa.pub")"

ssh root@192.168.1.1 "echo ${SSH_KEY} >> /etc/dropbear/authorized_keys"
