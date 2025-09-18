from typing import Any

import requests
from config import Config


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

    def get_level_close_by_id(self, level_id: str) -> dict[str, Any]:
        """Returns the specific level close referenced by its ID."""
        endpoint = (
            f"api/organizations/{self.client.organization_id}/"
            f"agencies/products/{self.client.product_id}/level_closes/{level_id}"
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
