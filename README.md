## IDM_permissions.py - Скрипт генерации отчета о правах hbac и sudo в IDM

Собирает `IDM_permissions.csv` из правил hbac и sudo в разрезе серверов.  
В отчет не попадают правила примененные ко всем хостам 
Использовать можно на любом из хостов с установленным клиентом freeipa(IDM)  
Для запуска:  
1. Скопировать скрипт на хост
2. Запустить `python IDM_permissions.py`
3. забрать отчет `IDM_permissions.csv`

## IDM_permissions.py — script for generating a report from hbac and sudo rules in IDM

Collects `IDM_permissions.csv` from hbac and sudo rules by servers.  
The report does not use rules applicable to all hosts  
You can use it on any host with the freeipa(IDM) client installed  
To run:  
1. Copy the script on the host
2. Run `python IDM_permissions.py`
3. get the report `IDM_permissions.csv`
