# pg-perms-sync

Service to compare LDAP group members with an external CMDB API to determine logins to add and delete.  
It will then connect to the database server, apply the changes and store the results in the CMDB.  
Designed to help manage user access in an environment with hundreds of servers.  

```bash
# Provides library for managing objects in PostgreSQL
pip install -i https://test.pypi.org/simple/ pg-mgt-utils
```

## Notes

* External Services
  * LDAP Reader / Caching API
  * PostgreSQL Instance with PostgRest API
  * Hashicorp Vault for secret management

job table contains all server/databases and job_types.
Process gets an item not processed in 15 minutes and not being processed.
Marks it as being processed - job_status = 1
perform actions - writing updates to job_history table
mark as not being processed - job_status = 0
