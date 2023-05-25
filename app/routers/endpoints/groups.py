from fastapi import APIRouter

router = APIRouter()

# Define some example data
test_data = {
    "server1": {
        "group1": {
            "metadata": {
                "registered": "2022-01-01",
                "processed": True
            },
            "members": [
                {"name": "Alice", "roles": "admin,editor"},
                {"name": "Bob", "roles": "editor"},
                {"name": "Charlie", "roles": "viewer"}
            ]
        },
        "group2": {
            "metadata": {
                "registered": "2022-01-02",
                "processed": False
            }
        }
    },
    "server2": {
        "group1": {
            "metadata": {
                "registered": "2022-01-03",
                "processed": True
            },
            "members": [
                {"name": "Frank", "roles": "viewer"}
            ]
        }
    }
}


@router.get("/server/{server_name}", description="Get server groups")
async def get_server(server_name: str):
    if server_name not in test_data:
        return {"error": "Server not found"}

    groups = []
    for group in test_data[server_name]:
        groups.append(group)

    return {"server_name": server_name, "groups": groups}

@router.get("/group/{server_name}/{group_name}", description="Get server group metadata")
async def get_group(server_name: str, group_name: str):
    if server_name not in test_data or group_name not in test_data[server_name]:
        return {"error": "Server or group not found"}

    group = test_data[server_name][group_name]
    metadata = {"registered": group["metadata"]["registered"], "processed": group["metadata"]["processed"]}

    if not group["metadata"]["processed"]:
        return {"server_name": server_name, "group_name": group_name, "metadata": metadata}

    members = group["members"]
    for member in members:
        member["roles"] = member["roles"].split(",")

    return {"server_name": server_name, "group_name": group_name, "metadata": metadata, "members": members}

@router.get("/servers/{server_name}/members", description="Get all members of a server")
async def get_all_members(server_name: str):
    if server_name not in test_data:
        return {"error": "Server not found"}

    members = []
    for group_name, group in test_data[server_name].items():
        if group["metadata"]["processed"]:
            for member in group["members"]:
                member["roles"] = member["roles"].split(",")
                members.append(member)

    return {"server_name": server_name, "members": members}