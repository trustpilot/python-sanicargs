[![Build Status](https://travis-ci.org/trustpilot/python-sanicargs.svg?branch=master)](https://travis-ci.org/trustpilot/python-sanicargs) [![Latest Version](https://img.shields.io/pypi/v/sanicargs.svg)](https://pypi.python.org/pypi/sanicargs) [![Python Support](https://img.shields.io/pypi/pyversions/sanicargs.svg)](https://pypi.python.org/pypi/sanicargs)

# Sanicargs
Parses query args in [Sanic](https://github.com/channelcat/sanic) using type annotations.

## Survey
Please fill out [this survey](https://docs.google.com/forms/d/e/1FAIpQLSdNLvB7NEJQhUyVdaZpBAgS0f1k9OywZp8xDqhaNY0rl-unZA/viewform?usp=sf_link) if you are using Sanicargs, we are gathering feedback :-)

## Install
Install with pip
```
$ pip install sanicargs
```

## Usage

Use the `parse_query_args` decorator to parse query args and type cast query args and path params with [Sanic](https://github.com/channelcat/sanic)'s routes or blueprints like in the [example](https://github.com/trustpilot/python-sanicargs/tree/master/examples/simple.py) below:

```python
import datetime
from sanic import Sanic, response
from sanicargs import parse_query_args

app = Sanic("test_sanic_app")

@app.route("/me/<id>/birthdate", methods=['GET'])
@parse_query_args
async def test_datetime(req, id: str, birthdate: datetime.datetime):
    return response.json({
        'id': id, 
        'birthdate': birthdate.isoformat()
    })

if __name__ == "__main__":
  app.run(host="0.0.0.0", port=8080, access_log=False, debug=False)
```

Test it running with 
```bash
$ curl 'http://0.0.0.0:8080/me/123/birthdate?birthdate=2017-10-30'
```

### Fields

* **str** : `ex: ?message=hello world`
* **int** : `ex: ?age=100`
* **bool** : `ex: ?missing=false`
* **datetime.datetime** : `ex: ?currentdate=2017-10-30T10:10:30 or 2017-10-30`
* **datetime.date** : `ex: ?birthdate=2017-10-30`
* **List[str]** : `ex: ?words=you,me,them,we`

### Note about datetimes

Dates and datetimes are parsed without timezone information giving you a "naive datetime" object. See the note on [datetime.timestamp()](https://docs.python.org/3/library/datetime.html#datetime.datetime.timestamp) about handling timezones if you require epoch format timestamps.

### Important notice about decorators

The sequence of decorators is, as usual, important in Python.

You need to apply the `parse_query_args` decorator as the first one executed which means closest to the `def`.

### `request` is mandatory!

You should always have request as the first argument in your function in order to use `parse_query_args`.

**Note** that `request` arg can be renamed and even type-annotated as long as it is the first arg.
