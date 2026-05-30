import asyncio
import json
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError
from urllib.request import Request, urlopen


class SendPulseCRMError(RuntimeError):
    pass


@dataclass(frozen=True)
class SendPulseCRMClient:
    api_key: str
    base_url: str = "https://api.sendpulse.com/crm/v1"
    timeout_seconds: int = 20

    async def request(self, method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        return await asyncio.to_thread(self._request_sync, method, path, payload)

    def _request_sync(self, method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        body = json.dumps(payload or {}, ensure_ascii=False).encode("utf-8") if payload is not None else None
        request = Request(
            f"{self.base_url}{path}",
            data=body,
            method=method,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
        )
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                raw = response.read().decode("utf-8")
        except HTTPError as exc:
            error_body = exc.read().decode("utf-8", errors="replace")
            raise SendPulseCRMError(f"SendPulse CRM {method} {path} failed: {exc.code} {error_body}") from exc
        if not raw:
            return {}
        return json.loads(raw)

    async def get_users(self) -> list[dict[str, Any]]:
        response = await self.request("GET", "/users")
        return _data_list(response)

    async def get_pipelines(self) -> list[dict[str, Any]]:
        response = await self.request("GET", "/pipelines")
        return _data_list(response)

    async def find_contact_by_phone(self, phone: str) -> dict[str, Any] | None:
        response = await self.request("POST", "/contacts/get-list", {"phone": phone, "limit": 10, "offset": 0})
        contacts = response.get("data", {}).get("list") or response.get("data", [])
        return contacts[0] if contacts else None

    async def create_contact(
        self,
        *,
        responsible_id: int,
        first_name: str,
        last_name: str | None,
        external_contact_id: str,
    ) -> dict[str, Any]:
        response = await self.request(
            "POST",
            "/contacts/create",
            {
                "responsibleId": responsible_id,
                "firstName": first_name,
                "lastName": last_name or "",
                "externalContactId": external_contact_id,
            },
        )
        return response["data"]

    async def add_phone(self, contact_id: int, phone: str) -> None:
        await self.request("POST", f"/contacts/{contact_id}/phones", {"phone": phone})

    async def add_contact_note(self, contact_id: int, message: str) -> None:
        await self.request("POST", f"/contacts/{contact_id}/comments", {"message": message[:65535]})

    async def create_deal(
        self,
        *,
        pipeline_id: int,
        step_id: int,
        responsible_id: int,
        contact_id: int,
        name: str,
        price: float,
        currency: str,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "pipelineId": pipeline_id,
            "stepId": step_id,
            "responsibleId": responsible_id,
            "name": name[:255],
            "price": price,
            "currency": currency,
            "contact": [contact_id],
        }
        response = await self.request("POST", "/deals", payload)
        return response["data"]

    async def add_deal_note(self, deal_id: int, message: str) -> None:
        await self.request("POST", f"/deals/{deal_id}/comments", {"message": message[:65535]})


def _data_list(response: dict[str, Any]) -> list[dict[str, Any]]:
    data = response.get("data", [])
    return data if isinstance(data, list) else [data]
