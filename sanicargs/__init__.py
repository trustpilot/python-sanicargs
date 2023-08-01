import datetime
import inspect
import json
from functools import wraps
from logging import getLogger

import ciso8601
from sanic.exceptions import BadRequest

from sanicargs.fields import List

__logger = getLogger("sanicargs")


def __parse_datetime(date_string):
    return ciso8601.parse_datetime_as_naive(date_string)


def __parse_date(date_string):
    return ciso8601.parse_datetime_as_naive(date_string).date()


def __parse_bool(str_or_bool):
    lower = str(str_or_bool).lower()
    if lower == "true":
        return True
    if lower == "false":
        return False
    raise ValueError("Can't parse {} as boolean".format(str_or_bool))


def __parse_list(str_or_list):
    try:
        return str_or_list.split(",")
    except AttributeError:
        return list(str_or_list)


__type_deserializers = {
    bool: __parse_bool,
    int: int,
    str: str,
    datetime.datetime: __parse_datetime,
    datetime.date: __parse_date,
    List[str]: __parse_list,
}


def parse_parameters(func):
    """parses query or body parameters depending on http method, validates and deserializes them
    VERY IMPORTANT!:
    to use this decorator it must be used in a Sanic endpoint and used BEFORE the
    sanic blueprint decorator like so:
        @blueprint.route("/foo/<businessunitid>/bar")
        @authorize_business_unit
        @parse_parameters
    and the signature of the function needs to start with request and the rest of
    the parameters need type hints like so:
        async def generate_csv(request, query: str, businessunitid: str):
    """
    return __parse(func)


def __parse(func, legacy=False):
    notations = inspect.signature(func)

    func_parameters = [
        (name, p.annotation, p.default) for name, p in notations.parameters.items()
    ]
    request_arg_name = inspect.getfullargspec(func)[0][0]

    @wraps(func)
    async def inner(request, *old_args, **route_parameters):
        kwargs = {}
        name = None
        if legacy or request.method == "GET":
            parameters = request.args
        else:
            if request.body == b"":  # support empty body
                parameters = {}
            else:
                parameters = json.loads(request.body)

        try:
            for name, arg_type, default in func_parameters:
                raw_value = parameters.get(name, None)

                # provided in route
                if name in route_parameters or name == request_arg_name:
                    if name == request_arg_name:
                        continue
                    raw_value = route_parameters[name]

                # no value
                elif name not in parameters:
                    if default != inspect._empty:
                        # TODO clone?
                        kwargs[name] = default
                        continue
                    else:
                        raise KeyError(
                            f"Missing required {'argument' if legacy else 'parameter'} {name}"
                        )

                parsed_value = __type_deserializers[arg_type](raw_value)
                kwargs[name] = parsed_value
        except Exception as err:
            __logger.warning(
                {
                    "message": f"Request {'args' if legacy else 'parameters'} not validated",
                    "name": name,
                    "raw_value": raw_value,
                    "stacktrace": str(err),
                }
            )
            raise BadRequest(f"Bad or missing value for {name}")
        return await func(request, **kwargs)

    return inner
