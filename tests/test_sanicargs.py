import datetime
import inspect
import uuid
from functools import wraps

import pytest
from sanic import Sanic, request, response
from sanic.server.protocols.websocket_protocol import WebSocketProtocol
from sanic_testing import TestManager

from sanicargs import fields, parse_parameters


def has_test_arg(func):
    signature = inspect.signature(func)
    assert signature.parameters["test"]

    @wraps(func)
    async def decorated(request, *args, **kwargs):
        return await func(request, *args, **kwargs)

    return decorated


@pytest.fixture
def app():
    app = Sanic(f"app_{uuid.uuid4().hex}")
    TestManager(app)

    @app.route("/int", methods=["GET"])
    @parse_parameters
    async def test_int(request, test: int):
        return response.json({"test": test})

    @app.route("/str", methods=["GET"])
    @parse_parameters
    async def test_str(request, test: str):
        return response.json({"test": test})

    @app.route("/bool", methods=["GET"])
    @parse_parameters
    async def test_bool(request, test: bool):
        return response.json({"test": test})

    @app.route("/datetime", methods=["GET"])
    @parse_parameters
    async def test_datetime(request, test: datetime.datetime):
        return response.json({"test": test.isoformat()})

    @app.route("/date", methods=["GET"])
    @parse_parameters
    async def test_date(request, test: datetime.date):
        return response.json({"test": test.isoformat()})

    @app.route("/list", methods=["GET"])
    @parse_parameters
    async def test_list(req, test: fields.List[str] = None):
        return response.json({"test": test})

    @app.route("/all", methods=["GET"])
    @parse_parameters
    async def test_all(
        req: request,
        a: int,
        b: str,
        c: datetime.datetime,
        d: datetime.date,
        e: fields.List[str] = None,
    ):
        return response.json(
            {"a": a, "b": b, "c": c.isoformat(), "d": c.isoformat(), "e": e}
        )

    @app.route("/optional", methods=["GET"])
    @parse_parameters
    async def test_optional(request, test: str = "helloworld"):
        return response.json({"test": test})

    @app.route("/with/<path_param>/path_params", methods=["GET"])
    @parse_parameters
    async def test_path_params(request, path_param: int, test: str, test_2: int = 35):
        return response.json({"path_param": path_param, "test": test, "test_2": test_2})

    @app.route("/test_arg", methods=["GET"])
    @has_test_arg
    @parse_parameters
    async def test_args(request, test: int):
        return response.json({"test": test})

    return app


#########
# Tests #
#########


def test_parse_int_success(app):
    __, response = app.test_client.get("/int?test=10")

    assert response.status == 200
    assert response.json == {"test": 10}


def test_parse_int_fail(app):
    __, response = app.test_client.get("/int?test=not an integer")

    assert response.status == 400


def test_parse_bool_true_success(app):
    __, response = app.test_client.get("/bool?test=true")
    assert response.status == 200
    assert response.json == {"test": True}


def test_parse_bool_false_success(app):
    __, response = app.test_client.get("/bool?test=false")
    assert response.status == 200
    assert response.json == {"test": False}


def test_parse_bool_fail(app):
    __, response = app.test_client.get("/bool?test=not an bool")
    assert response.status == 400


def test_parse_str_success(app):
    __, response = app.test_client.get("/str?test=hello")
    assert response.status == 200
    assert response.json == {"test": "hello"}


def test_parse_str_also_works_with_int(app):
    """there is no way of knowing if an str is really an integer"""
    __, response = app.test_client.get("/str?test=400")
    assert response.status == 200


def test_parse_datetime_success(app):
    __, response = app.test_client.get("/datetime?test=2017-10-10T10:10:10")
    assert response.status == 200
    assert response.json == {"test": "2017-10-10T10:10:10"}


def test_parse_encoded_datetime_success(app):
    __, response = app.test_client.get("/datetime?test=2020-03-01T23%3A00%3A00")
    assert response.status == 200
    assert response.json == {"test": "2020-03-01T23:00:00"}


def test_parse_datetime_with_timezone_success(app):
    __, response = app.test_client.get("/datetime?test=2020-03-01T23%3A00%3A00.000Z")
    assert response.status == 200
    assert response.json == {"test": "2020-03-01T23:00:00"}


def test_parse_datetime_fail(app):
    __, response = app.test_client.get("/datetime?test=not a datetime")
    assert response.status == 400


def test_parse_date_success(app):
    __, response = app.test_client.get("/date?test=2017-10-19")
    assert response.status == 200
    assert response.json == {"test": "2017-10-19"}


def test_parse_date_fail(app):
    __, response = app.test_client.get("/date?test=not a datetime")
    assert response.status == 400


def test_parse_list_success(app):
    __, response = app.test_client.get("/list?test=one,two,three")
    assert response.status == 200
    assert response.json == {"test": ["one", "two", "three"]}


def test_parse_list_also_works_with_singular(app):
    __, response = app.test_client.get("/list?test=not a datetime")
    assert response.status == 200
    assert response.json == {"test": ["not a datetime"]}


def test_all_at_once(app):
    __, response = app.test_client.get(
        "/all?a=10&b=test&c=2017-10-10T10:10:10&d=2017-10-10&e=a,b,c,d,e"
    )
    assert response.status == 200
    assert response.json == dict(
        a=10,
        b="test",
        c="2017-10-10T10:10:10",
        d="2017-10-10T10:10:10",
        e=["a", "b", "c", "d", "e"],
    )


def test_optional(app):
    __, response = app.test_client.get("/optional")
    assert response.status == 200
    assert response.json == {"test": "helloworld"}


def test_mandatory(app):
    __, response = app.test_client.get("/str")
    assert response.status == 400


def test_with_path_params(app):
    __, response = app.test_client.get("/with/123/path_params?test=hello")
    assert response.status == 200
    assert response.json == {"path_param": 123, "test": "hello", "test_2": 35}


def test_args_success(app):
    __, response = app.test_client.get("/test_arg?test=10")
    assert response.status == 200
    assert response.json == {"test": 10}
