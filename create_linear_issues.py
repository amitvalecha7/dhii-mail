import json
import os
import sys
from typing import Dict, Any, List

import requests

LINEAR_API_URL = "https://api.linear.app/graphql"


def graphql_request(api_key: str, query: str, variables: Dict[str, Any] = None) -> Dict[str, Any]:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    resp = requests.post(
        LINEAR_API_URL,
        headers=headers,
        json={"query": query, "variables": variables or {}},
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    if "errors" in data:
        raise RuntimeError(f"GraphQL errors: {data['errors']}")
    return data["data"]


def get_team_id(api_key: str, team_name: str) -> str:
    query = """
    query {
      teams(first: 50) {
        nodes {
          id
          name
        }
      }
    }
    """
    data = graphql_request(api_key, query)
    for team in data["teams"]["nodes"]:
        if team["name"] == team_name:
            return team["id"]
    raise RuntimeError(f"Team '{team_name}' not found")


def get_project_id(api_key: str, project_name: str) -> str:
    query = """
    query {
      projects(first: 100) {
        nodes {
          id
          name
        }
      }
    }
    """
    data = graphql_request(api_key, query)
    for proj in data["projects"]["nodes"]:
        if proj["name"] == project_name:
            return proj["id"]
    raise RuntimeError(f"Project '{project_name}' not found")


def create_issue(api_key: str, team_id: str, project_id: str, title: str, description: str, parent_id: str = None) -> str:
    mutation = """
    mutation IssueCreate($input: IssueCreateInput!) {
      issueCreate(input: $input) {
        success
        issue {
          id
          identifier
          title
        }
      }
    }
    """
    input_data: Dict[str, Any] = {
        "teamId": team_id,
        "title": title,
        "description": description,
        "projectId": project_id,
    }
    if parent_id:
        input_data["parentId"] = parent_id

    data = graphql_request(api_key, mutation, {"input": input_data})
    issue = data["issueCreate"]["issue"]
    print(f"Created issue {issue['identifier']}: {issue['title']}")
    return issue["id"]


def main():
    api_key = os.getenv("LINEAR_API_KEY")
    if not api_key:
        print("ERROR: Please set LINEAR_API_KEY environment variable.", file=sys.stderr)
        sys.exit(1)

    if len(sys.argv) < 2:
        print("Usage: python create_linear_issues.py issues_to_create.json", file=sys.stderr)
        sys.exit(1)

    json_path = sys.argv[1]
    with open(json_path, "r", encoding="utf-8") as f:
        issues: List[Dict[str, Any]] = json.load(f)

    # We assume all issues share the same team/project names
    sample = issues[0]
    team_name = sample["team"]
    project_name = sample["project"]

    print(f"Resolving team '{team_name}' and project '{project_name}'...")
    team_id = get_team_id(api_key, team_name)
    project_id = get_project_id(api_key, project_name)
    print(f"Team ID: {team_id}")
    print(f"Project ID: {project_id}")

    # First pass: create all parent (epic) issues (parent == null)
    title_to_id: Dict[str, str] = {}
    print("\nCreating parent (epic) issues...")
    for issue in issues:
        if issue.get("parent") is None:
            iid = create_issue(
                api_key=api_key,
                team_id=team_id,
                project_id=project_id,
                title=issue["title"],
                description=issue.get("description", ""),
            )
            title_to_id[issue["title"]] = iid

    # Second pass: create child issues with parentId
    print("\nCreating child (design/spec) issues...")
    for issue in issues:
        parent_title = issue.get("parent")
        if parent_title:
            parent_id = title_to_id.get(parent_title)
            if not parent_id:
                print(f"WARNING: Parent title '{parent_title}' not found for issue '{issue['title']}', skipping.", file=sys.stderr)
                continue
            iid = create_issue(
                api_key=api_key,
                team_id=team_id,
                project_id=project_id,
                title=issue["title"],
                description=issue.get("description", ""),
                parent_id=parent_id,
            )
            title_to_id[issue["title"]] = iid

    print("\nDone. Created/linked remaining issues.")


if __name__ == "__main__":
    main()
