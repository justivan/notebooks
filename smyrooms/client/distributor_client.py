from typing import Any

import requests

from smyrooms.config import Config


class APIClient:
    def __init__(
        self,
        base_url: str,
        organization_id: str,
        product_id: str,
    ):
        self.base_url = base_url.rstrip("/")
        self.organization_id = organization_id
        self.product_id = product_id
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Accept": "application/json",
                "Authorization": Config.DISTRIBUTOR_APIKEY,
            }
        )

    def _request(self, method: str, endpoint: str, **kwargs) -> Any:
        """Make an HTTP request to the API."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = self.session.request(method, url, **kwargs)
        response.raise_for_status()

        # Handle empty responses (like DELETE operations)
        if response.status_code == 204 or not response.content:
            return {"status": "deleted", "status_code": response.status_code}

        return response.json()


class LevelCloseAPI:
    def __init__(self, client: APIClient):
        self.client = client

    def get_level_closes(self) -> dict[str, Any]:
        """Returns the whole level closes (data and extra info)."""
        endpoint = (
            f"api/organizations/{self.client.organization_id}/"
            f"agencies/products/{self.client.product_id}/level_closes"
        )
        return self.client._request("GET", endpoint)

    def get_level_closes_by_id(self, level_id: str) -> dict[str, Any]:
        """Returns the specific level close referenced by its ID."""
        endpoint = (
            f"api/organizations/{self.client.organization_id}/"
            f"agencies/products/{self.client.product_id}/level_closes/{level_id}"
        )
        return self.client._request("GET", endpoint)

    def get_agency_level_closes(self, agency_id: str) -> dict[str, Any]:
        """Returns the level closes that apply to a concrete agency."""
        endpoint = (
            f"api/organizations/{self.client.organization_id}/"
            f"agencies/{agency_id}/products/{self.client.product_id}/level_closes"
        )
        return self.client._request("GET", endpoint)

    def create_or_update_level_close(
        self, level_id: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Create/update a constant level commission.Use 'new' as level_id to create."""
        endpoint = (
            f"api/organizations/{self.client.organization_id}/"
            f"agencies/products/{self.client.product_id}/level_closes/{level_id}"
        )
        return self.client._request("PUT", endpoint, json=data)


class ProviderFilterAPI:
    def __init__(self, client: APIClient):
        self.client = client

    def get_providers_filter(self, agency_id: str) -> dict[str, Any]:
        """Returns the providers filter applied for an agency."""
        endpoint = (
            f"api/organizations/{self.client.organization_id}/"
            f"agencies/{agency_id}/products/{self.client.product_id}/providers_filter"
        )
        return self.client._request("GET", endpoint)


class ClientGroupAPI:
    def __init__(self, client: APIClient):
        self.client = client

    def get_client_groups(self) -> dict[str, Any]:
        """Returns the list of all client groups."""
        endpoint = (
            f"organizations/{self.client.organization_id}/"
            f"agencies/products/{self.client.product_id}/getClientGroupList"
        )
        return self.client._request("GET", endpoint)

    def get_client_group_by_id(self, group_id: str) -> dict[str, Any]:
        """Returns a single client group by its ID."""
        endpoint = (
            f"organizations/{self.client.organization_id}/"
            f"agencies/products/{self.client.product_id}/getClientGroup/{group_id}"
        )
        return self.client._request("GET", endpoint)

    def get_client_group_by_ids(self, group_ids: list[str]) -> dict[str, Any]:
        """Returns client groups for a list of IDs."""
        endpoint = (
            f"organizations/{self.client.organization_id}/"
            f"agencies/products/{self.client.product_id}/getClientGroupByIdList"
        )
        return self.client._request("POST", endpoint, json=group_ids)

    def create_client_groups(
        self, client_groups_data: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Create multiple client groups at the same time."""
        endpoint = (
            f"organizations/{self.client.organization_id}/"
            f"agencies/products/{self.client.product_id}/newClientGroupList"
        )
        return self.client._request("POST", endpoint, json=client_groups_data)

    def update_client_group_list(
        self, client_groups_data: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Update multiple client groups at the same time."""
        endpoint = (
            f"organizations/{self.client.organization_id}/"
            f"agencies/products/{self.client.product_id}/updateClientGroupList"
        )
        return self.client._request("PUT", endpoint, json=client_groups_data)

    def delete_all_client_groups(self) -> dict[str, Any]:
        """Delete all client groups."""
        endpoint = (
            f"organizations/{self.client.organization_id}/"
            f"agencies/products/{self.client.product_id}/deleteAllClientGroups"
        )
        return self.client._request("DELETE", endpoint)

    def delete_client_group(self, group_id: str) -> dict[str, Any]:
        """Delete a single client group by its ID."""
        endpoint = (
            f"organizations/{self.client.organization_id}/"
            f"agencies/products/{self.client.product_id}/deleteClientGroup/{group_id}"
        )
        return self.client._request("DELETE", endpoint)


class DistributorRulesClient:
    def __init__(
        self,
        organization_id: str,
        product_id: str,
        environment: str = "qa",
    ):
        base_url = f"http://distributor.rules.api.{environment}.logitravel.internal"
        self._client = APIClient(base_url, organization_id, product_id)

        self.level_closes = LevelCloseAPI(self._client)
        self.provider_filters = ProviderFilterAPI(self._client)

    @staticmethod
    def _get_nested_value(obj: dict, keys: list[str], default: Any = None) -> Any:
        """Get value from nested dictionary."""
        try:
            for key in keys:
                if not isinstance(obj, dict):
                    return default
                obj = obj.get(key, default)
            return obj
        except Exception:
            return default

    def where(
        self,
        rules: list[dict],
        query: dict[str, Any],
    ) -> list[dict]:
        """Filter rules using a simple and intuitive query syntax.

        Query format:
        {
            "field": value,  # Simple equality
            "nested": {      # Nested dictionary matching
                "field": value
            },
            "$or": [        # Logical OR of conditions
                {"field1": value1},
                {"field2": value2}
            ],
            "$and": [       # Logical AND of conditions
                {"field1": value1},
                {"field2": value2}
            ],
            "list_field": {  # List operations
                "$any": value,    # Any item equals value
                "$all": value,    # All items equal value
                "$in": [values],  # Field value in list
                "$nin": [values], # Field value not in list
                "$contains": value, # List contains value
                "$size": 2,      # List has exact size
                "$empty": true   # List is empty
            }
        }

        Examples:
            # Simple field equality
            where(rules, {"tag": 1})

            # Nested field matching
            where(rules, {"lvl": {"cli": {"t": 1}}})

            # List operations
            where(rules, {
                "lvl": {
                    "prv": {
                        "l": {"$contains": "EXPR"}
                    }
                }
            })

            # Complex conditions
            where(rules, {
                "$or": [
                    {"id": {"$in": ["1234", "5678"]}},
                    {
                        "lvl": {
                            "prv": {
                                "t": 1,
                                "l": {"$contains": "EXPR"}
                            }
                        }
                    }
                ]
            })

        Returns:
            List of rules matching all conditions
        """
        ops = {
            # Value comparisons
            "$eq": lambda v, t: v == t,
            "$ne": lambda v, t: v != t,
            "$gt": lambda v, t: v > t if v is not None else False,
            "$gte": lambda v, t: v >= t if v is not None else False,
            "$lt": lambda v, t: v < t if v is not None else False,
            "$lte": lambda v, t: v <= t if v is not None else False,
            "$in": lambda v, t: v in t if isinstance(t, (list, tuple)) else False,
            "$nin": lambda v, t: v not in t if isinstance(t, (list, tuple)) else False,
            # List operations
            "$contains": lambda v, t: t in v if isinstance(v, (list, tuple)) else False,
            "$containsAny": (
                lambda v, t: any(x in v for x in t)
                if isinstance(v, (list, tuple)) and isinstance(t, (list, tuple))
                else False
            ),
            "$containsAll": (
                lambda v, t: all(x in v for x in t)
                if isinstance(v, (list, tuple)) and isinstance(t, (list, tuple))
                else False
            ),
            "$ncontains": (
                lambda v, t: t not in v if isinstance(v, (list, tuple)) else True
            ),
            "$any": (
                lambda v, t: any(x == t for x in v)
                if isinstance(v, (list, tuple))
                else False
            ),
            "$all": (
                lambda v, t: all(x == t for x in v)
                if isinstance(v, (list, tuple))
                else False
            ),
            "$size": (
                lambda v, t: len(v) == t if isinstance(v, (list, tuple)) else False
            ),
            "$empty": lambda v, t: (
                (len(v) == 0) == t if isinstance(v, (list, tuple)) else t
            ),
            # Type checks
            "$exists": lambda v, t: (v is not None) == t,
            "$type": lambda v, t: isinstance(v, t),
        }

        def evaluate_query(value: Any, condition: Any) -> bool:
            """Evaluate a query condition against a value."""
            # Simple equality for non-dict conditions
            if not isinstance(condition, dict):
                return value == condition

            # Handle logical operators first
            if "$or" in condition:
                return any(evaluate_query(value, c) for c in condition["$or"])
            if "$and" in condition:
                return all(evaluate_query(value, c) for c in condition["$and"])

            # Handle standard operators
            for op, target in condition.items():
                if op in ops:
                    return ops[op](value, target)

            # Handle nested dictionary matching
            if isinstance(value, dict):
                return all(
                    evaluate_query(value.get(k), v) for k, v in condition.items()
                )

            return False

        def matches_query(rule: dict, query: dict, path: list[str] = None) -> bool:
            """Check if rule matches query using operator dictionary."""
            path = path or []

            # Handle top-level logical operators
            if "$or" in query:
                return any(matches_query(rule, q, path) for q in query["$or"])
            if "$and" in query:
                return all(matches_query(rule, q, path) for q in query["$and"])

            # Handle field conditions
            for key, condition in query.items():
                if key.startswith("$"):
                    continue
                value = self._get_nested_value(rule, path + [key])
                if not evaluate_query(value, condition):
                    return False
            return True

        return [rule for rule in rules if matches_query(rule, query)]

    def filter_rules(
        self,
        rules: list[dict],
        filters: dict[str, Any] | None = None,
        **kwargs,
    ) -> list[dict]:
        """Legacy filter method, preserved for backward compatibility.
        Prefer using where() for new code."""
        # Convert dot notation and kwargs to nested dictionary
        query = {}

        # Handle kwargs
        for key, value in kwargs.items():
            current = query
            parts = key.split(".")
            for part in parts[:-1]:
                current = current.setdefault(part, {})
            current[parts[-1]] = value

        # Handle filters
        if filters:
            for path, condition in filters.items():
                current = query
                parts = path.split(".")
                for part in parts[:-1]:
                    current = current.setdefault(part, {})

                if isinstance(condition, dict) and "op" in condition:
                    op = condition["op"]
                    value = condition["value"]
                    if op == "contains":
                        current[parts[-1]] = {"$contains": value}
                    elif op == "in":
                        current[parts[-1]] = {"$in": value}
                    else:
                        current[parts[-1]] = value
                else:
                    current[parts[-1]] = condition

        return self.where(rules, query)


class DistributorMastersClient:
    def __init__(
        self,
        organization_id: str,
        product_id: str,
        environment: str = "qa",
    ):
        base_url = f"http://distributor.masters.api.{environment}.logitravel.internal"
        self._client = APIClient(base_url, organization_id, product_id)

        self.client_groups = ClientGroupAPI(self._client)
