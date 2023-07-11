import asyncio
import hashlib
import time
from concurrent.futures import ThreadPoolExecutor
from typing import List, Optional

import psycopg2
import requests


async def add_user_to_server(
    username: str,
    hashed_password: str,
    group: str,
    server: str,
    database: str,
    user: str,
    password: str,
) -> None:
    conn = psycopg2.connect(
        host=server, database=database, user=user, password=password
    )

    cur = conn.cursor()

    # Check if group exists
    cur.execute(f"SELECT 1 FROM pg_catalog.pg_roles WHERE rolname = '{group}'")
    group_exists = cur.fetchone() is not None

    if not group_exists:
        # Create group
        cur.execute(f"CREATE ROLE {group}")

    # Check if user exists
    cur.execute(f"SELECT 1 FROM pg_catalog.pg_roles WHERE rolname = '{username}'")
    user_exists = cur.fetchone() is not None

    if not user_exists:
        # Create user with hashed password
        hashed_password = hashlib.sha256(hashed_password.encode()).hexdigest()
        cur.execute(
            f"CREATE USER {username} WITH ENCRYPTED PASSWORD '{hashed_password}'"
        )

    else:
        # Update password with hashed password
        hashed_password = hashlib.sha256(hashed_password.encode()).hexdigest()
        cur.execute(
            f"ALTER USER {username} WITH ENCRYPTED PASSWORD '{hashed_password}'"
        )

    # Add user to group
    cur.execute(f"GRANT {group} TO {username}")

    conn.commit()
    cur.close()
    conn.close()


async def remove_user_from_server(
    username: str, group: str, host: str, database: str, user: str, password: str
) -> None:
    conn = psycopg2.connect(host=host, database=database, user=user, password=password)

    cur = conn.cursor()

    # Remove user from group
    cur.execute(f"REVOKE {group} FROM {username}")

    # Check if user is a member of any other groups
    # cur.execute(f"SELECT COUNT(*) FROM pg_catalog.pg_group WHERE '{username}' = ANY(grolist)")
    cur.execute(
        f"""SELECT oid FROM pg_roles WHERE oid IN (
                       SELECT roleid FROM  pg_auth_members 
                        WHERE member=(SELECT oid FROM pg_roles WHERE rolname='{username}')
                    );
                """
    )
    result = cur.fetchone()
    is_member_of_other_groups = result[0] > 0 if result is not None else False

    if not is_member_of_other_groups:
        # Check if user owns any objects
        cur.execute(
            f"SELECT relname, relkind FROM pg_catalog.pg_class WHERE relowner = (SELECT oid FROM pg_roles WHERE rolname='{username}')"
        )
        objects_owned = cur.fetchall()

        for obj in objects_owned:
            # Reassign ownership to database owner
            cur.execute(
                f"SELECT datdba FROM pg_catalog.pg_database WHERE datname = '{database}'"
            )
            result = cur.fetchone()
            database_owner = result[0] if result is not None else "postgres"
            cur.execute(f"ALTER {obj[1]} {obj[0]} OWNER TO {database_owner}")

        # Drop user
        cur.execute(f"DROP USER {username}")

    conn.commit()
    cur.close()
    conn.close()


async def sync_roles() -> None:
    print("Syncing roles")
    time.sleep(5)
    print("Roles synced")


async def get_servers() -> Optional[List[str]]:
    response = requests.get("http://localhost:8000/api/v1/servers")
    if response.status_code == 200:
        servers = response.json()
        return servers
    else:
        print("Error getting servers")


async def get_local_groups(server_name: str) -> Optional[List[str]]:
    # Your code to get local groups goes here
    response = requests.get(f"http://localhost:8000/api/v1/server/{server_name}")
    if response.status_code == 200:
        groups = response.json()["groups"]
        return groups
    else:
        print("Error getting groups")


async def get_local_group_members(server_name: str, group: str) -> List[str]:
    # Your code to get external group members goes here
    response = requests.get(f"http://localhost:8000/api/v1/group/{server_name}/{group}")
    if response.status_code == 200:
        members = response.json()["members"]
        return members
    else:
        print(
            f"Error getting local group members for group {group} on server {server_name}"
        )
        return []


async def get_external_group_members(group: str) -> List[str]:
    # Your code to get external group members goes here
    response = requests.get(f"http://localhost:8001/ldap_group/{group}?refresh=true")
    if response.status_code == 200:
        members = response.json()["members"]
        return members
    else:
        print(f"Error getting external group members for group {group}")
        return []


async def process_servers(batch_size: int = 10) -> None:
    servers = await get_servers()
    if servers is None:
        print("No servers found")
        return

    with ThreadPoolExecutor() as executor:
        futures = []
        for server in servers:
            future = executor.submit(process_server, server)
            futures.append(future)

            if len(futures) >= batch_size:
                await asyncio.gather(*futures)
                futures = []

        if futures:
            await asyncio.gather(*futures)


async def process_server(server: str) -> None:
    local_groups = await get_local_groups(server)
    if local_groups is None:
        print(f"No local groups found for server {server}")
        return

    for group in local_groups:
        external_members = await get_external_group_members(group)
        local_members = await get_local_group_members(server, group)

        members_to_add = set(external_members) - set(local_members)
        members_to_remove = set(local_members) - set(external_members)

        # Your code to add or remove members goes here
        print(
            f"Group {group}: {len(members_to_add)} members to add, {len(members_to_remove)} members to remove"
        )
