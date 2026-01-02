
```bash
export ENVIRONMENT=test
pytest --cov=src -v
```

```bash
collected 5 items                                                          

tests/unit/test_core_data_mgmt.py::test_inbound_factory PASSED       [ 20%]
tests/unit/test_core_data_mgmt.py::test_general_data_manager PASSED  [ 40%]
tests/unit/test_core_data_mgmt.py::test_pub_data_manager PASSED      [ 60%]
tests/unit/test_db_data_access.py::test_db_data_access PASSED        [ 80%]
tests/unit/test_db_session.py::test_db_session PASSED                [100%]

============================== tests coverage ==============================
_____________ coverage: platform linux, python 3.13.9-final-0 ______________

Name                              Stmts   Miss  Cover
-----------------------------------------------------
src/adapter/sql/data_access.py       38      7    82%
src/adapter/sql/data_base.py         32      5    84%
src/adapter/sql/models.py            41      0   100%
src/core/data_domain.py              20      0   100%
src/core/data_manager_helper.py      21      2    90%
src/core/use_cases.py                30      3    90%
src/main.py                           0      0   100%
src/ports/inbound.py                 11      2    82%
src/ports/interfaces.py               4      0   100%
src/ports/repository.py               5      1    80%
-----------------------------------------------------
TOTAL                               202     20    90%
============================ 5 passed in 0.31s =============================
```

