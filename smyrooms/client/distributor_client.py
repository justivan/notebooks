from datetime import datetime
from typing import Any, Self

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
        """Returns the level closes that apply to an agency."""
        endpoint = (
            f"api/organizations/{self.client.organization_id}/"
            f"agencies/{agency_id}/products/{self.client.product_id}/level_closes"
        )
        return self.client._request("GET", endpoint)

    def create_or_update_level_close(
        self, level_id: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Create or update a level close. Use 'new' as level_id to create."""
        endpoint = (
            f"api/organizations/{self.client.organization_id}/"
            f"agencies/products/{self.client.product_id}/level_closes/{level_id}"
        )
        return self.client._request("PUT", endpoint, json=data)


class ProviderFilterAPI:
    def __init__(self, client: APIClient):
        self.client = client

    def get_providers_filter(self, agency_id: str) -> dict[str, Any]:
        """Returns blacklisted providers applied for an agency."""
        endpoint = (
            f"api/organizations/{self.client.organization_id}/"
            f"agencies/{agency_id}/products/{self.client.product_id}/providers_filter"
        )
        return self.client._request("GET", endpoint)


class AgencyRulesAPI:
    def __init__(self, client: APIClient):
        self.client = client

    def get_agency_rules(self) -> dict[str, Any]:
        """Returns all rules for agencies."""
        endpoint = (
            f"api/organizations/{self.client.organization_id}/"
            f"agencies/products/{self.client.product_id}/rules"
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


class RuleFilter:
    """
    Interface for filtering rule lists with dot-notation field access.

    Supports method chaining for complex filtering operations. Rules with
    non-existent field paths are excluded from results.

    Example:
        filtered = (
            RuleFilter(rules)
            .where_field_in("tag", 1)
            .where_list_contains_any("cli", 1, credential_ids)
            .exclude_list_contains_any("lvl.prv", 1, provider_codes)
            .to_list()
        )
    """

    def __init__(self, rules: list[dict[str, Any]]) -> None:
        self.rules = rules

    def _get_nested_value(
        self, rule: dict[str, Any], path: str, default: Any = None
    ) -> Any:
        """Get nested dictionary value safely using dot notation."""
        keys = path.split(".")
        obj = rule
        try:
            for key in keys:
                obj = obj[key]
            return obj
        except (KeyError, TypeError):
            return default

    def where_field_in(self, path: str, values: Any) -> Self:
        """Filter where scalar field value is in values."""
        if not isinstance(values, (list, tuple, set)):
            values = [values]

        self.rules = [
            rule for rule in self.rules if self._get_nested_value(rule, path) in values
        ]
        return self

    def where_field_equals(self, path: str, value: Any) -> Self:
        """Filter where scalar field value equals value."""
        self.rules = [
            rule for rule in self.rules if self._get_nested_value(rule, path) == value
        ]
        return self

    def where_list_contains_any(
        self, path: str, type_value: int, values: list[Any]
    ) -> Self:
        """Filter where list field contains any of the values AND type matches."""
        self.rules = [
            rule
            for rule in self.rules
            if (
                self._get_nested_value(rule, f"lvl.{path}.t") == type_value
                and any(
                    value in (self._get_nested_value(rule, f"lvl.{path}.l") or [])
                    for value in values
                )
            )
        ]
        return self

    def exclude_field_in(self, path: str, values: Any) -> Self:
        """Exclude rules where scalar field value is in values."""
        if not isinstance(values, (list, tuple, set)):
            values = [values]

        self.rules = [
            rule
            for rule in self.rules
            if self._get_nested_value(rule, path) not in values
        ]
        return self

    def exclude_field_equals(self, path: str, value: Any) -> Self:
        """Exclude rules where scalar field value equals value."""
        self.rules = [
            rule for rule in self.rules if self._get_nested_value(rule, path) != value
        ]
        return self

    def exclude_list_contains_any(
        self, path: str, type_value: int, values: list[Any]
    ) -> Self:
        """Exclude rules where list field contains any values AND type matches."""
        self.rules = [
            rule
            for rule in self.rules
            if not (
                self._get_nested_value(rule, f"lvl.{path}.t") == type_value
                and any(
                    v in (self._get_nested_value(rule, f"lvl.{path}.l") or [])
                    for v in values
                )
            )
        ]
        return self

    def where_date_range_overlaps(
        self, path: str, start_date: str, end_date: str
    ) -> Self:
        """
        Filter rules where date range overlaps with given range.
        Only includes rules with specific date ranges (t=1), not global rules (t=0).
        """
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError as e:
            raise ValueError("Dates must be in 'YYYY-MM-DD' format") from e

        self.rules = [
            rule
            for rule in self.rules
            if self._date_ranges_overlap(rule, path, start_dt, end_dt)
        ]
        return self

    def _date_ranges_overlap(
        self, rule: dict[str, Any], path: str, start_dt: datetime, end_dt: datetime
    ) -> bool:
        """Check if rule's date range overlaps with given date range."""

        rule_start_str = self._get_nested_value(rule, f"lvl.{path}.from")
        rule_end_str = self._get_nested_value(rule, f"lvl.{path}.to")

        # Only process rules with complete date ranges
        if rule_start_str is None or rule_end_str is None:
            return False

        try:
            rule_start_dt = datetime.strptime(rule_start_str, "%Y-%m-%d")
            rule_end_dt = datetime.strptime(rule_end_str, "%Y-%m-%d")
        except (ValueError, TypeError):
            # Skip rules with invalid date formats or types
            return False

        return start_dt <= rule_end_dt and rule_start_dt <= end_dt

    def exclude_algorithmic_rules(self) -> Self:
        """Exclude rules created by algorithms (blacklist and blocked providers)."""
        algorithmic_descriptions = [
            "Automatic blacklist.",
            "Automatic providers blocked algorithm.",
        ]
        return self.exclude_field_in("description", algorithmic_descriptions)

    def exclude_automatic(self) -> Self:
        """Alias for exclude_algorithmic_rules() - shorter method name."""
        return self.exclude_algorithmic_rules()

    def exclude_obsolete(self) -> Self:
        """Exclude rules where isObsolete is True."""
        return self.exclude_field_equals("isObsolete", True)

    def apply_analysis_defaults(self) -> Self:
        """Apply default exclusions for analysis (algorithmic + obsolete)."""
        return self.exclude_algorithmic_rules().exclude_obsolete()

    def to_dict(self, key_field: str = "id") -> dict[str, dict[str, Any]]:
        """Return the filtered rules as a dictionary keyed by specified field."""
        return {rule[key_field]: rule for rule in self.rules if key_field in rule}

    def to_list(self) -> list[dict[str, Any]]:
        """Return the filtered rules as a list."""
        return self.rules

    def count(self) -> int:
        """Return count of filtered rules."""
        return len(self.rules)


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
        self.agency_rules = AgencyRulesAPI(self._client)


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
