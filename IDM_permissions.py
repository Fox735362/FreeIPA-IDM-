from ipalib import api
from pprint import pprint
import time
import csv


api.bootstrap(context="custom", in_server=False)
api.finalize()

ipa_host_dict = {}
ipa_sudorule_dict = {}
ipa_hbacrule_dict = {}
ipa_group_dict = {}
ipa_hostgroup_dict = {}

if api.env.in_server:
    api.Backend.ldap2.connect()
else:
    api.Backend.rpcclient.connect()

raw_host_settings = ipa_host_settings_all=api.Command.host_find(all=True)['result']
for i in raw_host_settings:
    tmp_hbacrule = []
    tmp_sudorule = []
    if 'memberof_hbacrule' in i:
        tmp_hbacrule+=i['memberof_hbacrule']
    if 'memberofindirect_hbacrule' in i:
        tmp_hbacrule+=i['memberofindirect_hbacrule']
    if 'memberof_sudorule' in i:
        tmp_sudorule+=i['memberof_sudorule']
    if 'memberofindirect_sudorule' in i:
        tmp_sudorule+=i['memberofindirect_sudorule']
    ipa_host_dict[i['fqdn'][0]]={
        "hbacrule":tmp_hbacrule, "sudorule":tmp_sudorule,
        "hbac_users":[], "sudo_users":[]
    }

raw_group_settings = api.Command.group_find(all=True)['result']
for i in raw_group_settings:
    tmp_member_user = []
    if 'member_user' in i:
        tmp_member_user+=i['member_user']
    if 'memberindirect_user' in i:
        tmp_member_user+=i['memberindirect_user']
    ipa_group_dict[(i['cn'][0])]={
        "member_user":tmp_member_user
    }

raw_hostgroup_settings = api.Command.hostgroup_find(all=True)['result']
for i in raw_hostgroup_settings:
    tmp_member_host = []
    if 'member_host' in i:
        tmp_member_host+=i['member_host']
    if 'memberindirect_host' in i:
        tmp_member_host+=i['memberindirect_host']
    ipa_hostgroup_dict[(i['cn'][0])]={
        "member_host":tmp_member_host
    }

raw_hbacrule_settings = ipa_host_settings_all=api.Command.hbacrule_find(all=True)['result']
for i in raw_hbacrule_settings:
    tmp_memberhost = []
    tmp_memberuser = []
    if i['accessruletype'][0]=='allow':
        if 'memberhost_host' in i:
            tmp_memberhost+=i['memberhost_host']
        if 'memberhost_hostgroup' in i:
            for host_grp in i['memberhost_hostgroup']:
                tmp_memberhost+=ipa_hostgroup_dict[host_grp]['member_host']
        if 'memberuser_group' in i:
            for user_grp in i['memberuser_group']:
                tmp_memberuser+=ipa_group_dict[user_grp]['member_user']
        if 'memberuser_user' in i:
            tmp_memberuser+=i['memberuser_user']
    ipa_hbacrule_dict[i['cn'][0]]={
        "memberhost":tmp_memberhost, "memberuser":tmp_memberuser
    }

raw_sudorule_settings = ipa_host_settings_all=api.Command.sudorule_find(all=True)['result']
for i in raw_sudorule_settings:
    tmp_memberhost = []
    tmp_memberuser = []
    if 'cmdcategory' in i:
        if i['cmdcategory'][0]=='all':
            if 'memberhost_host' in i:
                tmp_memberhost+=i['memberhost_host']
            if 'memberhost_hostgroup' in i:
                for host_grp in i['memberhost_hostgroup']:
                    tmp_memberhost+=ipa_hostgroup_dict[host_grp]['member_host']
                    tmp_memberhost+=i['memberhost_hostgroup']
            if 'memberuser_group' in i:
                for user_grp in i['memberuser_group']:
                    tmp_memberuser+=ipa_group_dict[user_grp]['member_user']
            if 'memberuser_user' in i:
                tmp_memberuser+=i['memberuser_user']
    ipa_sudorule_dict[i['cn'][0]]={
        "memberhost":tmp_memberhost, "memberuser":tmp_memberuser
    }

for ipa_host in ipa_host_dict:
    if ipa_host_dict[ipa_host]['hbacrule']:
        for hbacrule in ipa_host_dict[ipa_host]['hbacrule']:
            ipa_host_dict[ipa_host]['hbac_users']+=ipa_hbacrule_dict[hbacrule]['memberuser']
            ipa_host_dict[ipa_host]['hbac_users']=list(dict.fromkeys(ipa_host_dict[ipa_host]['hbac_users']))
        for sudorule in ipa_host_dict[ipa_host]['sudorule']:
            ipa_host_dict[ipa_host]['sudo_users']+=ipa_sudorule_dict[sudorule]['memberuser']
            ipa_host_dict[ipa_host]['sudo_users']=list(dict.fromkeys(ipa_host_dict[ipa_host]['sudo_users']))

final_host_list = []
for ipa_host in ipa_host_dict:
    temp_dict = {'fqdn':ipa_host,
                 'hbac_users':ipa_host_dict[ipa_host]['hbac_users'],
                 'sudo_users':ipa_host_dict[ipa_host]['sudo_users'],
                 'hbacrule':ipa_host_dict[ipa_host]['hbacrule'],
                 'sudorule':ipa_host_dict[ipa_host]['sudorule']
    }
    final_host_list.append(temp_dict)

fieldnames = final_host_list[0].keys()
csv_file_name = 'IDM_permissions.csv'

try:
    with open(csv_file_name, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        writer.writerows(final_host_list)
    print(f"CSV file '{csv_file_name}' created successfully.")

except IOError as e:
    print(f"Error writing to CSV file: {e}")
