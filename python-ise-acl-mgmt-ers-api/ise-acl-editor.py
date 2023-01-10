#!/usr/bin/env python3

"""
Copyright (c) 2018-2020 Cisco and/or its affiliates.
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import json
import requests
import sys
import csv
from requests.auth import HTTPBasicAuth
from pathlib import Path
from crayons import green, yellow, white, red
from requests.packages.urllib3.exceptions import InsecureRequestWarning


# Locate the directory containing this file and the repository root.
# Temporarily add these directories to the system path so that we can import
# local files.
here = Path(__file__).parent.absolute()
repository_root = (here / ".." ).resolve()
sys.path.insert(0, str(repository_root))

# Disable insecure request warnings
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Contants

ise_user = "admin"
ise_password = "C!sco123"
ise_host = "10.95.61.22"
ise_port = "9060"

# Functions

def get_acl_list(host,port,user,password):
    """Get the list of ACLs from ISE ERS API."""

    print("\n==> Sending API request to ISE...")
    uri = f"https://{host}:{port}/ers/config/downloadableacl"
    headers = {'Accept': 'application/json','Content-Type': 'application/json'}
    response = requests.get(uri, auth=HTTPBasicAuth(user, password), headers=headers, verify=False)
    # Consider any status other than 2xx an error
    response.raise_for_status()

    acl_list = response.json()["SearchResult"]["resources"]

    return acl_list

def get_acl_entry(host,port,user,password,acl_id):
    """Get the ACL details for every ACL from the list."""
    
    #print("\n==> Sending API request to ISE...")
    uri = f"https://{host}:{port}/ers/config/downloadableacl/{acl_id}"
    headers = {'Accept': 'application/json','Content-Type': 'application/json'}
    response = requests.get(uri, auth=HTTPBasicAuth(user, password), headers=headers, verify=False)
    # Consider any status other than 2xx an error
    response.raise_for_status()

    acl_entry = response.json()["DownloadableAcl"]

    return acl_entry
    
def update_acl_entry(host,port,user,password,acl_entry):
    """Update ACL entry."""
    
    print("\n==> Sending API request to ISE...")
    uri = f"https://{host}:{port}/ers/config/downloadableacl/{acl_entry['id']}"
    headers = {'Accept': 'application/json','Content-Type': 'application/json'}
    body = {"DownloadableAcl": acl_entry}
    try:
        response = requests.put(uri, auth=HTTPBasicAuth(user, password), headers=headers, data=json.dumps(body), verify=False)
        # Consider any status other than 2xx an error
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        #raise SystemExit(err)
        print(red(f"\n\nERROR: {err}"))

    return response.json()

def write_to_file(filename,acl_entries):
    """Write ACLs to file."""

    with open(filename, 'w') as csvfile:
        fieldnames = acl_entries[0].keys()
        csvwriter = csv.DictWriter(csvfile,fieldnames)
        csvwriter.writeheader()
        csvwriter.writerows(acl_entries)

# If this script is the "main" script, run...
if __name__ == "__main__":

    # Get the number of line to add to ACLs
    n_lines=input(yellow("How many line you would like to add to all ACLs:\n"))
    add_acl_line = ""

    for n in range(0,int(n_lines)):
        # Get user input on what acl line to add to ACLs
        acl_line = input(yellow(f"Please enter an ACL entry number {n} to add at the top of each ACL:\n"))
        add_acl_line = acl_line + "\n"+add_acl_line

    print(white(f"\nGet ACL list from ISE"))
    # Get the list of ACLs from ISE ERS API
    ise_acl_list = get_acl_list(ise_host,ise_port,ise_user,ise_password)

    print(white(f"\nGet ACL entries from ISE"))
    
    ise_acl_entries = []

    for acl in ise_acl_list:
        # For each ACL ID get ACL details from ISE
        ise_acl_entry = get_acl_entry(ise_host,ise_port,ise_user,ise_password,acl["id"])
        # Append to the list of entries
        ise_acl_entries.append(ise_acl_entry)
    
    
    print(white(f"\nWrite the original ACLs to file"))
    # Write the original ACLs to file
    write_to_file("ise-acl-list-old.csv",ise_acl_entries)
    
    print(white(f"\nUpdate ACL entries in ISE"))
    for acl in ise_acl_entries:
        # Append new ACLs entry to every ACL
        acl["dacl"] = add_acl_line+'\n'+acl["dacl"]
        # Update ACL entry in ISE
        result = update_acl_entry(ise_host,ise_port,ise_user,ise_password,acl)
        print(green(f"\nResult: {result}"))

    # Get all ACLs from ISE to verify that they were updated
    ise_acl_updated = []

    for acl in ise_acl_list:
        # For each ACL ID get ACL details from ISE
        ise_acl_entry = get_acl_entry(ise_host,ise_port,ise_user,ise_password,acl["id"])
        # Append to the list of entries
        ise_acl_updated.append(ise_acl_entry)
    
    # Write the new ACLs to file
    print(white(f"\nWrite the new ACLs to file"))
    write_to_file("ise-acl-list-new.csv",ise_acl_updated)
