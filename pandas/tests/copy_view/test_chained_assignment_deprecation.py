import numpy as np
import pytest

from pandas.errors import ChainedAssignmentError

from pandas import DataFrame
import pandas._testing as tm


def test_methods_iloc_warn(using_copy_on_write):
    if not using_copy_on_write:
        df = DataFrame({"a": [1, 2, 3], "b": 1})
        with tm.assert_cow_warning(match="A value"):
            df.iloc[:, 0].replace(1, 5, inplace=True)

        with tm.assert_cow_warning(match="A value"):
            df.iloc[:, 0].fillna(1, inplace=True)

        with tm.assert_cow_warning(match="A value"):
            df.iloc[:, 0].interpolate(inplace=True)

        with tm.assert_cow_warning(match="A value"):
            df.iloc[:, 0].ffill(inplace=True)

        with tm.assert_cow_warning(match="A value"):
            df.iloc[:, 0].bfill(inplace=True)


# TODO(CoW-warn) expand the cases
@pytest.mark.parametrize(
    "indexer", [0, [0, 1], slice(0, 2), np.array([True, False, True])]
)
def test_series_setitem(indexer, using_copy_on_write):
    # ensure we only get a single warning for those typical cases of chained
    # assignment
    df = DataFrame({"a": [1, 2, 3], "b": 1})

    # using custom check instead of tm.assert_produces_warning because that doesn't
    # fail if multiple warnings are raised
    with pytest.warns() as record:
        df["a"][indexer] = 0
    assert len(record) == 1
    if using_copy_on_write:
        assert record[0].category == ChainedAssignmentError
    else:
        assert record[0].category == FutureWarning
        assert "ChainedAssignmentError" in record[0].message.args[0]


@pytest.mark.parametrize(
    "indexer", ["a", ["a", "b"], slice(0, 2), np.array([True, False, True])]
)
def test_frame_setitem(indexer):
    df = DataFrame({"a": [1, 2, 3, 4, 5], "b": 1})

    with tm.raises_chained_assignment_error():
        df[0:3][indexer] = 10
