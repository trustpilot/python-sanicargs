[![Build Status](https://travis-ci.org/trustpilot/python-sanicargs.svg?branch=master)](https://travis-ci.org/trustpilot/python-sanicargs) [![Latest Version](https://img.shields.io/pypi/v/sanicargs.svg)](https://pypi.python.org/pypi/sanicargs) [![Python Support](https://img.shields.io/pypi/pyversions/sanicargs.svg)](https://pypi.python.org/pypi/sanicargs)

# Sanicargs
Parses query args in sanic using type annotations

## Usage

Use with [Sanic framework](https://github.com/channelcat/sanic)
```
    @app.route("/datetime", methods=['GET'])
    @parse_query_args
    async def test_datetime(request, test: datetime.datetime):
        return response.json({'test': test.isoformat()})
```