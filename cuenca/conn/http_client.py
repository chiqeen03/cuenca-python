import os
from typing import Any, Dict, Optional, Tuple

from requests import Response, Session

from ..version import API_VERSION, CLIENT_VERSION

API_URL = 'https://api.cuenca.com'
SANDBOX_URL = 'https://sandbox.cuenca.com'


class HttpClient:

    base_url: str
    auth: Tuple[str, str]
    webhook_secret: Optional[str]
    session: Session

    def __init__(self):
        self.session = Session()
        self.session.headers.update(
            {
                'X-Cuenca-Api-Version': API_VERSION,
                'User-Agent': f'cuenca-python/{CLIENT_VERSION}',
            }
        )
        self.base_url = API_URL
        api_key = os.getenv('CUENCA_API_KEY', '')
        api_secret = os.getenv('CUENCA_API_SECRET', '')
        self.webhook_secret = os.getenv('CUENCA_WEBHOOK_SECRET')
        self.auth = (api_key, api_secret)

    def configure(
        self,
        api_key: str,
        api_secret: str,
        webhook_secret: Optional[str] = None,
        sandbox: Optional[bool] = None,
    ):
        """
        This allows us to instantiate the http client when importing the
        client library and configure it later. It's also useful when rolling
        the api key
        """
        self.auth = (api_key, api_secret)
        self.webhook_secret = webhook_secret or self.webhook_secret
        if sandbox is not None:
            if sandbox:
                self.base_url = SANDBOX_URL
            else:
                self.base_url = API_URL

    def get(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        return self.request('get', endpoint, params=params)

    def post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        return self.request('post', endpoint, data=data)

    def delete(
        self, endpoint: str, data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        return self.request('delete', endpoint, data=data)

    def request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        resp = self.session.request(
            method=method,
            url=self.base_url + endpoint,
            auth=self.auth,
            json=data,
            params=params,
            **kwargs,
        )
        self._check_response(resp)
        return resp.json()

    def _check_response(self, response: Response):
        if response.ok:
            return
        response.raise_for_status()
