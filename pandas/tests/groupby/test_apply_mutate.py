import numpy as np

import pandas as pd
import pandas._testing as tm


def test_group_by_copy():
    # GH#44803
    df = pd.DataFrame(
        {
            "name": ["Alice", "Bob", "Carl"],
            "age": [20, 21, 20],
        }
    ).set_index("name")

    grp_by_same_value = df.groupby(["age"], group_keys=False).apply(lambda group: group)
    grp_by_copy = df.groupby(["age"], group_keys=False).apply(
        lambda group: group.copy()
    )
    tm.assert_frame_equal(grp_by_same_value, grp_by_copy)


def test_mutate_groups():
    # GH3380

    df = pd.DataFrame(
        {
            "cat1": ["a"] * 8 + ["b"] * 6,
            "cat2": ["c"] * 2
            + ["d"] * 2
            + ["e"] * 2
            + ["f"] * 2
            + ["c"] * 2
            + ["d"] * 2
            + ["e"] * 2,
            "cat3": [f"g{x}" for x in range(1, 15)],
            "val": np.random.default_rng(2).integers(100, size=14),
        }
    )

    def f(x):
        x = x.copy()
        x["rank"] = x.val.rank(method="min")
        return x.groupby("cat2")["rank"].min()

    expected = pd.DataFrame(
        {
            "cat1": list("aaaabbb"),
            "cat2": list("cdefcde"),
            "rank": [3.0, 2.0, 5.0, 1.0, 2.0, 4.0, 1.0],
        }
    ).set_index(["cat1", "cat2"])["rank"]
    result = df.groupby("cat1").apply(f)
    tm.assert_series_equal(result, expected)


def test_no_mutate_but_looks_like():
    # GH 8467
    # first show's mutation indicator
    # second does not, but should yield the same results
    df = pd.DataFrame({"key": [1, 1, 1, 2, 2, 2, 3, 3, 3], "value": range(9)})

    result1 = df.groupby("key", group_keys=True).apply(lambda x: x[:].value)
    result2 = df.groupby("key", group_keys=True).apply(lambda x: x.value)
    tm.assert_series_equal(result1, result2)
