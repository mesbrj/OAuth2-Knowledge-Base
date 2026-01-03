
```bash
export ENVIRONMENT=test
pytest --cov=src -v
```

```bash
collected 8 items                                                          

tests/unit/test_core_data_mgmt.py::test_inbound_factory PASSED        [ 12%]
tests/unit/test_core_data_mgmt.py::test_general_data_manager PASSED   [ 25%]
tests/unit/test_core_data_mgmt.py::test_pub_data_manager PASSED       [ 37%]
tests/unit/test_db_data_access.py::test_db_data_access PASSED         [ 50%]
tests/unit/test_db_session.py::test_db_session PASSED                 [ 62%]
tests/unit/test_web_api.py::test_health_check[asyncio] PASSED         [ 75%]
tests/unit/test_web_api.py::test_create_team[asyncio] PASSED          [ 87%]
tests/unit/test_web_api.py::test_create_user[asyncio] PASSED          [100%]

============================== tests coverage ==============================
_____________ coverage: platform linux, python 3.13.9-final-0 ______________

Name                              Stmts   Miss  Cover
-----------------------------------------------------
src/adapter/rest/dto.py              34      0   100%
src/adapter/rest/func_deps.py         6      0   100%
src/adapter/rest/routes.py           14      0   100%
src/adapter/rest/server.py           17      5    71%
src/adapter/sql/data_access.py       38      7    82%
src/adapter/sql/data_base.py         32      5    84%
src/adapter/sql/models.py            52      0   100%
src/core/data_domain.py              49      0   100%
src/core/data_manager_helper.py      21      2    90%
src/core/use_cases.py                30      3    90%
src/main.py                           9      9     0%
src/ports/inbound.py                 11      2    82%
src/ports/interfaces.py               4      0   100%
src/ports/repository.py               5      1    80%
-----------------------------------------------------
TOTAL                               322     34    89%
============================ 8 passed in 0.48s =============================
```

