import asyncio
import time

import pytest
from typing import List, Coroutine

from httpx import Response
from fastapi import status

from api_connector.connector import AsyncInternalAPIConnector
from api_connector.utils import RequestTypeEnum, ProtocolTypeEnum


@pytest.fixture(scope='session')
def api_connector():
    return AsyncInternalAPIConnector(
        host='postman-echo.com',
        protocol=ProtocolTypeEnum.HTTP
    )


async def gather_metrics(func, data: List[Coroutine]):
    """Gather metrics for bunch"""
    start_time = time.time()
    result: List[Response] = await func(requests=data)
    end_time = time.time() - start_time
    metrics = {
        'eval_time': end_time,
        'errors': 0,
        'single_eval_time': 0
    }
    for response in result:
        metrics[response.url.path] = {
            'status_code': response.status_code,
            'eval_time': response.elapsed.total_seconds()
        }
        metrics['single_eval_time'] = (
                metrics['single_eval_time'] +
                response.elapsed.total_seconds()
        )
        if response.status_code != status.HTTP_200_OK:
            metrics['errors'] = metrics['errors'] + 1
    return metrics, result


def generate_get(api_connector, num: int = 1) -> List[Coroutine]:
    return [
        api_connector.get(
            path='/get',
            params={f'test{x}': x},
        ) for x in range(0, num)
    ]


def generate_post(api_connector, num: int = 1) -> List[Coroutine]:
    return [
        api_connector.post(
            path='/post',
            params={f'test{x}': x},
            json={f'test{x}': x}
        ) for x in range(0, num)
    ]


def generate_put(api_connector, num: int = 1) -> List[Coroutine]:
    return [
        api_connector.put(
            path='/put',
            params={f'test{x}': x},
            json={f'test{x}': x}
        )
        for x in range(0, num)
    ]


def generate_delete(api_connector, num: int = 1) -> List[Coroutine]:
    return [
        api_connector.delete(
            path='/delete',
            params={f'test{x}': x},
        ) for x in range(0, num)
    ]


@pytest.mark.asyncio
async def test_bunch(api_connector):
    response_group = await api_connector.bunch(
        requests=generate_get(api_connector, 3)
        + generate_post(api_connector, 3)
        + generate_put(api_connector, 3)
        + generate_delete(api_connector, 3)
    )
    assert len(response_group) == 12


@pytest.mark.asyncio
async def test_bunch_order(api_connector):
    response_group = await api_connector.bunch(
        requests=generate_get(api_connector, 1)
        + generate_post(api_connector, 1)
        + generate_put(api_connector, 1)
        + generate_delete(api_connector, 1)
        + generate_get(api_connector, 1)
    )
    assert response_group[0].request.method == RequestTypeEnum.GET
    assert response_group[1].request.method == RequestTypeEnum.POST
    assert response_group[2].request.method == RequestTypeEnum.PUT
    assert response_group[3].request.method == RequestTypeEnum.DELETE
    assert response_group[4].request.method == RequestTypeEnum.GET


@pytest.mark.asyncio
async def test_bunch_with_metrics(api_connector):
    response_group_metrics, _ = await gather_metrics(
        api_connector.bunch,
        generate_get(api_connector, 10)
    )

    # check errors
    assert not response_group_metrics['errors']

    # check total eval time faster than total requests time
    assert response_group_metrics['eval_time'] \
           < response_group_metrics['single_eval_time']

    # check single requests starting from 3
    single_request_time = 0
    for request in generate_get(api_connector, 3):
        response = await request
        single_request_time = (
            single_request_time +
            response.elapsed.total_seconds()
        )

    assert response_group_metrics['eval_time'] < single_request_time

    # check single requests in simple asyncio gather
    # check speedup with AsyncClient vs simple gather
    single_in_bunch_request_time = 0
    request_tasks = []
    for request in generate_get(api_connector, 10):
        request_tasks.append(asyncio.ensure_future(request))
    responses = await asyncio.gather(*request_tasks)
    for response in responses:
        single_in_bunch_request_time = (
            single_in_bunch_request_time +
            response.elapsed.total_seconds()
        )

    assert response_group_metrics['eval_time'] < single_in_bunch_request_time


@pytest.mark.asyncio
async def test_get(api_connector):
    response = await api_connector.get(path='/get', params={'x': 1})
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_with_string_params(api_connector):
    response = await api_connector.get(path='/get', params='z=1&x=2')
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_post(api_connector):
    response = await api_connector.post(path='/post', params={'x': 1})
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_post_with_string_params(api_connector):
    response = await api_connector.post(path='/post', params='z=1&x=2')
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete(api_connector):
    response = await api_connector.delete(path='/delete', params={'x': 1})
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_with_string_params(api_connector):
    response = await api_connector.delete(path='/delete', params='z=1&x=2')
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_put(api_connector):
    response = await api_connector.put(path='/put', params={'x': 1})
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_put_with_string_params(api_connector):
    response = await api_connector.put(path='/put', params='z=1&x=2')
    assert response.status_code == 200

# TODO add tests for file
