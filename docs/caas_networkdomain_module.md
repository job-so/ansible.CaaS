---
title: |
    caas\_networkdomain - Create, Configure, Remove Network Domain on
    Dimension Data Managed Cloud Platform
...

Synopsis
========

Create, Remove Network domains on Dimension Data Managed Cloud Platform

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
<td>caas_credentials<br/><div style="font-size: small;"></div></td>
<td>yes</td>
<td></td>
    <td><ul></ul></td>
    <td><div>Complexe variable containing credentials. From an external file or from module caas_credentials (See related documentation)</div></td></tr>
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
    <td><div>Name that has to be given to the instance</div><div>Minimum length 1 character Maximum length 75 characters.</div></td></tr>
        <tr>
<td>state<br/><div style="font-size: small;"></div></td>
<td>no</td>
<td>present</td>
    <td><ul><li>present</li><li>absent</li></ul></td>
    <td><div>Should the resource be present or absent.</div><div>Take care : Absent will delete the networkdomain</div></td></tr>
    </table>
</br>
Examples
========

>     # Creates a new networkdomain named "ansible.Caas_SandBox", 
>         tasks:
>           - name: Deploy my Nework Domain
>             caas_networkdomain:
>               caas_credentials: "{{ caas_credentials }}"
>               name: ansible.CaaS_Sandbox
>               type: ADVANCED
>             register: caas_networkdomain

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
    <td> networkdomains </td>
    <td>  </td>
    <td align=center>  </td>
    <td align=center>  </td>
    <td align=center>  </td>
</tr>

</table>
</br></br>
This is an Extras Module
========================

For more information on what this means please read modules\_extra

For help in developing on modules, should you be so inclined, please
read community, developing\_test\_pr and developing\_modules.
