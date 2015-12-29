# ansible.CaaS
Ansible modules for managing Dimension Data Cloud

A simple/trivial wrappper of CaaS API v2.1 documented here : https://community.opsourcecloud.net/View.jsp?procId=10011686f65f51b7f474acb2013072d2

## modules
  * library/caas_server.py : Create/Delete Servers on Dimension Data Managed Cloud Platforms

## example
  * demo.yml : Sample Deployment file
  * caas_credentials.yml : Sample file to fill with your own credentials

## installation
  1. Install Ansible : http://docs.ansible.com/ansible/intro_installation.html
  2. Download this repo : 
  2. Create a credential files
  3. ansible-playbook demo.yml
