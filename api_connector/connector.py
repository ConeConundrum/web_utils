import io
import asyncio
from logging import getLogger
from typing import Optional, Union, Dict, List, Any, Coroutine

import httpx
import aioify
from httpx import AsyncClient, Response
from httpx._models import URL  # noqa
from fastapi import status, HTTPException
from starlette.responses import StreamingResponse

from api_connector.utils import ProtocolTypeEnum

logger = getLogger()


class AsyncInternalAPIConnector:
    """
    Asynchronous API wrapper for requests between services based on httpx
    """

    def __init__(
            self, *,
            host: str,
            protocol: ProtocolTypeEnum = ProtocolTypeEnum.HTTP,
            port: Optional[int] = None,
            http2: bool = True,
            request_timeout: int = 30
    ):
        self.request_timeout = request_timeout
        self.protocol = protocol
        self.http2 = http2
        self.host = host
        self.port = port
        self._url = self._form_url()

        self.__post = aioify.aioify(httpx.post)
        self.__get = aioify.aioify(httpx.get)
        self.__put = aioify.aioify(httpx.put)
        self.__delete = aioify.aioify(httpx.delete)

    def _form_url(self) -> str:
        """Url forming"""
        return f'{self.protocol}://{self.host}:{self.port}' if self.port else f'{self.protocol}://{self.host}'  # noqa

    async def post(
            self,
            path: str,
            *,
            files: Optional[Dict[str, Union[bytes, str]]] = None,
            json: Union[dict, list, None] = None,
            params: Union[bytes, str, dict, None] = None,
            cookies: Optional[dict] = None,
            auth: Union[dict, tuple, None] = None,
            headers: Optional[dict] = None,
            data: Optional[dict] = None,
    ) -> Response:
        """Http post method"""
        return await self.__post(
            self._url + path,
            params=params,
            json=json,
            cookies=cookies,
            auth=auth,
            headers=headers,
            files=files,
            data=data,
            timeout=self.request_timeout
        )

    async def get(
            self,
            path: str,
            *,
            params: Union[bytes, str, dict, None] = None,
            cookies: Optional[dict] = None,
            auth: Union[dict, tuple, None] = None,
            headers: Optional[dict] = None,
    ) -> Response:
        """Http get method"""
        return await self.__get(
            url=URL(self._url + path),
            params=params,
            cookies=cookies,
            auth=auth,
            headers=headers,
            timeout=self.request_timeout
        )

    async def put(
            self,
            path: str = None,
            *,
            json: Union[dict, list, None] = None,
            params: Union[bytes, str, dict, None] = None,
            cookies: Optional[dict] = None,
            auth: Union[dict, tuple, None] = None,
            headers: Optional[dict] = None,
            data: Optional[dict] = None,
    ) -> Response:
        """Http put method"""

        return await self.__put(
            url=URL(self._url + path),
            json=json,
            params=params,
            cookies=cookies,
            auth=auth,
            headers=headers,
            data=data,
            timeout=self.request_timeout
        )

    async def delete(
            self,
            path: str = None,
            *,
            params: Union[bytes, str, dict, None] = None,
            cookies: Optional[dict] = None,
            auth: Union[dict, tuple, None] = None,
            headers: Optional[dict] = None,
    ) -> Response:
        """Http delete method"""
        return await self.__delete(
            self._url + path,
            params=params,
            cookies=cookies,
            auth=auth,
            headers=headers,
            timeout=self.request_timeout
        )

    @staticmethod
    async def bunch(
            *,
            requests: List[Coroutine]
    ) -> List[Response]:
        """
        Method for multiple async request
        Handles get, post, put, delete, file_get coroutines

        Response is List[Response], which elements
        in requests list elements order

        Using:
            connect = AsyncInternalAPIConnector
            responses = await connect.bunch(
                connect.post("/places/company", json=jsonable_encoder(company_data))
                connect.get(f"/places/company/{company_id}/list")
                connect.put("/places/company", json=company_address.dict())
                ...
            )
            create_place, get_place, put_place = *responses
        """
        async with AsyncClient() as _:
            # get all task
            request_tasks = []
            for request in requests:
                request_tasks.append(asyncio.ensure_future(request))
            responses: Union[BaseException, Any] = await asyncio.gather(*request_tasks)
        return responses

    async def get_file(
            self,
            path: str = None,
            *,
            params: Union[bytes, str, dict, None] = None,
            cookies: Optional[dict] = None,
            auth: Union[dict, tuple, None] = None,
            headers: Optional[dict] = None,
    ) -> StreamingResponse:
        """Http get method for file"""
        response = await self.get(
            path=path,
            params=params,
            cookies=cookies,
            auth=auth,
            headers=headers
        )
        if not response.content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Bad file data', headers=headers
            )

        if ("content-disposition" not in response.headers) or \
                ("filename" not in response.headers['content-disposition']):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='No file in response', headers=headers
            )

        return self._stream_file(response=response, headers=response.headers)

    @staticmethod
    def _stream_file(
            response: Response,
            headers: Optional[dict]
    ) -> StreamingResponse:
        """
        Compose bytes data to response as stream
        """
        return StreamingResponse(
            headers=headers,
            content=io.BytesIO(response.content),
        )
