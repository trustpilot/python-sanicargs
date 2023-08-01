import uuid

import pytest
from sanic import response, Sanic
from sanic_testing import TestManager

from sanicargs import parse_parameters, fields
from sanic.server.protocols.websocket_protocol import WebSocketProtocol
from sanic import request

import datetime

from functools import wraps
import inspect
import json


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

    @app.route("/int", methods=["POST"])
    @parse_parameters
    async def test_int(request, test: int):
        return response.json({"test": test})

    @app.route("/str", methods=["POST"])
    @parse_parameters
    async def test_str(request, test: str):
        return response.json({"test": test})

    @app.route("/bool", methods=["POST"])
    @parse_parameters
    async def test_bool(request, test: bool):
        return response.json({"test": test})

    @app.route("/datetime", methods=["POST"])
    @parse_parameters
    async def test_datetime(request, test: datetime.datetime):
        return response.json({"test": test.isoformat()})

    @app.route("/date", methods=["POST"])
    @parse_parameters
    async def test_date(request, test: datetime.date):
        return response.json({"test": test.isoformat()})

    @app.route("/list", methods=["POST"])
    @parse_parameters
    async def test_list(req, test: fields.List[str] = None):
        return response.json({"test": test})

    @app.route("/all", methods=["POST"])
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

    @app.route("/optional", methods=["POST"])
    @parse_parameters
    async def test_optional(request, test: str = "helloworld"):
        return response.json({"test": test})

    @app.route("/with/<path_param>/path_params", methods=["POST"])
    @parse_parameters
    async def test_path_params(request, path_param: int, test: str, test_2: int = 35):
        return response.json({"path_param": path_param, "test": test, "test_2": test_2})

    @app.route("/test_arg", methods=["POST"])
    @has_test_arg
    @parse_parameters
    async def test_args(request, test: int):
        return response.json({"test": test})

    return app



#########
# Tests #
#########


def test_parse_int_success(app):
    __, response = app.test_client.post("/int", data=json.dumps({"test": 10}))
    assert response.status == 200
    assert response.json == {"test": 10}


def test_parse_int_fail(app):
    __, response = app.test_client.post("/int", data=json.dumps({"test": "not an integer"}))
    assert response.status == 400


def test_parse_bool_true_success(app):
    __, response = app.test_client.post("/bool", data=json.dumps({"test": True}))
    assert response.status == 200
    assert response.json == {"test": True}


def test_parse_bool_false_success(app):
    __, response = app.test_client.post("/bool", data=json.dumps({"test": False}))
    assert response.status == 200
    assert response.json == {"test": False}


def test_parse_bool_fail(app):
    __, response = app.test_client.post("/bool", data=json.dumps({"test": "not an bool"}))
    assert response.status == 400


def test_parse_str_success(app):
    __, response = app.test_client.post("/str", data=json.dumps({"test": "hello"}))
    assert response.status == 200
    assert response.json == {"test": "hello"}


def test_parse_str_also_works_with_int(app):
    """ allow strings to work as ints
    """
    __, response = app.test_client.post("/str", data=json.dumps({"test": "400"}))
    assert response.status == 200


def test_parse_datetime_success(app):
    __, response = app.test_client.post(
        "/datetime", data=json.dumps({"test": "2017-10-10T10:10:10"})
    )
    assert response.status == 200
    assert response.json == {"test": "2017-10-10T10:10:10"}


def test_parse_datetime_fail(app):
    __, response = app.test_client.post("/datetime", data=json.dumps({"test": "not a datetime"}))
    assert response.status == 400


def test_parse_date_success(app):
    __, response = app.test_client.post("/date", data=json.dumps({"test": "2017-10-19"}))
    assert response.status == 200
    assert response.json == {"test": "2017-10-19"}


def test_parse_date_fail(app):
    __, response = app.test_client.post("/date", data=json.dumps({"test": "not a datetime"}))
    assert response.status == 400


def test_parse_string_list_success(app):
    __, response = app.test_client.post("/list", data=json.dumps({"test": "one,two,three"}))
    assert response.status == 200
    assert response.json == {"test": ["one", "two", "three"]}


def test_parse_list_success(app):
    __, response = app.test_client.post(
        "/list", data=json.dumps({"test": ["one", "two", "three"]})
    )
    assert response.status == 200
    assert response.json == {"test": ["one", "two", "three"]}


def test_parse_string_list_also_works_with_singular(app):
    __, response = app.test_client.post("/list", data=json.dumps({"test": "not a datetime"}))
    assert response.status == 200
    assert response.json == {"test": ["not a datetime"]}


def test_parse_list_also_works_with_singular(app):
    __, response = app.test_client.post("/list", data=json.dumps({"test": ["not a datetime"]}))
    assert response.status == 200
    assert response.json == {"test": ["not a datetime"]}


def test_all_at_once(app):
    __, response = app.test_client.post(
        "/all",
        data=json.dumps(
            {
                "a": 10,
                "b": "test",
                "c": "2017-10-10T10:10:10",
                "d": "2017-10-10",
                "e": ["a", "b", "c", "d", "e"],
            }
        ),
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
    __, response = app.test_client.post("/optional")
    assert response.status == 200
    assert response.json == {"test": "helloworld"}


def test_mandatory(app):
    __, response = app.test_client.post("/str")
    assert response.status == 400


def test_with_path_params(app):
    __, response = app.test_client.post(
        "/with/123/path_params", data=json.dumps({"test": "hello"})
    )
    assert response.status == 200
    assert response.json == {"path_param": 123, "test": "hello", "test_2": 35}


def test_args_success(app):
    __, response = app.test_client.post("/test_arg", data=json.dumps({"test": 10}))
    assert response.status == 200
    assert response.json == {"test": 10}
