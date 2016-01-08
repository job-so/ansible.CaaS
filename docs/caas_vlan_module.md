---
title: |
    caas\_vlan - Create, Configure, Remove Network Domain on Dimension Data
    Managed Cloud Platform
...

Synopsis
========

Create, Remove Network vlans on Dimension Data Managed Cloud Platform

Options
=======

<table border=1 cellpadding=4>
<tr>
<th class="head">parameter</th>
<th class="head">required</th>
<th class="head">default</th>
<th class="head">choices</th>
<th class="head">comments</th>
</tr>
        <tr>
<td>caas_apiurl<br/><div style="font-size: small;"></div></td>
<td>yes</td>
<td></td>
    <td><ul></ul></td>
    <td><div>See caas_server for more information</div></td></tr>
        <tr>
<td>caas_datacenter<br/><div style="font-size: small;"></div></td>
<td>yes</td>
<td></td>
    <td><ul></ul></td>
    <td><div>See caas_server for more information</div></td></tr>
        <tr>
<td>caas_password<br/><div style="font-size: small;"></div></td>
<td>yes</td>
<td></td>
    <td><ul></ul></td>
    <td><div>The associated password</div></td></tr>
        <tr>
<td>caas_username<br/><div style="font-size: small;"></div></td>
<td>yes</td>
<td></td>
    <td><ul></ul></td>
    <td><div>Your username credential</div></td></tr>
        <tr>
<td>description<br/><div style="font-size: small;"></div></td>
<td>no</td>
<td>Created and managed by ansible.CaaS - https://github.com/job-so/ansible.CaaS</td>
    <td><ul></ul></td>
    <td><div>Maximum length: 255 characters.</div></td></tr>
        <tr>
<td>name<br/><div style="font-size: small;"></div></td>
<td>yes</td>
<td></td>
    <td><ul></ul></td>
    <td><div>Name that has to be given to the instance</div><div>The name must be unique inside the DataCenter</div><div>Minimum length 1 character Maximum length 75 characters.</div></td></tr>
        <tr>
<td>networkDomainId<br/><div style="font-size: small;"></div></td>
<td>no</td>
<td></td>
    <td><ul></ul></td>
    <td><div>The id of a Network Domain belonging to {org-id} within the same MCP 2.0 data center.</div></td></tr>
        <tr>
<td>networkDomainName<br/><div style="font-size: small;"></div></td>
<td>no</td>
<td></td>
    <td><ul></ul></td>
    <td><div>The name of a Network Domain belonging to {org-id} within the same MCP 2.0 data center.</div></td></tr>
        <tr>
<td>privateIpv4BaseAddress<br/><div style="font-size: small;"></div></td>
<td>no</td>
<td></td>
    <td><ul></ul></td>
    <td><div>An Integer between 16 and 24, which represents the size of the VLAN to be deployed and must be consistent with the privateIpv4BaseAddress provided.</div><div>If this property is not provided, the VLAN will default to being /24</div></td></tr>
        <tr>
<td>state<br/><div style="font-size: small;"></div></td>
<td>no</td>
<td>present</td>
    <td><ul><li>present</li><li>absent</li></ul></td>
    <td><div>Should the resource be present or absent.</div><div>Take care : Absent will powerOff and delete all servers.</div></td></tr>
    </table>
</br>
Examples
========

>     # Creates a new vlan named "ansible.Caas_SandBox", 
>     -caas_networkdomain:
>         caas_apiurl: "{{ caas_apiurl }}"
>         caas_username: "{{ caas_username }}"
>         caas_password: "{{ caas_password }}"
>         datacenterId: "{{ caas_datacenter }}"
>         name: "vlan_webservers"
>         register: caas_networkdomain

This is an Extras Module
========================

For more information on what this means please read modules\_extra

For help in developing on modules, should you be so inclined, please
read community, developing\_test\_pr and developing\_modules.
