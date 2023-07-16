from typing import Any, Dict, List, Optional

import requests
from fastapi import APIRouter

router: APIRouter = APIRouter()

# get postgrest url from env variable

# get all groups for a server
# get all groups for a server/database
# get all members for a server/database group
# get all members for a server with databases and groups


@router.get("/jobs/", description="Get jobs", response_model=List[Dict[str, Any]])
def get_jobs(
    status: Optional[int] = None,
    server: Optional[str] = None,
    database: Optional[str] = None,
    job_type: Optional[str] = None,
):
    url = "http://your_postgrest_api_url/job"
    params = {}
    if status is not None:
        params["current_status"] = str(status)
    if server is not None:
        params["server"] = server
    if database is not None:
        params["database"] = database
    if job_type is not None:
        params["job_type"] = job_type
    response = requests.get(url, params=params, timeout=30)
    results = response.json()
    return results


@router.get("/servers", description="Get servers", response_model=List[Dict[str, str]])
async def get_server_list() -> List[Dict[str, str]]:
    servers: List[Dict[str, str]] = []
    for server_name, values in test_data.items():
        servers.append(
            {"server_name": server_name, "connection": values["metadata"]["connection"]}
        )

    return servers


@router.get(
    "/server/{server_name}",
    description="Get server groups",
    response_model=Dict[str, Any],
)
async def get_server(server_name: str) -> Dict[str, Any]:
    if server_name not in test_data:
        return {"error": "Server not found"}

    groups: List[str] = []
    for group in test_data[server_name]["groups"]:
        groups.append(group)

    return {"server_name": server_name, "groups": groups}


@router.get(
    "/group/{server_name}/{group_name}",
    description="Get server group metadata",
    response_model=Dict[str, Any],
)
async def get_group(server_name: str, group_name: str) -> Dict[str, Any]:
    if (
        server_name not in test_data
        or group_name not in test_data[server_name]["groups"]
    ):
        return {"error": "Server or group not found"}

    group: Dict[str, Any] = test_data[server_name]["groups"][group_name]
    metadata: Dict[str, Any] = {
        "registered": group["metadata"]["registered"],
        "processed": group["metadata"]["processed"],
        "roles": group["metadata"]["roles"],
    }

    if not group["metadata"]["processed"]:
        members = []
    else:
        members: List[Dict[str, Any]] = group["members"]

    return {
        "server_name": server_name,
        "group_name": group_name,
        "metadata": metadata,
        "members": members,
    }


@router.get(
    "/servers/{server_name}/members",
    description="Get all members of a server",
    response_model=Dict[str, Any],
)
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
