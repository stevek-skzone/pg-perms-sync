import asyncio
import hashlib
import time
from concurrent.futures import ThreadPoolExecutor
from typing import List, Optional

# import psycopg
import requests

# from psycopg import sql
from pg_mgt_utils.pg_client import PgClient
from pg_mgt_utils.pg_common import pg_scram_sha256

from app.config import config

# Get jobs from postgrest
# Get all groups for a server
# Get records from ldap
# Compare records
#  - if ldap record not in postgrest, add it
#  - if postgrest record not in ldap, remove it


async def get_jobs() -> Optional[List[dict]]:
    """
    Gets a list of jobs from a PostgRest API.

    Returns:
        List[dict]: A list of jobs.
    """
    response = requests.get(f"{config.POSTGREST_URL}/job", timeout=5)
    if response.status_code == 200:
        jobs = response.json()
        return jobs

    return None


async def get_groups(server_name: str) -> Optional[List[str]]:
    """
    Gets a list of groups from a PostgRest API for a server.

    Args:
        server_name (str): The name of the server.

    Returns:
        List[str]: A list of group names.
    """
    # use api to get groups
    response = requests.get(
        f"{config.POSTGREST_URL}/group?server_name=eq.{server_name}", timeout=5
    )
    if response.status_code == 200:
        groups = response.json()
        return groups  # list of dicts with group_name and server_name

    return None


async def get_group_from_ldap(group_name: str) -> Optional[List[str]]:
    """
    Gets a list of members for an external group from an API.

    Args:
        group (str): The name of the group.

    Returns:
        List[str]: A list of member names.
    """
    response = requests.get(
        f"{config.ENTITLEMENT_CACHE_SERVER}/ldap_group/{group_name}", timeout=5
    )
    if response.status_code == 200:
        members = response.json()["members"]
        return members

    print(f"Error getting external group members for group {group_name}")
    return []


# function that compares a source and target list and returns a list of items to add and a list of items to remove
def compare_lists(source: List[str], target: List[str]) -> tuple:
    """
    Compares two lists and returns a tuple of lists of items to add and items to remove.

    Args:
        source (List[str]): The source list.
        target (List[str]): The target list.

    Returns:
        tuple: A tuple of lists of items to add and items to remove.
    """
    items_to_add = set(source) - set(target)
    items_to_remove = set(target) - set(source)

    return items_to_add, items_to_remove


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
    pg_client = PgClient(server, user, password, database)

    result = pg_client.check_user_exists(username)
    if not result:
        hashed_password = pg_scram_sha256()
        pg_client.create_user(username, hashed_password)


async def remove_user_from_server(
    username: str, group: str, server: str, database: str, user: str, password: str
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
    pg_client = PgClient(server, user, password, database)

    result = pg_client.check_user_exists(username)
    if result:
        pg_client.drop_user(username)


async def process_servers(batch_size: int = 10) -> None:
    """
    Processes a batch of jobs.

    Args:
        batch_size (int): The number of jobs to process in a batch.

    Returns:
        None
    """
    jobs = await get_jobs()
    if jobs is None:
        print("No jobs found")
        return

    with ThreadPoolExecutor() as executor:
        futures = []
        for job in jobs:
            future = executor.submit(process_server, job)
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
    server_groups = await get_groups(server)
    if server_groups is None:
        print(f"No groups found for server {server}")
        return

    for group in server_groups:
        ldap_members = await get_group_from_ldap(group["group_name"])
        server_members = group["members"]

        members_to_add, members_to_remove = compare_lists(ldap_members, server_members)

        # Your code to add or remove members goes here
        print(
            f"""Group {group}: {len(members_to_add)} members to add,
            {len(members_to_remove)} members to remove"""
        )
