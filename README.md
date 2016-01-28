# ansible.CaaS
Ansible modules for managing Dimension Data Cloud

A simple/trivial wrappper of CaaS API v2.1 documented [here](https://community.opsourcecloud.net/View.jsp?procId=10011686f65f51b7f474acb2013072d2)

RFTM :-) : For each module, you should find a clear documentation. click on documentation links below.

## modules
  * [caas_credentials.py](/library/caas_credentials.py) : Check credentials against MCP [(documentation)](https://rawgit.com/job-so/ansible.CaaS/master/docs/caas_credentials_module.html)
  * [caas_networkdomain.py](/library/caas_networkdomain.py) : Create/Delete Network Domain on MCP [(documentation)](https://rawgit.com/job-so/ansible.CaaS/master/docs/caas_networkdomain_module.html)
  * [caas_vlan.py](/library/caas_vlan.py) : Create/Delete VLAN on MCP [(documentation)](https://rawgit.com/job-so/ansible.CaaS/master/docs/caas_vlan_module.html)
  * [caas_server.py](/library/caas_server.py) : Create/Delete Servers on MCP [(documentation)](https://rawgit.com/job-so/ansible.CaaS/master/docs/caas_server_module.html)
  * [caas_firewallrule.py](/library/caas_firewallrule.py) : Create/Delete FireWall rules on MCP [(documentation)](https://rawgit.com/job-so/ansible.CaaS/master/docs/caas_firewallrule_module.html)
  * [caas_loadbalancer.py](/library/caas_loadbalancer.py) : Create/Delete Load Balancing config on MCP [(documentation)](https://rawgit.com/job-so/ansible.CaaS/master/docs/caas_loadbalancer_module.html)
  * [caas_publicip.py](/library/caas_publicip.py) : Create/Delete Public IP blocks on MCP [(documentation)](https://rawgit.com/job-so/ansible.CaaS/master/docs/caas_publicip_module.html)

## example
  * [demo.yml](/demo.yml) : Sample Demo Ansible playbook file
  * [cleandemo.yml](/cleandemo.yml) : Cleanning the Demo environment
  * [caas_credentials.yml](/caas_credentials.yml) : Sample file to fill with your own credentials

## installation
  1. Install Ansible on a clean machine (You can use a CENTOS7/64 template on MCP)
    1. yum update
	yum install epel-release
	yum install ansible
	2. yum install git asciidoc python python-sphinx
	3. easy_install pip
	4. pip install paramiko PyYAML Jinja2 httplib2 six
    4. git clone git://github.com/ansible/ansible.git --recursive
    5. source ./ansible/hacking/env-setup
  2. Download this repo : 
    1. git clone git://github.com/job-so/ansible.CaaS
	2. ln -s /root/ansible.CaaS/library ansible/lib/ansible/modules/extras/cloud/dimension_data

## How to run a demo
  2. Create a credential files
  3. ansible-playbook demo.yml

## dev : build the documentation
  1. make --directory ~/ansible/ webdocs
  2. Rst Documentation : ~/ansible/docsite/
  3. HTML Dcumentation : cp  ~/ansible/docsite/htmlout/caas_*.html ~/ansible.CaaS/docs/
  4. MARKDOWN Documentation : for f in ~/ansible/docsite/rst/caas_*_module.rst; do g=${f/.rst/.md}; h=${g/'/ansible/docsite/rst/'/'/ansible.CaaS/docs/'}; pandoc -s -o $h $f; done



