from typing import List, Dict, Any
from fastapi import APIRouter

router: APIRouter = APIRouter()

# Define some example data
test_data: Dict[str, Dict[str, Any]] = {
    "server1": {
        "metadata": {
            "connection": "localhost:8000",
            "last_processed": "2022-01-15T12:00:00Z"
        },
        "groups": {
            "group1": {
                "metadata": {
                    "registered": "2022-01-01",
                    "processed": True,
                    "roles": ["admin", "editor", "viewer"]
                },
                "members": [
                    {"name": "Alice", "date_added": "2022-01-01T12:00:00Z"},
                    {"name": "Bob", "date_added": "2022-01-01T12:00:00Z"},
                    {"name": "Charlie", "date_added": "2022-01-01T12:00:00Z"}
                ]
            },
            "group2": {
                "metadata": {
                    "registered": "2022-01-02",
                    "processed": False,
                    "roles": []
                }
            }
        }
    },
    "server2": {
        "metadata": {
            "connection": "localhost:8001",
            "last_processed": "2022-01-14T12:00:00Z"
        },
        "groups": {
            "group3": {
                "metadata": {
                    "registered": "2022-01-03",
                    "processed": True,
                    "roles": ["viewer"]
                },
                "members": [
                    {"name": "Frank", "date_added": "2022-01-03T12:00:00Z"}
                ]
            }
        }
    }
}

@router.get("/servers", description="Get servers", response_model=List[Dict[str, str]])
async def get_server_list() -> List[Dict[str, str]]:
    servers: List[Dict[str, str]] = []
    for server_name, values in test_data.items():
        servers.append({"server_name": server_name, "connection": values["metadata"]["connection"]})

    return servers


@router.get("/server/{server_name}", description="Get server groups", response_model=Dict[str, Any])
async def get_server(server_name: str) -> Dict[str, Any]:
    if server_name not in test_data:
        return {"error": "Server not found"}

    groups: List[str] = []
    for group in test_data[server_name]["groups"]:
        groups.append(group)

    return {"server_name": server_name, "groups": groups}

@router.get("/group/{server_name}/{group_name}", description="Get server group metadata", response_model=Dict[str, Any])
async def get_group(server_name: str, group_name: str) -> Dict[str, Any]:
    if server_name not in test_data or group_name not in test_data[server_name]["groups"]:
        return {"error": "Server or group not found"}

    group: Dict[str, Any] = test_data[server_name]["groups"][group_name]
    metadata: Dict[str, Any] = {"registered": group["metadata"]["registered"], 
                "processed": group["metadata"]["processed"],
                "roles": group["metadata"]["roles"]}

    if not group["metadata"]["processed"]:
        members = []
    else:    
        members: List[Dict[str, Any]] = group["members"]

    return {"server_name": server_name, "group_name": group_name, "metadata": metadata, "members": members}

@router.get("/servers/{server_name}/members", description="Get all members of a server", response_model=Dict[str, Any])
async def get_all_members(server_name: str) -> Dict[str, Any]:
    if server_name not in test_data:
        return {"error": "Server not found"}

    members: List[Dict[str, Any]] = []
    for group_name, group in test_data[server_name]["groups"].items():
        if group["metadata"]["processed"]:
            for member in group["members"]:
                member["roles"] = member["roles"].split(",")
                members.append(member)

    return {"server_name": server_name, "members": members}