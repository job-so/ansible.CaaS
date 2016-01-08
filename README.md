# ansible.CaaS
Ansible modules for managing Dimension Data Cloud

A simple/trivial wrappper of CaaS API v2.1 documented [here](https://community.opsourcecloud.net/View.jsp?procId=10011686f65f51b7f474acb2013072d2)

## modules
  * [library/caas_networkdomain.py](/library/caas_networkdomain.py)-[(documentation)](/docs/caas_networkdomain_module.md) : Create/Delete Network Domain on Dimension Data Managed Cloud Platforms 
  * [library/caas_vlan.py](/job-so/ansible.CaaS/blob/master/library/caas_vlan.py)-[(documentation)](/job-so/ansible.CaaS/blob/master/docs/caas_vlan_module.md) : Create/Delete VLAN on Dimension Data Managed Cloud Platforms   * [library/caas_server.py](/job-so/ansible.CaaS/blob/master/library/caas_server.py)-[(documentation)](/job-so/ansible.CaaS/blob/master/docs/caas_server_module.md) : Create/Delete Servers on Dimension Data Managed Cloud Platforms 
  *  

## example
  * demo.yml : Sample Deployment file
  * caas_credentials.yml : Sample file to fill with your own credentials

## installation
  1. Install Ansible
    1. yum install asciidoc
    2. yum install python-sphinx
    2. git clone git://github.com/ansible/ansible.git --recursive
    2. source ./hacking/env-setup
  2. Download this repo : 
  2. Create a credential files
  3. ansible-playbook demo.yml
