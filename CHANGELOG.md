# Change Log

## 0.0.1 (2017-01-09)

- git init

# 1.0.0(2017-01-12)

- added test suite
- added path_param type casting

# 1.1.0(2018-03-01)

- request can be renamed and even type-annotated

# 1.2.0 (2018-03-01)

- added support for boolean parameters

# 1.3.0 (2019-01-08)

- @wraps the inner function to keep the args signature

# 1.4.0 (2019-03-04)

- Update deps to allow latest version of sanic

# 2.0.0 (2020-03-18)

- Require `sanic >= 18.12` (LTS)
- Use `ciso8601` to parse date

# 2.0.1 (2020-03-18)

- Remove forgotten `print` statement

# 2.0.2 (2020-03-18)

- Log `raw_value` if parsing is failing

# 2.0.3 (2020-03-18)

- re-release version since @sloev reacted a little too fast on deleting a release

# 2.1.0 (2020-12-18)

- Add parse_parameters decorator to support both GET(query params) and POST(body params) requests
- Start deprecated process of parse_query_args

# 3.0.0 (2023-08-01)

- Bump versions of everything
- Depricate `parse_query_args`