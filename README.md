# ansible.CaaS
Ansible modules for managing Dimension Data Cloud

A simple/trivial wrappper of CaaS API v2.1 documented [here](https://community.opsourcecloud.net/View.jsp?procId=10011686f65f51b7f474acb2013072d2)

## modules
  * [caas_networkdomain.py](/library/caas_networkdomain.py) : Create/Delete Network Domain on MCP [(documentation)](/docs/caas_networkdomain_module.md)
  * [caas_vlan.py](/library/caas_vlan.py) : Create/Delete VLAN on MCP [(documentation)](/docs/caas_vlan_module.md)
  * [caas_server.py](/library/caas_server.py) : Create/Delete Servers on MCP [(documentation)](/docs/caas_server_module.md)
  * [caas_firewallrule.py](/library/caas_firewallrule.py) : Create/Delete FireWall rules on MCP [(documentation)](/docs/caas_firewallrule_module.md)
  * [caas_loadbalancer.py](/library/caas_loadbalancer.py) : Create/Delete Load Balancing config on MCP [(documentation)](/docs/caas_loadbalancer_module.md)
  * [caas_publicip.py](/library/caas_publicip.py) : Create/Delete Public IP blocks on MCP [(documentation)](/docs/caas_publicip_module.md)

## example
  * [demo.yml](/demo.yml) : Sample Demo Ansible playbook file
  * [cleandemo.yml](/cleandemo.yml) : Cleanning the Demo environment
  * [caas_credentials.yml](/caas_credentials.yml) : Sample file to fill with your own credentials

## installation
  1. Install Ansible
    1. yum install asciidoc
    2. yum install python-sphinx
    2. git clone git://github.com/ansible/ansible.git --recursive
    2. source ./hacking/env-setup
  2. Download this repo : 
  2. Create a credential files
  3. ansible-playbook demo.yml
