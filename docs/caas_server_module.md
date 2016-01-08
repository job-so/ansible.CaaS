---
title: |
    caas\_server - Create, Configure, Remove Servers on Dimension Data
    Managed Cloud Platform
...

Synopsis
========

Create, Configure, Remove Servers on Dimension Data Managed Cloud
Platform For now, this module only support MCP 2.0.

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
<td>action<br/><div style="font-size: small;"></div></td>
<td>no</td>
<td>startServer</td>
    <td><ul><li>startServer</li><li>shutdownServer</li><li>rebootServer</li><li>resetServer</li><li>powerOffServer</li><li>updateVmwareTools</li><li>upgradeVirtualHardware</li></ul></td>
    <td><div>Action to perform against all servers.</div><div>startServer : starts non-running Servers</div><div>shutdownServer : performs guest OS initiated shutdown of running Servers (preferable to powerOffServer)</div><div>rebootServer : performs guest OS initiated restart of running Servers (preferable to resetServer)</div><div>resetServer : performs hard reset of running Servers</div><div>powerOffServer : performs hard power off of running Servers</div><div>updateVmwareTools : triggers an update of the VMware Tools software running on the guest OS of the Servers</div><div>upgradeVirtualHardware : triggers an update of the VMware Virtual Hardware. VMware recommend cloning the Server prior to performing the upgrade in case something goes wrong during the upgrade process</div></td></tr>
        <tr>
<td>administratorPassword<br/><div style="font-size: small;"></div></td>
<td>no</td>
<td></td>
    <td><ul></ul></td>
    <td><div>TBC</div></td></tr>
        <tr>
<td>caas_apiurl<br/><div style="font-size: small;"></div></td>
<td>yes</td>
<td></td>
    <td><ul></ul></td>
    <td><div>Africa (AF) : https://api-mea.dimensiondata.com</div><div>Asia Pacific (AP) : https://api-ap.dimensiondata.com</div><div>Australia (AU) : https://api-au.dimensiondata.com</div><div>Canada(CA) : https://api-canada.dimensiondata.com</div><div>Europe (EU) : https://api-eu.dimensiondata.com</div><div>North America (NA) : https://api-na.dimensiondata.com</div><div>South America (SA) : https://api-latam.dimensiondata.com</div></td></tr>
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
<td>count<br/><div style="font-size: small;"></div></td>
<td>no</td>
<td>1</td>
    <td><ul></ul></td>
    <td><div>Number of instances to deploy.  Decreasing this number as no effect.</div></td></tr>
        <tr>
<td>datacenterId<br/><div style="font-size: small;"></div></td>
<td>yes</td>
<td></td>
    <td><ul></ul></td>
    <td><div>You can use your own 'Private MCP', or any public MCP 2.0 below :</div><div>Asia Pacific (AP) :</div><div>   AP3 Singapore - Serangoon</div><div>Australia (AU) :</div><div>   AU9 Australia - Sydney</div><div>   AU10  Australia - Melbourne</div><div>   AU11 New Zealand - Hamilton</div><div>Europe (EU) :</div><div>   EU6 Germany - Frankfurt</div><div>   EU7 Netherland - Amsterdam</div><div>   EU8 UK - London</div><div>North America (NA) :</div><div>   NA9 US - Ashburn</div><div>   NA12 US - Santa Clara</div></td></tr>
        <tr>
<td>description<br/><div style="font-size: small;"></div></td>
<td>no</td>
<td>Created and managed by ansible.CaaS - https://github.com/job-so/ansible.CaaS</td>
    <td><ul></ul></td>
    <td><div>Maximum length: 255 characters.</div></td></tr>
        <tr>
<td>imageId<br/><div style="font-size: small;"></div></td>
<td>no</td>
<td></td>
    <td><ul><li>present</li><li>absent</li></ul></td>
    <td><div>UUID of the Server Image being used as the target for the new Server deployment</div></td></tr>
        <tr>
<td>imageName<br/><div style="font-size: small;"></div></td>
<td>no</td>
<td></td>
    <td><ul></ul></td>
    <td><div>TBC</div></td></tr>
        <tr>
<td>name<br/><div style="font-size: small;"></div></td>
<td>yes</td>
<td></td>
    <td><ul></ul></td>
    <td><div>Name that has to be given to the instance Minimum length 1 character Maximum length 75 characters.</div></td></tr>
        <tr>
<td>networkInfo<br/><div style="font-size: small;"></div></td>
<td>no</td>
<td></td>
    <td><ul></ul></td>
    <td><div>For an MCP 2.0 request, a networkInfo element is required. networkInfo identifies the Network Domain to which the Server will be deployed.</div><div>It contains a primaryNic element defining the required NIC for the Server and optional additionalNic elements defining any additional VLAN connections for the Server.</div><div>Each NIC must contain either a VLAN ID (vlanId) OR a Private IPv4 address (privateIpv4) from the target VLAN which the NIC will associate the Server with.</div></td></tr>
        <tr>
<td>state<br/><div style="font-size: small;"></div></td>
<td>no</td>
<td>present</td>
    <td><ul><li>present</li><li>absent</li></ul></td>
    <td><div>Should the resource be present or absent.</div><div>Take care : Absent will powerOff and delete all servers.</div></td></tr>
        <tr>
<td>wait<br/><div style="font-size: small;"></div></td>
<td>no</td>
<td>True</td>
    <td><ul><li>True</li><li>False</li></ul></td>
    <td><div>TBC</div></td></tr>
    </table>
</br>
Examples
========

>     # Creates a new server named "WebServer" of CentOS 7 with default CPU/RAM/HD, 
>     #   on Vlan "vlan_webservers", in Network Domain : "ansible.Caas_SandBox"
>     -caas_server:
>         caas_apiurl: "{{ caas_apiurl }}"
>         caas_username: "{{ caas_username }}"
>         caas_password: "{{ caas_password }}"
>         datacenterId: "{{ caas_datacenter }}"
>         name: "WebServer"
>         imageName: CentOS 7 64-bit 2 CPU
>         administratorPassword: "{{ root_password }}"
>         networkInfo:
>             networkDomainName: ansible.Caas_SandBox
>             primaryNic: 
>                 vlanName: vlan_webservers
>         register: caas_server

This is an Extras Module
========================

For more information on what this means please read modules\_extra

For help in developing on modules, should you be so inclined, please
read community, developing\_test\_pr and developing\_modules.
