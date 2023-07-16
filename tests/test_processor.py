import asyncio
import os
import sys
from unittest.mock import MagicMock, Mock, patch

import psycopg2
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.processor import (
    add_user_to_server,
    get_external_group_members,
    get_local_group_members,
    get_local_groups,
    get_servers,
    process_server,
    process_servers,
    remove_user_from_server,
    sync_roles,
)

# from app.main import app

# client = TestClient(app)


def test_add_user_to_server():
    # Test adding a new user to a new group
    username = "testuser"
    hashed_password = "testpassword"
    group = "testgroup"
    server = "localhost"
    database = "postgres"
    user = "postgres"
    password = "example"

    asyncio.run(
        add_user_to_server(
            username, hashed_password, group, server, database, user, password
        )
    )

    # Check that the user was added to the group
    conn = psycopg2.connect(
        host=server, database=database, user=user, password=password
    )
    cur = conn.cursor()
    cur.execute(f"SELECT 1 FROM pg_catalog.pg_roles WHERE rolname = '{username}'")
    result = cur.fetchone()
    assert result is not None
    cur.close()
    conn.close()


# def test_remove_user_from_server():
#     # Test removing a user from a group
#     username = "testuser"
#     group = "testgroup"
#     server = "localhost"
#     database = "postgres"
#     user = "postgres"
#     password = "example"

#     asyncio.run(
#         remove_user_from_server(username, group, server, database, user, password)
#     )

#     # Check that the user was removed from the group
#     conn = psycopg2.connect(
#         host=server, database=database, user=user, password=password
#     )
#     cur = conn.cursor()
#     cur.execute(f"SELECT 1 FROM pg_catalog.pg_roles WHERE rolname = '{username}'")
#     result = cur.fetchone()
#     assert result is None
#     cur.close()
#     conn.close()


# @patch("app.services.processor.time.sleep")
# def test_sync_roles(mock_sleep):
#     # Test syncing roles
#     asyncio.run(sync_roles())
#     mock_sleep.assert_called_once_with(5)


# @patch("app.services.processor.requests.get")
# def test_get_servers(mock_get):
#     # Test getting servers
#     mock_response = MagicMock()
#     mock_response.status_code = 200
#     mock_response.json.return_value = ["testserver1", "testserver2"]
#     mock_get.return_value = mock_response

#     servers = asyncio.run(get_servers())
#     assert servers == ["testserver1", "testserver2"]


# @patch("app.services.processor.requests.get")
# def test_get_local_groups(mock_get):
#     # Test getting local groups
#     mock_response = MagicMock()
#     mock_response.status_code = 200
#     mock_response.json.return_value = {"groups": ["testgroup1", "testgroup2"]}
#     mock_get.return_value = mock_response

#     groups = asyncio.run(get_local_groups("testserver"))
#     assert groups == ["testgroup1", "testgroup2"]


# @patch("app.services.processor.requests.get")
# def test_get_local_group_members(mock_get):
#     # Test getting local group members
#     mock_response = MagicMock()
#     mock_response.status_code = 200
#     mock_response.json.return_value = {"members": ["testuser1", "testuser2"]}
#     mock_get.return_value = mock_response

#     members = asyncio.run(get_local_group_members("testserver", "testgroup"))
#     assert members == ["testuser1", "testuser2"]


# @patch("app.services.processor.requests.get")
# def test_get_external_group_members(mock_get):
#     # Test getting external group members
#     mock_response = MagicMock()
#     mock_response.status_code = 200
#     mock_response.json.return_value = {"members": ["testuser1", "testuser2"]}
#     mock_get.return_value = mock_response

#     members = asyncio.run(get_external_group_members("testgroup"))
#     assert members == ["testuser1", "testuser2"]


# @patch("app.services.processor.get_local_group_members")
# @patch("app.services.processor.get_external_group_members")
# def test_process_server(mock_external_members, mock_local_members):
#     # Test processing a server
#     mock_external_members.return_value = ["testuser1", "testuser2"]
#     mock_local_members.return_value = ["testuser2", "testuser3"]

#     mock_print = Mock()
#     with patch("builtins.print", mock_print):
#         asyncio.run(process_server("server1"))

#     # Check that the correct number of members were added and removed
#     mock_print.assert_called_with(
#         "Group testgroup: 1 members to add, 1 members to remove"
#     )
