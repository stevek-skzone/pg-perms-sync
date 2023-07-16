import asyncio
import hashlib
import time
from concurrent.futures import ThreadPoolExecutor
from typing import List, Optional

import psycopg
import requests
from psycopg import sql


async def add_user_to_server(
    username: str,
    hashed_password: str,
    group: str,
    server: str,
    database: str,
    user: str,
    password: str,
) -> None:
    """
    Adds a new user to a group on a PostgreSQL server.

    Args:
        username (str): The name of the user to add.
        hashed_password (str): The hashed password of the user to add.
        group (str): The name of the group to add the user to.
        server (str): The hostname or IP address of the PostgreSQL server.
        database (str): The name of the PostgreSQL database.
        user (str): The username to use to connect to the PostgreSQL server.
        password (str): The password to use to connect to the PostgreSQL server.

    Returns:
        None
    """
    conn = psycopg.connect(
        host=server, dbname=database, user=user, password=password, autocommit=True
    )

    cur = conn.cursor()

    # Check if group exists
    cur.execute("SELECT 1 FROM pg_catalog.pg_roles WHERE rolname = %s", (group,))
    group_exists = cur.fetchone() is not None

    if not group_exists:
        # Create group
        cur.execute(sql.SQL("CREATE ROLE {group}").format(group=sql.Identifier(group)))

    # Check if user exists
    cur.execute("SELECT 1 FROM pg_catalog.pg_roles WHERE rolname = %s", (username,))
    user_exists = cur.fetchone() is not None

    if not user_exists:
        # Create user with hashed password
        hashed_password = hashlib.sha256(hashed_password.encode()).hexdigest()
        cur.execute(
            sql.SQL("CREATE ROLE {username} WITH ENCRYPTED PASSWORD %s").format(
                username=sql.Identifier(username)
            ),
            (sql.Literal(hashed_password),),
        )

    else:
        # Update password with hashed password
        hashed_password = hashlib.sha256(hashed_password.encode()).hexdigest()
        cur.execute(
            sql.SQL("ALTER ROLE {username} WITH ENCRYPTED PASSWORD %s").format(
                username=sql.Identifier(username)
            ),
            (hashed_password,),
        )

    # Add user to group
    cur.execute(
        sql.SQL("GRANT {group} TO {username}").format(
            group=sql.Identifier(group), username=sql.Identifier(username)
        )
    )

    conn.commit()
    cur.close()
    conn.close()


async def remove_user_from_server(
    username: str, group: str, host: str, database: str, user: str, password: str
) -> None:
    """
    Removes a user from a group on a PostgreSQL server.

    Args:
        username (str): The name of the user to remove.
        group (str): The name of the group to remove the user from.
        server (str): The hostname or IP address of the PostgreSQL server.
        database (str): The name of the PostgreSQL database.
        user (str): The username to use to connect to the PostgreSQL server.
        password (str): The password to use to connect to the PostgreSQL server.

    Returns:
        None
    """
    conn = psycopg.connect(
        host=host, dbname=database, user=user, password=password, autocommit=True
    )

    cur = conn.cursor()

    # Remove user from group
    cur.execute(
        sql.SQL("REVOKE {group} FROM {username}").format(
            group=sql.Identifier(group), username=sql.Identifier(username)
        )
    )

    # Check if user is a member of any other groups
    cur.execute(
        """SELECT oid FROM pg_roles WHERE oid IN (
                            SELECT roleid FROM pg_auth_members 
                            WHERE member=(SELECT oid FROM pg_roles WHERE rolname=%s)
                        )""",
        (username,),
    )

    result = cur.fetchone()
    is_member_of_other_groups = result[0] > 0 if result is not None else False

    if not is_member_of_other_groups:
        # Check if user owns any objects
        cur.execute(
            """SELECT relname, relkind FROM pg_catalog.pg_class WHERE relowner = (
                                SELECT oid FROM pg_roles WHERE rolname=%s
                            )""",
            (username,),
        )
        objects_owned = cur.fetchall()

        for obj in objects_owned:
            # Reassign ownership to database owner
            cur.execute(
                "SELECT datdba FROM pg_catalog.pg_database WHERE datname = %s",
                (database,),
            )
            result = cur.fetchone()
            database_owner = result[0] if result is not None else "postgres"
            cur.execute(
                sql.SQL("ALTER {obj_type} {obj_name} OWNER TO {database_owner}").format(
                    obj_type=sql.Identifier(obj[1]),
                    obj_name=sql.Identifier(obj[0]),
                    database_owner=sql.Identifier(database_owner),
                )
            )

        # Drop user
        cur.execute(
            sql.SQL("DROP ROLE {username}").format(username=sql.Identifier(username))
        )

    conn.commit()
    cur.close()
    conn.close()


async def sync_roles() -> None:
    """
    Synchronizes roles between external and local groups.

    Returns:
        None
    """
    print("Syncing roles")
    time.sleep(5)
    print("Roles synced")


async def get_servers() -> Optional[List[str]]:
    """
    Gets a list of servers from an external API.

    Returns:
        List[str]: A list of server names.
    """
    response = requests.get("http://localhost:8000/api/v1/servers", timeout=5)
    if response.status_code == 200:
        servers = response.json()
        return servers

    print("Error getting servers")


async def get_local_groups(server_name: str) -> Optional[List[str]]:
    """
    Gets a list of local groups from a PostgreSQL server.

    Args:
        server (str): The hostname or IP address of the PostgreSQL server.

    Returns:
        List[str]: A list of group names.
    """
    response = requests.get(
        f"http://localhost:8000/api/v1/server/{server_name}", timeout=5
    )
    if response.status_code == 200:
        groups = response.json()["groups"]
        return groups

    print("Error getting groups")


async def get_local_group_members(server_name: str, group: str) -> List[str]:
    """
    Gets a list of members for a local group from a PostgreSQL server.

    Args:
        server_name (str): The hostname or IP address of the PostgreSQL server.
        group (str): The name of the group.

    Returns:
        List[str]: A list of member names.
    """
    response = requests.get(
        f"http://localhost:8000/api/v1/group/{server_name}/{group}", timeout=5
    )
    if response.status_code == 200:
        members = response.json()["members"]
        return members

    print(
        f"Error getting local group members for group {group} on server {server_name}"
    )
    return []


async def get_external_group_members(group: str) -> List[str]:
    """
    Gets a list of members for an external group from an API.

    Args:
        group (str): The name of the group.

    Returns:
        List[str]: A list of member names.
    """
    response = requests.get(
        f"http://localhost:8001/ldap_group/{group}?refresh=true", timeout=5
    )
    if response.status_code == 200:
        members = response.json()["members"]
        return members

    print(f"Error getting external group members for group {group}")
    return []


async def process_servers(batch_size: int = 10) -> None:
    """
    Processes a batch of servers.

    Args:
        batch_size (int): The number of servers to process in a batch.

    Returns:
        None
    """
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
    """
    Processes a server.

    Args:
        server (str): The name of the server.

    Returns:
        None
    """
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
            f"""Group {group}: {len(members_to_add)} members to add, 
            {len(members_to_remove)} members to remove"""
        )
