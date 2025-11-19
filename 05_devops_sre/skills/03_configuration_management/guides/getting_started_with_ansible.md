# Getting Started with Ansible - Complete Guide

## Overview

Ansible is an agentless configuration management tool that uses SSH to configure systems declaratively. This guide covers everything from installation to advanced patterns used in production environments.

## Table of Contents

1. [Installation and Setup](#installation-and-setup)
2. [Core Concepts](#core-concepts)
3. [Writing Your First Playbook](#writing-your-first-playbook)
4. [Inventory Management](#inventory-management)
5. [Variables and Templates](#variables-and-templates)
6. [Roles and Organization](#roles-and-organization)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

## Installation and Setup

### Installing Ansible

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install ansible

# CentOS/RHEL
sudo yum install epel-release
sudo yum install ansible

# macOS
brew install ansible

# Python pip (all platforms)
pip install ansible

# Verify installation
ansible --version
```

### Initial Configuration

Create Ansible configuration file:

```bash
mkdir -p ~/.ansible
cat > ~/.ansible/ansible.cfg << 'EOF'
[defaults]
inventory = ./inventory
remote_user = deploy
host_key_checking = False
retry_files_enabled = False
gathering = smart
fact_caching = jsonfile
fact_caching_connection = /tmp/ansible_facts
fact_caching_timeout = 3600

[privilege_escalation]
become = True
become_method = sudo
become_user = root
become_ask_pass = False

[ssh_connection]
pipelining = True
ssh_args = -o ControlMaster=auto -o ControlPersist=60s
EOF
```

### SSH Setup

Configure SSH keys for passwordless authentication:

```bash
# Generate SSH key (if you don't have one)
ssh-keygen -t ed25519 -C "ansible@example.com"

# Copy key to target servers
ssh-copy-id user@server1.example.com
ssh-copy-id user@server2.example.com

# Test connection
ssh user@server1.example.com 'echo "Connection successful"'
```

## Core Concepts

### Ad-Hoc Commands

Test Ansible without writing playbooks:

```bash
# Ping all hosts
ansible all -m ping

# Check disk space
ansible all -m shell -a 'df -h'

# Install package
ansible web_servers -m apt -a 'name=nginx state=present' --become

# Restart service
ansible web_servers -m systemd -a 'name=nginx state=restarted' --become

# Copy file
ansible all -m copy -a 'src=/local/file dest=/remote/file mode=0644'

# Get facts about hosts
ansible all -m setup

# Execute command
ansible all -m command -a 'uptime'
```

### Ansible Modules

Most commonly used modules:

- **apt/yum**: Package management
- **copy**: Copy files
- **template**: Process Jinja2 templates
- **file**: Manage files and directories
- **systemd/service**: Manage services
- **user**: Manage users
- **git**: Git operations
- **shell/command**: Execute commands
- **uri**: HTTP requests
- **docker_container**: Docker management

## Writing Your First Playbook

### Simple Web Server Setup

Create `webserver.yml`:

```yaml
---
- name: Setup Web Server
  hosts: web_servers
  become: yes

  tasks:
    - name: Update apt cache
      apt:
        update_cache: yes
        cache_valid_time: 3600

    - name: Install nginx
      apt:
        name: nginx
        state: present

    - name: Copy nginx config
      copy:
        content: |
          server {
              listen 80;
              server_name example.com;
              root /var/www/html;
              index index.html;
          }
        dest: /etc/nginx/sites-available/default
      notify: reload nginx

    - name: Ensure nginx is running
      systemd:
        name: nginx
        state: started
        enabled: yes

  handlers:
    - name: reload nginx
      systemd:
        name: nginx
        state: reloaded
```

Run the playbook:

```bash
ansible-playbook webserver.yml

# Dry run (check mode)
ansible-playbook webserver.yml --check

# Run with verbose output
ansible-playbook webserver.yml -vvv

# Limit to specific hosts
ansible-playbook webserver.yml --limit server1
```

## Inventory Management

### Static Inventory

Create `inventory/hosts`:

```ini
# Simple inventory
[web_servers]
web1.example.com
web2.example.com

[db_servers]
db1.example.com
db2.example.com

# With variables
[web_servers]
web1.example.com ansible_host=10.0.1.10 ansible_port=2222
web2.example.com ansible_host=10.0.1.11

# Groups of groups
[production:children]
web_servers
db_servers

[production:vars]
env=production
backup_enabled=true
```

### YAML Inventory

Create `inventory/hosts.yml`:

```yaml
all:
  children:
    web_servers:
      hosts:
        web1.example.com:
          ansible_host: 10.0.1.10
        web2.example.com:
          ansible_host: 10.0.1.11
      vars:
        http_port: 80
        max_clients: 200

    db_servers:
      hosts:
        db1.example.com:
          ansible_host: 10.0.2.10
          postgres_role: primary
        db2.example.com:
          ansible_host: 10.0.2.11
          postgres_role: replica
```

### Dynamic Inventory

For cloud environments, use dynamic inventory:

```bash
# AWS
pip install boto3
ansible-inventory -i aws_ec2.yml --graph

# Azure
pip install azure-cli
ansible-inventory -i azure_rm.yml --graph

# GCP
pip install google-auth
ansible-inventory -i gcp_compute.yml --graph
```

Example AWS dynamic inventory (`aws_ec2.yml`):

```yaml
plugin: aws_ec2
regions:
  - us-east-1
  - us-west-2
filters:
  tag:Environment: production
keyed_groups:
  - key: tags.Role
    prefix: role
  - key: tags.Environment
    prefix: env
hostnames:
  - private-ip-address
compose:
  ansible_host: private_ip_address
```

## Variables and Templates

### Variable Precedence

From lowest to highest priority:

1. Role defaults
2. Inventory file/group vars
3. Inventory group_vars/all
4. Playbook group_vars/all
5. Inventory group_vars/*
6. Playbook group_vars/*
7. Inventory file/host vars
8. Inventory host_vars/*
9. Playbook host_vars/*
10. Host facts
11. Play vars
12. Play vars_prompt
13. Play vars_files
14. Role and include vars
15. Block vars
16. Task vars
17. Extra vars (command line)

### Using Variables

```yaml
---
- name: Variable Examples
  hosts: web_servers
  vars:
    app_name: myapp
    app_version: 1.0.0
    app_port: 8080

  tasks:
    - name: Debug variables
      debug:
        msg: "Deploying {{ app_name }} version {{ app_version }}"

    - name: Use variables in module
      copy:
        content: "App: {{ app_name }}\nVersion: {{ app_version }}"
        dest: "/opt/{{ app_name }}/version.txt"

    - name: Load variables from file
      include_vars:
        file: vars/{{ env }}.yml

    - name: Register output
      command: date
      register: current_date

    - name: Use registered variable
      debug:
        msg: "Current date: {{ current_date.stdout }}"
```

### Jinja2 Templates

Create `templates/nginx.conf.j2`:

```jinja2
# Managed by Ansible - Do not edit manually

user {{ nginx_user }};
worker_processes {{ nginx_workers | default(ansible_processor_vcpus) }};

events {
    worker_connections {{ nginx_worker_connections | default(1024) }};
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Logging
    access_log {{ nginx_access_log }};
    error_log {{ nginx_error_log }};

    # Performance
    sendfile on;
    tcp_nopush on;
    keepalive_timeout {{ nginx_keepalive_timeout | default(65) }};

    # Virtual Hosts
    {% for vhost in nginx_vhosts %}
    server {
        listen {{ vhost.port | default(80) }};
        server_name {{ vhost.server_name }};
        root {{ vhost.root }};

        {% if vhost.ssl | default(false) %}
        listen 443 ssl;
        ssl_certificate {{ vhost.ssl_cert }};
        ssl_certificate_key {{ vhost.ssl_key }};
        {% endif %}

        location / {
            try_files $uri $uri/ =404;
        }
    }
    {% endfor %}
}
```

Use in playbook:

```yaml
- name: Configure nginx
  template:
    src: templates/nginx.conf.j2
    dest: /etc/nginx/nginx.conf
    owner: root
    group: root
    mode: '0644'
    validate: 'nginx -t -c %s'
  notify: reload nginx
```

## Roles and Organization

### Directory Structure

```
ansible/
├── ansible.cfg
├── inventory/
│   ├── production/
│   │   ├── hosts
│   │   └── group_vars/
│   └── staging/
│       ├── hosts
│       └── group_vars/
├── playbooks/
│   ├── site.yml
│   ├── webservers.yml
│   └── databases.yml
├── roles/
│   ├── common/
│   │   ├── tasks/
│   │   │   └── main.yml
│   │   ├── handlers/
│   │   │   └── main.yml
│   │   ├── templates/
│   │   ├── files/
│   │   ├── vars/
│   │   │   └── main.yml
│   │   └── defaults/
│   │       └── main.yml
│   ├── webserver/
│   └── database/
└── group_vars/
    ├── all.yml
    ├── web_servers.yml
    └── db_servers.yml
```

### Creating a Role

```bash
# Create role structure
ansible-galaxy init roles/myapp

# Role structure
roles/myapp/
├── defaults/       # Default variables
├── files/          # Static files
├── handlers/       # Event handlers
├── meta/           # Role metadata
├── tasks/          # Main tasks
├── templates/      # Jinja2 templates
├── tests/          # Test playbooks
└── vars/           # Variables
```

### Example Role

`roles/myapp/tasks/main.yml`:

```yaml
---
- name: Include OS-specific variables
  include_vars: "{{ ansible_os_family }}.yml"

- name: Install application dependencies
  package:
    name: "{{ item }}"
    state: present
  loop: "{{ app_dependencies }}"

- name: Create application user
  user:
    name: "{{ app_user }}"
    home: "{{ app_home }}"
    shell: /bin/bash

- name: Deploy application
  include_tasks: deploy.yml

- name: Configure application
  template:
    src: config.yml.j2
    dest: "{{ app_home }}/config.yml"
  notify: restart application
```

Use role in playbook:

```yaml
---
- name: Deploy Application
  hosts: app_servers
  roles:
    - common
    - myapp
  vars:
    app_version: "2.0.0"
```

## Best Practices

### 1. Use Check Mode and Diff

```bash
# Test without making changes
ansible-playbook site.yml --check

# Show file differences
ansible-playbook site.yml --check --diff
```

### 2. Idempotency

Write idempotent tasks:

```yaml
# Good - idempotent
- name: Ensure nginx is installed
  apt:
    name: nginx
    state: present

# Bad - not idempotent
- name: Install nginx
  shell: apt-get install nginx
```

### 3. Use Handlers

```yaml
tasks:
  - name: Copy nginx config
    copy:
      src: nginx.conf
      dest: /etc/nginx/nginx.conf
    notify: reload nginx

handlers:
  - name: reload nginx
    systemd:
      name: nginx
      state: reloaded
```

### 4. Vault for Secrets

```bash
# Create encrypted file
ansible-vault create secrets.yml

# Edit encrypted file
ansible-vault edit secrets.yml

# Encrypt existing file
ansible-vault encrypt vars/production.yml

# Run playbook with vault
ansible-playbook site.yml --ask-vault-pass

# Use vault password file
ansible-playbook site.yml --vault-password-file ~/.vault_pass
```

### 5. Tags for Selective Execution

```yaml
tasks:
  - name: Install packages
    apt:
      name: nginx
    tags:
      - packages
      - install

  - name: Configure application
    template:
      src: config.j2
      dest: /etc/app/config
    tags:
      - config
```

Run specific tags:

```bash
ansible-playbook site.yml --tags "config"
ansible-playbook site.yml --skip-tags "packages"
```

## Troubleshooting

### Debug Tasks

```yaml
- name: Show all variables
  debug:
    var: hostvars[inventory_hostname]

- name: Show specific variable
  debug:
    msg: "App version: {{ app_version }}"

- name: Show ansible facts
  debug:
    var: ansible_facts
```

### Verbose Output

```bash
# Levels of verbosity
ansible-playbook site.yml -v    # Normal
ansible-playbook site.yml -vv   # More details
ansible-playbook site.yml -vvv  # Lots of details
ansible-playbook site.yml -vvvv # Everything including SSH
```

### Common Issues

**Issue: Host unreachable**
```bash
# Test connectivity
ansible all -m ping

# Check SSH config
ansible all -m shell -a 'echo $SSH_CONNECTION'
```

**Issue: Permission denied**
```bash
# Use become
ansible-playbook site.yml --become --ask-become-pass

# Or in playbook
become: yes
```

**Issue: Fact gathering slow**
```bash
# Disable fact gathering if not needed
gather_facts: no

# Or use smart gathering in ansible.cfg
gathering = smart
```

## Next Steps

1. **Learn Ansible Galaxy**: Reuse community roles
2. **Implement CI/CD**: Test playbooks automatically
3. **Use Ansible Tower/AWX**: Web UI and API for Ansible
4. **Explore Collections**: Ansible Content Collections
5. **Write Custom Modules**: Extend Ansible functionality

## Resources

- [Official Documentation](https://docs.ansible.com/)
- [Ansible Galaxy](https://galaxy.ansible.com/)
- [Best Practices](https://docs.ansible.com/ansible/latest/user_guide/playbooks_best_practices.html)
- [Module Index](https://docs.ansible.com/ansible/latest/collections/index_module.html)

---

**Last Updated**: 2025-11-19
**Version**: 1.0
