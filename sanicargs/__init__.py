import inspect
from functools import wraps
import ciso8601
import datetime

from sanic import response
from sanic.exceptions import abort
from sanicargs.fields import List

from logging import getLogger

__logger = getLogger("sanicargs")


def __parse_datetime(date_string):
    return ciso8601.parse_datetime_as_naive(date_string)


def __parse_date(date_string):
    return ciso8601.parse_datetime_as_naive(date_string).date()


def __parse_bool(str):
    lower = str.lower()
    if lower == "true":
        return True
    if lower == "false":
        return False
    raise ValueError("Can't parse {} as boolean".format(str))


__type_deserializers = {
    bool: __parse_bool,
    int: int,
    str: str,
    datetime.datetime: __parse_datetime,
    datetime.date: __parse_date,
    List[str]: lambda s: s.split(","),
}


def parse_query_args(func):
    """parses query args and validates, deserializes them
    VERY IMPORTANT!:
    to use this decorator it must be used in a Sanic endpoint and used BEFORE the 
    sanic blueprint decorator like so:
        @blueprint.route("/foo/<businessunitid>/bar")
        @authorize_business_unit
        @parse_query_args
    and the signature of the function needs to start with request and the rest of 
    the parameters need type hints like so:
        async def generate_csv(request, query: str, businessunitid: str):
    """
    notations = inspect.signature(func)

    parameters = [
        (name, p.annotation, p.default) for name, p in notations.parameters.items()
    ]
    request_arg_name = inspect.getfullargspec(func)[0][0]

    @wraps(func)
    async def inner(request, *old_args, **route_parameters):
        kwargs = {}
        name = None
        try:
            for name, arg_type, default in parameters:
                raw_value = request.args.get(name, None)

                # provided in route
                if name in route_parameters or name == request_arg_name:
                    if name == request_arg_name:
                        continue
                    raw_value = route_parameters[name]

                # no value
                elif name not in request.args:
                    if default != inspect._empty:
                        # TODO clone?
                        kwargs[name] = default
                        continue
                    else:
                        raise KeyError("Missing required argument %s" % name)

                parsed_value = __type_deserializers[arg_type](raw_value)
                kwargs[name] = parsed_value
        except Exception as err:
            __logger.warning(
                {
                    "message": "Request args not validated",
                    "name": name,
                    "raw_value": raw_value,
                    "stacktrace": str(err),
                }
            )
            return abort(400, "Bad or missing value for %s" % name)
        return await func(request, **kwargs)

    return inner
