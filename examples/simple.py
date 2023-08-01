import datetime

from sanic import Sanic, response

from sanicargs import parse_parameters

app = Sanic("test_sanic_app")


@app.route("/me/<id>/birthdate", methods=["GET"])
@parse_parameters
async def test_datetime(request, id: str, birthdate: datetime.datetime):
    return response.json({"id": id, "birthdate": birthdate.isoformat()})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, access_log=False, debug=False)
