---
title: |
    caas\_credentials - Check Dimension Data Managed Cloud Platform
    credentials
...

Synopsis
========

Check Dimension Data Managed Cloud Platform credentials This step is
optionnal

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
<td>apiurl<br/><div style="font-size: small;"></div></td>
<td>yes</td>
<td></td>
    <td><ul></ul></td>
    <td><div>Africa (AF) : https://api-mea.dimensiondata.com</div><div>Asia Pacific (AP) : https://api-ap.dimensiondata.com</div><div>Australia (AU) : https://api-au.dimensiondata.com</div><div>Canada(CA) : https://api-canada.dimensiondata.com</div><div>Europe (EU) : https://api-eu.dimensiondata.com</div><div>North America (NA) : https://api-na.dimensiondata.com</div><div>South America (SA) : https://api-latam.dimensiondata.com</div></td></tr>
        <tr>
<td>datacenterId<br/><div style="font-size: small;"></div></td>
<td>yes</td>
<td></td>
    <td><ul></ul></td>
    <td><div>You can use your own 'Private MCP', or any public MCP 2.0 below :</div><div>Asia Pacific (AP) :</div><div>   AP3 Singapore - Serangoon</div><div>   AP4 Japan - Tokyo</div><div>Australia (AU) :</div><div>   AU9 Australia - Sydney</div><div>   AU10  Australia - Melbourne</div><div>   AU11 New Zealand - Hamilton</div><div>Europe (EU) :</div><div>   EU6 Germany - Frankfurt</div><div>   EU7 Netherland - Amsterdam</div><div>   EU8 UK - London</div><div>North America (NA) :</div><div>   NA9 US - Ashburn</div><div>   NA12 US - Santa Clara</div></td></tr>
        <tr>
<td>password<br/><div style="font-size: small;"></div></td>
<td>yes</td>
<td></td>
    <td><ul></ul></td>
    <td><div>The associated password</div></td></tr>
        <tr>
<td>username<br/><div style="font-size: small;"></div></td>
<td>yes</td>
<td></td>
    <td><ul></ul></td>
    <td><div>Your username credential</div></td></tr>
    </table>
</br>
Examples
========

>     # Check credentials with username/password provided inside playbook (not recommended)
>         tasks:
>           - name: Check credentials (optionnal Step)
>             caas_credentials:
>               apiurl: https://api-eu.dimensiondata.com
>               username: firstname.lastname
>               password: MySecret_KeepItSecret
>               datacenterId: EU6 
>             register: cas_credentials
>
>     # Check credentials with username/password provided in an external file (recommended)
>       - name: Deploy Dimension Data infrastructure  
>         hosts: localhost
>         vars_files:
>           - /root/caas_credentials.yml
>         tasks:
>           - name: Check credentials (optionnal Step)
>             caas_credentials:
>               username: "{{caas_credentials.username}}"
>               password: "{{caas_credentials.password}}"
>               apiurl: "{{caas_credentials.apiurl}}"
>               datacenter: "{{caas_credentials.datacenter}}" 
>             register: caas_credentials
>
>     # Content of the external file /root/caas_credentials.yml
>     caas_credentials:
>         username: firstname.lastname
>         password: MySecret_KeepItSecret
>         apiurl: https://api-eu.dimensiondata.com
>         datacenter: EU6 

Return Values
=============

Common return values are documented here common\_return\_values, the
following are the fields unique to this module:

<table border=1 cellpadding=4>
<tr>
<th class="head">name</th>
<th class="head">description</th>
<th class="head">returned</th>
<th class="head">type</th>
<th class="head">sample</th>
</tr>

    <tr>
    <td> caas_credentials </td>
    <td> destination file/path </td>
    <td align=center> success </td>
    <td align=center> string </td>
    <td align=center> https://api-eu.dimensiondata.com </td>
</tr>

</table>
</br></br>
This is an Extras Module
========================

For more information on what this means please read modules\_extra

For help in developing on modules, should you be so inclined, please
read community, developing\_test\_pr and developing\_modules.
