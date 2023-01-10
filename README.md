# ISE downloadable ACL Management using ERS API and SecureX Orchestration

## Python Script

What this script will do:
* Take the unmber of lines to add to each ACL and each ACL entry as an input.
* Save the original ACLs to a csv file.
* Append provided entries to all ACLs __ise-acl-list-old.csv__.
* Get the new ACLs and save to a csv file __ise-acl-list-new.csv__.

Please take a look at the [demo](https://www.youtube.com/watch?v=zyQevR7SGZU) that shows the use case for this script.

## SecureX Orchestration

This SecureX Orchestration workflow will add one ACL line at the end of each downloadable ACL list in ISE configuration. 

## Requirements

###Targets

**Note:** If your Cisco ISE deployment is on-premises and not accessible from the internet, you will need a [SecureX orchestration remote](https://ciscosecurity.github.io/sxo-05-security-workflows/remote/) to use ISE with orchestration.

**Target Group:** Default TargetGroup
| Target Name |	Type |	Details |	Account Keys |	Notes |
|-------------|------|--------|--------|--------|
|ISE_ERS_Target |	HTTP Endpoint |	Protocol: HTTPS<br>Host: ISE Primary Admin Node<br>Port: 9060<br>Path: None| ISE_ERS_Credentials |	 |
