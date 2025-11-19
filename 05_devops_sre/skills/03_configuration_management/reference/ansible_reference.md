# Ansible Reference

## Overview
Comprehensive reference for Ansible automation, covering playbooks, roles, modules, and enterprise best practices.

## Table of Contents
- [Core Concepts](#core-concepts)
- [Playbook Structure](#playbook-structure)
- [Roles](#roles)
- [Variables and Facts](#variables-and-facts)
- [Templates](#templates)
- [Handlers](#handlers)
- [Vault Integration](#vault-integration)
- [Best Practices](#best-practices)
- [Advanced Patterns](#advanced-patterns)

---

## Core Concepts

### Inventory
```ini
# inventory/production.ini
[webservers]
web01.example.com ansible_host=10.0.1.10
web02.example.com ansible_host=10.0.1.11

[databases]
db01.example.com ansible_host=10.0.2.10
db02.example.com ansible_host=10.0.2.11

[production:children]
webservers
databases

[production:vars]
ansible_user=deploy
ansible_python_interpreter=/usr/bin/python3
```

### Dynamic Inventory
```python
#!/usr/bin/env python3
# inventory/aws_ec2_dynamic.py
import json
import boto3

def get_inventory():
    ec2 = boto3.client('ec2')
    inventory = {
        '_meta': {'hostvars': {}},
        'all': {'hosts': []},
        'webservers': {'hosts': []},
        'databases': {'hosts': []}
    }

    response = ec2.describe_instances(
        Filters=[{'Name': 'tag:Environment', 'Values': ['production']}]
    )

    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            if instance['State']['Name'] != 'running':
                continue

            hostname = instance['PrivateIpAddress']
            inventory['all']['hosts'].append(hostname)

            # Group by tags
            for tag in instance.get('Tags', []):
                if tag['Key'] == 'Role':
                    group = tag['Value']
                    if group not in inventory:
                        inventory[group] = {'hosts': []}
                    inventory[group]['hosts'].append(hostname)

            # Host variables
            inventory['_meta']['hostvars'][hostname] = {
                'ansible_host': instance['PrivateIpAddress'],
                'instance_id': instance['InstanceId'],
                'instance_type': instance['InstanceType']
            }

    return inventory

if __name__ == '__main__':
    print(json.dumps(get_inventory(), indent=2))
```

---

## Playbook Structure

### Basic Playbook
```yaml
# playbooks/webserver_setup.yml
---
- name: Configure web servers
  hosts: webservers
  become: yes
  vars:
    http_port: 80
    max_clients: 200

  pre_tasks:
    - name: Update package cache
      apt:
        update_cache: yes
        cache_valid_time: 3600
      when: ansible_os_family == "Debian"

  roles:
    - common
    - nginx
    - ssl

  tasks:
    - name: Ensure nginx is running
      service:
        name: nginx
        state: started
        enabled: yes

    - name: Copy custom index page
      template:
        src: templates/index.html.j2
        dest: /var/www/html/index.html
        owner: www-data
        group: www-data
        mode: '0644'
      notify: reload nginx

  post_tasks:
    - name: Verify nginx is responding
      uri:
        url: http://localhost
        status_code: 200
      retries: 3
      delay: 5

  handlers:
    - name: reload nginx
      service:
        name: nginx
        state: reloaded
```

### Multi-Play Playbook
```yaml
# playbooks/full_stack_deploy.yml
---
- name: Prepare database servers
  hosts: databases
  become: yes
  serial: 1  # One at a time

  tasks:
    - name: Take database backup
      mysql_db:
        name: all
        state: dump
        target: /backup/pre-deploy-{{ ansible_date_time.iso8601 }}.sql

    - name: Run database migrations
      command: /opt/app/bin/migrate
      register: migration_result

    - name: Verify migration
      assert:
        that:
          - migration_result.rc == 0
        fail_msg: "Migration failed on {{ inventory_hostname }}"

- name: Deploy application servers
  hosts: webservers
  become: yes
  serial: "50%"  # Half at a time for rolling deployment

  tasks:
    - name: Pull latest code
      git:
        repo: https://github.com/company/app.git
        dest: /opt/app
        version: "{{ app_version }}"
      notify: restart app

    - name: Install dependencies
      pip:
        requirements: /opt/app/requirements.txt
        virtualenv: /opt/app/venv

    - name: Health check
      uri:
        url: http://localhost:8000/health
        status_code: 200
      retries: 5
      delay: 10

  handlers:
    - name: restart app
      systemd:
        name: myapp
        state: restarted
        daemon_reload: yes
```

---

## Roles

### Role Directory Structure
```
roles/nginx/
├── README.md
├── defaults/
│   └── main.yml          # Default variables
├── files/
│   └── nginx.conf        # Static files
├── handlers/
│   └── main.yml          # Handlers
├── meta/
│   └── main.yml          # Role metadata and dependencies
├── tasks/
│   ├── main.yml          # Main task file
│   ├── install.yml       # Task includes
│   └── configure.yml
├── templates/
│   └── vhost.conf.j2     # Jinja2 templates
├── tests/
│   ├── inventory
│   └── test.yml
└── vars/
    └── main.yml          # Role variables
```

### Complete Role Example
```yaml
# roles/nginx/defaults/main.yml
---
nginx_port: 80
nginx_worker_processes: auto
nginx_worker_connections: 1024
nginx_client_max_body_size: 10M
nginx_keepalive_timeout: 65
nginx_sites: []
```

```yaml
# roles/nginx/vars/main.yml
---
nginx_user: www-data
nginx_log_dir: /var/log/nginx
nginx_conf_dir: /etc/nginx
```

```yaml
# roles/nginx/meta/main.yml
---
galaxy_info:
  role_name: nginx
  author: DevOps Team
  description: Nginx web server configuration
  company: Example Corp
  license: MIT
  min_ansible_version: 2.9
  platforms:
    - name: Ubuntu
      versions:
        - focal
        - jammy
  galaxy_tags:
    - web
    - nginx

dependencies:
  - role: common
  - role: ssl
    when: nginx_ssl_enabled
```

```yaml
# roles/nginx/tasks/main.yml
---
- name: Include OS-specific variables
  include_vars: "{{ ansible_os_family }}.yml"

- name: Install nginx
  include_tasks: install.yml

- name: Configure nginx
  include_tasks: configure.yml

- name: Setup virtual hosts
  include_tasks: vhosts.yml
  when: nginx_sites | length > 0

- name: Ensure nginx is running
  service:
    name: nginx
    state: started
    enabled: yes
```

```yaml
# roles/nginx/tasks/install.yml
---
- name: Add nginx repository (Ubuntu)
  apt_repository:
    repo: ppa:nginx/stable
    state: present
  when: ansible_distribution == "Ubuntu"

- name: Install nginx package
  package:
    name: nginx
    state: present

- name: Create log directory
  file:
    path: "{{ nginx_log_dir }}"
    state: directory
    owner: "{{ nginx_user }}"
    group: "{{ nginx_user }}"
    mode: '0755'
```

```yaml
# roles/nginx/tasks/configure.yml
---
- name: Deploy nginx main configuration
  template:
    src: nginx.conf.j2
    dest: "{{ nginx_conf_dir }}/nginx.conf"
    owner: root
    group: root
    mode: '0644'
    validate: 'nginx -t -c %s'
  notify: reload nginx

- name: Remove default site
  file:
    path: "{{ nginx_conf_dir }}/sites-enabled/default"
    state: absent
  notify: reload nginx
```

```yaml
# roles/nginx/handlers/main.yml
---
- name: reload nginx
  service:
    name: nginx
    state: reloaded

- name: restart nginx
  service:
    name: nginx
    state: restarted
```

```jinja2
{# roles/nginx/templates/nginx.conf.j2 #}
user {{ nginx_user }};
worker_processes {{ nginx_worker_processes }};
pid /run/nginx.pid;

events {
    worker_connections {{ nginx_worker_connections }};
    use epoll;
    multi_accept on;
}

http {
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout {{ nginx_keepalive_timeout }};
    types_hash_max_size 2048;
    server_tokens off;

    client_max_body_size {{ nginx_client_max_body_size }};

    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Logging
    access_log {{ nginx_log_dir }}/access.log;
    error_log {{ nginx_log_dir }}/error.log;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript
               application/json application/javascript application/xml+rss;

    # Virtual host configs
    include {{ nginx_conf_dir }}/sites-enabled/*;
}
```

---

## Variables and Facts

### Variable Precedence (lowest to highest)
1. command line values (e.g., -u my_user)
2. role defaults (defaults/main.yml)
3. inventory file or script group vars
4. inventory group_vars/all
5. playbook group_vars/all
6. inventory group_vars/*
7. playbook group_vars/*
8. inventory file or script host vars
9. inventory host_vars/*
10. playbook host_vars/*
11. host facts / cached set_facts
12. play vars
13. play vars_prompt
14. play vars_files
15. role vars (vars/main.yml)
16. block vars
17. task vars
18. include_vars
19. set_facts / registered vars
20. role (and include_role) params
21. include params
22. extra vars (-e in CLI)

### Variable Examples
```yaml
# group_vars/all/common.yml
---
ntp_servers:
  - 0.pool.ntp.org
  - 1.pool.ntp.org

ssh_port: 22
enable_firewall: yes

# Environment-specific settings
environments:
  dev:
    debug: yes
    log_level: debug
  staging:
    debug: yes
    log_level: info
  production:
    debug: no
    log_level: warning
```

```yaml
# group_vars/webservers/nginx.yml
---
nginx_vhosts:
  - name: example.com
    root: /var/www/example.com
    port: 80
    ssl: yes
    cert_file: /etc/ssl/certs/example.com.crt
    key_file: /etc/ssl/private/example.com.key
```

### Using Facts
```yaml
---
- name: Use ansible facts
  hosts: all
  tasks:
    - name: Display facts
      debug:
        msg: |
          OS: {{ ansible_distribution }} {{ ansible_distribution_version }}
          Kernel: {{ ansible_kernel }}
          CPUs: {{ ansible_processor_vcpus }}
          Memory: {{ ansible_memtotal_mb }}MB
          IP: {{ ansible_default_ipv4.address }}

    - name: Install package based on OS
      package:
        name: "{{ 'httpd' if ansible_os_family == 'RedHat' else 'apache2' }}"
        state: present

    - name: Custom facts
      set_fact:
        app_env: "{{ 'production' if 'prod' in inventory_hostname else 'staging' }}"
        cacheable: yes
```

### Custom Facts
```bash
# /etc/ansible/facts.d/custom.fact
#!/bin/bash
echo "{\"deployment\": {\"version\": \"1.2.3\", \"date\": \"$(date -I)\"}}"
```

```yaml
- name: Use custom facts
  debug:
    msg: "Deployment version: {{ ansible_local.custom.deployment.version }}"
```

---

## Templates

### Jinja2 Templates
```jinja2
{# templates/app_config.yml.j2 #}
# Application Configuration
# Generated by Ansible on {{ ansible_date_time.iso8601 }}
# Managed host: {{ inventory_hostname }}

app:
  name: {{ app_name }}
  version: {{ app_version }}
  environment: {{ app_environment }}
  debug: {{ debug_mode | default(false) }}

database:
  host: {{ db_host }}
  port: {{ db_port }}
  name: {{ db_name }}
  user: {{ db_user }}
  password: {{ db_password }}
  pool_size: {{ db_pool_size | default(10) }}

{% if redis_enabled %}
cache:
  type: redis
  host: {{ redis_host }}
  port: {{ redis_port | default(6379) }}
  db: {{ redis_db | default(0) }}
{% endif %}

servers:
{% for server in web_servers %}
  - name: {{ server.name }}
    url: {{ server.url }}
    weight: {{ server.weight | default(1) }}
{% endfor %}

{% if app_environment == 'production' %}
logging:
  level: INFO
  handlers:
    - type: file
      path: /var/log/{{ app_name }}/app.log
      max_size: 100MB
      retention: 30
{% else %}
logging:
  level: DEBUG
  handlers:
    - type: console
{% endif %}
```

### Advanced Template Filters
```yaml
---
- name: Template filter examples
  hosts: localhost
  vars:
    services:
      - web
      - api
      - worker
    config:
      timeout: 30
      retries: 3

  tasks:
    - name: Use filters
      debug:
        msg: |
          Upper: {{ app_name | upper }}
          Default: {{ undefined_var | default('fallback') }}
          Mandatory: {{ required_var | mandatory }}
          Join: {{ services | join(', ') }}
          To JSON: {{ config | to_json }}
          To YAML: {{ config | to_yaml }}
          Hash: {{ password | password_hash('sha512') }}
          B64 Encode: {{ 'secret' | b64encode }}
          Regex: {{ 'test123' | regex_replace('[0-9]', '') }}
          Path: {{ '/path/to/file.txt' | basename }}
```

---

## Handlers

### Handler Best Practices
```yaml
# handlers/main.yml
---
- name: restart nginx
  service:
    name: nginx
    state: restarted
  listen: "web services"

- name: reload nginx
  service:
    name: nginx
    state: reloaded
  listen: "web services"

- name: restart php-fpm
  service:
    name: php-fpm
    state: restarted
  listen: "web services"

- name: clear cache
  command: /usr/local/bin/clear-cache
  listen: "web services"

# Tasks that notify
- name: Update nginx config
  template:
    src: nginx.conf.j2
    dest: /etc/nginx/nginx.conf
  notify: reload nginx

- name: Update PHP config
  template:
    src: php.ini.j2
    dest: /etc/php/8.1/fpm/php.ini
  notify:
    - restart php-fpm
    - "web services"  # Triggers all handlers listening to this
```

---

## Vault Integration

### Encrypting Variables
```bash
# Encrypt a file
ansible-vault encrypt group_vars/production/secrets.yml

# Decrypt a file
ansible-vault decrypt group_vars/production/secrets.yml

# Edit encrypted file
ansible-vault edit group_vars/production/secrets.yml

# Rekey (change password)
ansible-vault rekey group_vars/production/secrets.yml

# Encrypt string
ansible-vault encrypt_string 'secret_password' --name 'db_password'
```

### Vault Password File
```bash
# .vault_pass
#!/bin/bash
# Retrieve password from secure storage
aws secretsmanager get-secret-value \
  --secret-id ansible-vault-password \
  --query SecretString \
  --output text
```

```bash
chmod +x .vault_pass
ansible-playbook playbook.yml --vault-password-file .vault_pass
```

### Mixed Encrypted Variables
```yaml
# group_vars/production/secrets.yml
---
db_password: !vault |
          $ANSIBLE_VAULT;1.1;AES256
          66386439653966636161336438623537376436...

api_key: !vault |
          $ANSIBLE_VAULT;1.1;AES256
          39653966636161336438623537376436653934...

# Plain text variables
db_host: db.example.com
db_port: 5432
```

---

## Best Practices

### 1. Directory Organization
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
│   ├── nginx/
│   └── postgresql/
├── group_vars/
│   └── all/
├── host_vars/
└── library/  # Custom modules
```

### 2. Idempotency
```yaml
# BAD - Not idempotent
- name: Add line to file
  shell: echo "setting=value" >> /etc/config

# GOOD - Idempotent
- name: Ensure setting in config
  lineinfile:
    path: /etc/config
    line: "setting=value"
    regexp: '^setting='

# BAD - May cause issues on re-run
- name: Download file
  command: wget http://example.com/file.tar.gz

# GOOD - Idempotent download
- name: Download file
  get_url:
    url: http://example.com/file.tar.gz
    dest: /tmp/file.tar.gz
    checksum: sha256:abc123...
```

### 3. Error Handling
```yaml
---
- name: Error handling examples
  hosts: webservers
  tasks:
    - name: Attempt risky operation
      command: /usr/bin/risky-command
      register: result
      failed_when: false
      changed_when: result.rc == 0

    - name: Handle failure
      debug:
        msg: "Command failed, but continuing"
      when: result.rc != 0

    - name: Block with rescue
      block:
        - name: Try to start service
          service:
            name: myapp
            state: started

      rescue:
        - name: Service failed to start
          debug:
            msg: "Service start failed, attempting recovery"

        - name: Check logs
          command: tail -n 50 /var/log/myapp/error.log
          register: logs

        - name: Display logs
          debug:
            var: logs.stdout_lines

      always:
        - name: Send notification
          uri:
            url: https://hooks.slack.com/services/XXX
            method: POST
            body_format: json
            body:
              text: "Deployment {{ 'succeeded' if result is success else 'failed' }}"
```

### 4. Tags
```yaml
---
- name: Complete server setup
  hosts: all
  tasks:
    - name: Install packages
      package:
        name: "{{ item }}"
        state: present
      loop:
        - git
        - vim
        - htop
      tags:
        - packages
        - setup

    - name: Configure firewall
      ufw:
        rule: allow
        port: "{{ item }}"
      loop:
        - 22
        - 80
        - 443
      tags:
        - security
        - firewall

    - name: Deploy application
      git:
        repo: https://github.com/company/app.git
        dest: /opt/app
      tags:
        - deploy
        - app
```

```bash
# Run specific tags
ansible-playbook site.yml --tags "deploy"
ansible-playbook site.yml --tags "setup,security"
ansible-playbook site.yml --skip-tags "deploy"
```

### 5. Testing Playbooks
```yaml
# Use check mode (dry run)
ansible-playbook playbook.yml --check

# Show differences
ansible-playbook playbook.yml --check --diff

# Limit to specific hosts
ansible-playbook playbook.yml --limit webservers

# Start at specific task
ansible-playbook playbook.yml --start-at-task="Deploy application"
```

---

## Advanced Patterns

### 1. Dynamic Includes
```yaml
---
- name: Dynamic task inclusion
  hosts: all
  tasks:
    - name: Include OS-specific tasks
      include_tasks: "tasks/{{ ansible_os_family | lower }}.yml"

    - name: Include role dynamically
      include_role:
        name: "{{ item }}"
      loop:
        - common
        - "{{ app_role }}"
      when: app_role is defined
```

### 2. Delegation
```yaml
---
- name: Load balancer management
  hosts: webservers
  serial: 1
  tasks:
    - name: Disable server in load balancer
      haproxy:
        state: disabled
        host: "{{ inventory_hostname }}"
        socket: /var/run/haproxy.sock
      delegate_to: "{{ item }}"
      loop: "{{ groups['loadbalancers'] }}"

    - name: Deploy application
      include_role:
        name: app_deploy

    - name: Wait for health check
      uri:
        url: http://localhost:8000/health
        status_code: 200
      retries: 5
      delay: 10

    - name: Enable server in load balancer
      haproxy:
        state: enabled
        host: "{{ inventory_hostname }}"
        socket: /var/run/haproxy.sock
      delegate_to: "{{ item }}"
      loop: "{{ groups['loadbalancers'] }}"
```

### 3. Async Tasks
```yaml
---
- name: Long running tasks
  hosts: databases
  tasks:
    - name: Run long backup
      command: /usr/local/bin/full-backup
      async: 3600  # Maximum runtime
      poll: 0      # Fire and forget
      register: backup_job

    - name: Do other work
      debug:
        msg: "Backup running in background"

    - name: Check backup status
      async_status:
        jid: "{{ backup_job.ansible_job_id }}"
      register: job_result
      until: job_result.finished
      retries: 60
      delay: 60
```

### 4. Custom Modules
```python
#!/usr/bin/python
# library/custom_health_check.py

from ansible.module_utils.basic import AnsibleModule
import requests

def check_health(url, timeout):
    try:
        response = requests.get(url, timeout=timeout)
        return {
            'status_code': response.status_code,
            'healthy': response.status_code == 200,
            'response_time': response.elapsed.total_seconds()
        }
    except Exception as e:
        return {
            'healthy': False,
            'error': str(e)
        }

def main():
    module = AnsibleModule(
        argument_spec=dict(
            url=dict(type='str', required=True),
            timeout=dict(type='int', default=30)
        ),
        supports_check_mode=True
    )

    result = check_health(
        module.params['url'],
        module.params['timeout']
    )

    if result.get('healthy'):
        module.exit_json(changed=False, **result)
    else:
        module.fail_json(msg="Health check failed", **result)

if __name__ == '__main__':
    main()
```

```yaml
# Use custom module
- name: Check application health
  custom_health_check:
    url: http://{{ inventory_hostname }}:8000/health
    timeout: 10
  register: health
```

### 5. Ansible Configuration
```ini
# ansible.cfg
[defaults]
inventory = ./inventory/production/hosts
roles_path = ./roles
host_key_checking = False
retry_files_enabled = False
gathering = smart
fact_caching = jsonfile
fact_caching_connection = /tmp/ansible_facts
fact_caching_timeout = 86400
callback_whitelist = profile_tasks, timer
stdout_callback = yaml

[privilege_escalation]
become = True
become_method = sudo
become_user = root
become_ask_pass = False

[ssh_connection]
ssh_args = -o ControlMaster=auto -o ControlPersist=60s
pipelining = True
control_path = /tmp/ansible-ssh-%%h-%%p-%%r
```

---

## Performance Optimization

### 1. Mitogen Strategy
```ini
# ansible.cfg
[defaults]
strategy_plugins = /usr/local/lib/python3/site-packages/ansible_mitogen/plugins/strategy
strategy = mitogen_linear

[ssh_connection]
pipelining = True
```

### 2. Forks and Serial
```yaml
# ansible.cfg
[defaults]
forks = 50  # Parallel execution

# In playbook
- name: Rolling deployment
  hosts: webservers
  serial: "30%"  # Process 30% at a time
```

### 3. Fact Caching
```ini
[defaults]
gathering = smart
fact_caching = redis
fact_caching_connection = localhost:6379:0
fact_caching_timeout = 86400
```

---

## Troubleshooting

### Debug Techniques
```yaml
---
- name: Debugging playbook
  hosts: all
  tasks:
    - name: Show all variables
      debug:
        var: hostvars[inventory_hostname]

    - name: Conditional debug
      debug:
        msg: "Variable is: {{ my_var }}"
      when: ansible_verbosity >= 2

    - name: Debug with verbosity
      debug:
        msg: "Detailed info"
        verbosity: 1
```

```bash
# Increase verbosity
ansible-playbook playbook.yml -v    # verbose
ansible-playbook playbook.yml -vv   # more verbose
ansible-playbook playbook.yml -vvv  # very verbose (connection debugging)
ansible-playbook playbook.yml -vvvv # enable connection debugging
```

### Syntax Check
```bash
# Check playbook syntax
ansible-playbook playbook.yml --syntax-check

# List tasks
ansible-playbook playbook.yml --list-tasks

# List hosts
ansible-playbook playbook.yml --list-hosts

# Lint playbooks
ansible-lint playbook.yml
```

---

## CI/CD Integration

### GitLab CI Example
```yaml
# .gitlab-ci.yml
stages:
  - validate
  - deploy

validate:
  stage: validate
  script:
    - ansible-playbook --syntax-check playbooks/site.yml
    - ansible-lint playbooks/
  only:
    - merge_requests

deploy_staging:
  stage: deploy
  script:
    - ansible-playbook -i inventory/staging playbooks/site.yml
  only:
    - develop

deploy_production:
  stage: deploy
  script:
    - ansible-playbook -i inventory/production playbooks/site.yml
  only:
    - main
  when: manual
```

---

## Security Best Practices

1. **Use Ansible Vault** for secrets
2. **Avoid storing passwords** in plain text
3. **Use SSH keys** for authentication
4. **Limit privilege escalation** to necessary tasks
5. **Validate external inputs** in templates
6. **Keep Ansible updated** for security patches
7. **Use HTTPS** for role/collection downloads
8. **Audit playbook runs** and maintain logs
9. **Use dynamic inventory** to avoid hardcoded IPs
10. **Implement change control** for production deployments
