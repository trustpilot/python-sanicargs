
import pytest
from sanic import response, Sanic

from sanicargs import parse_query_args, fields
from sanic.websocket import WebSocketProtocol
from sanic.exceptions import InvalidUsage
from sanic import request

import datetime


@pytest.yield_fixture
def app():
    app = Sanic("test_sanic_app")

    @app.route("/int", methods=['GET'])
    @parse_query_args
    async def test_int(request, test: int):
        return response.json({'test': test})

    @app.route("/str", methods=['GET'])
    @parse_query_args
    async def test_str(request, test: str):
        return response.json({'test': test})

    @app.route("/datetime", methods=['GET'])
    @parse_query_args
    async def test_datetime(request, test: datetime.datetime):
        return response.json({'test': test.isoformat()})

    @app.route("/date", methods=['GET'])
    @parse_query_args
    async def test_date(request, test: datetime.date):
        return response.json({'test': test.isoformat()})

    @app.route("/list", methods=['GET'])
    @parse_query_args
    async def test_list(req, test: fields.List[str] = None):
        return response.json({'test': test})

    @app.route("/all", methods=['GET'])
    @parse_query_args
    async def test_all(
            req: request, 
            a: int,
            b: str,
            c: datetime.datetime,
            d: datetime.date,
            e: fields.List[str] = None):
        return response.json({
            'a': a,
            'b': b,
            'c': c.isoformat(),
            'd': c.isoformat(),
            'e': e
        })

    @app.route("/optional", methods=['GET'])
    @parse_query_args
    async def test_optional(request, test: str = 'helloworld'):
        return response.json({'test': test})

    @app.route("/with/<path_param>/path_params", methods=['GET'])
    @parse_query_args
    async def test_path_params(request, path_param: int, test: str, test_2: int=35):
        return response.json({'path_param': path_param, 'test': test, 'test_2': test_2})

    yield app

@pytest.fixture
def test_cli(loop, app, test_client):
    return loop.run_until_complete(test_client(app, protocol=WebSocketProtocol))


#########
# Tests #
#########


async def test_parse_int_success(test_cli):
    resp = await test_cli.get('/int?test=10')
    assert resp.status == 200
    resp_json = await resp.json()
    assert resp_json == {'test': 10}


async def test_parse_int_fail(test_cli):
    resp = await test_cli.get('/int?test=not an integer')
    assert resp.status == 400


async def test_parse_str_success(test_cli):
    resp = await test_cli.get('/str?test=hello')
    assert resp.status == 200
    resp_json = await resp.json()
    assert resp_json == {'test': 'hello'}


async def test_parse_str_also_works_with_int(test_cli):
    ''' there is no way of knowing if an str is really an integer
    '''
    resp = await test_cli.get('/str?test=400')
    assert resp.status == 200


async def test_parse_datetime_success(test_cli):
    resp = await test_cli.get('/datetime?test=2017-10-10T10:10:10')
    assert resp.status == 200
    resp_json = await resp.json()
    assert resp_json == {'test': '2017-10-10T10:10:10'}


async def test_parse_datetime_fail(test_cli):
    resp = await test_cli.get('/datetime?test=not a datetime')
    assert resp.status == 400


async def test_parse_date_success(test_cli):
    resp = await test_cli.get('/date?test=2017-10-10')
    assert resp.status == 200
    resp_json = await resp.json()
    assert resp_json == {'test': '2017-10-10'}


async def test_parse_date_fail(test_cli):
    resp = await test_cli.get('/date?test=not a datetime')
    assert resp.status == 400
   

async def test_parse_list_success(test_cli):
    resp = await test_cli.get('/list?test=one,two,three')
    assert resp.status == 200
    resp_json = await resp.json()
    assert resp_json == {'test': [
      'one', 'two', 'three'
    ]}


async def test_parse_list_also_works_with_singular(test_cli):
    resp = await test_cli.get('/list?test=not a datetime')
    assert resp.status == 200
    resp_json = await resp.json()
    assert resp_json == {'test': [
      'not a datetime'
    ]}


async def test_all_at_once(test_cli):
    resp = await test_cli.get('/all?a=10&b=test&c=2017-10-10T10:10:10&d=2017-10-10&e=a,b,c,d,e')
    assert resp.status == 200
    resp_json = await resp.json()
    assert resp_json == dict(
      a=10,
      b='test',
      c='2017-10-10T10:10:10',
      d='2017-10-10T10:10:10',
      e=[
        'a', 'b', 'c', 'd', 'e'
      ]
    )


async def test_optional(test_cli):
    resp = await test_cli.get('/optional')
    assert resp.status == 200
    resp_json = await resp.json()
    assert resp_json == {'test': 'helloworld'}


async def test_mandatory(test_cli):
    resp = await test_cli.get('/str')
    assert resp.status == 400


async def test_with_path_params(test_cli):
    resp = await test_cli.get('/with/123/path_params?test=hello')
    assert resp.status == 200
    resp_json = await resp.json()
    assert resp_json == {'path_param': 123, 'test': 'hello', 'test_2': 35}
