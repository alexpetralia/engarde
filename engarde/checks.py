# -*- coding: utf-8 -*-
"""
checks.py

Each function in here should

- Take a DataFrame as its first argument, maybe optional arguments
- Makes its assert on the result
- Return the original DataFrame
"""
import numpy as np
import pandas as pd

from engarde.utils import bad_locations


def none_missing(df, columns=None):
    """
    Asserts that there are no missing values (NaNs) in the DataFrame.
    """
    if columns is None:
        columns = df.columns
    try:
        assert not df[columns].isnull().any().any()
    except AssertionError as e:
        missing = df[columns].isnull()
        msg = bad_locations(missing)
        e.args = msg
        raise
    return df

def is_monotonic(df, items=None, increasing=None, strict=False):
    """
    Asserts that the DataFrame is monotonic

    Parameters
    ==========

    df : Series or DataFrame
    items : dict
        mapping columns to conditions (increasing, strict)
    increasing : None or bool
        None is either increasing or decreasing.
    strict: whether the comparison should be strict
    """
    if items is None:
        items = {k: (increasing, strict) for k in df}

    for col, (increasing, strict) in items.items():
        s = pd.Index(df[col])
        if increasing:
            good = getattr(s, 'is_monotonic_increasing')
        elif increasing is None:
            good = getattr(s, 'is_monotonic') | getattr(s, 'is_monotonic_decreasing')
        else:
            good = getattr(s, 'is_monotonic_decreasing')
        if strict:
            if increasing:
                good = good & (s.to_series().diff().dropna() > 0).all()
            elif increasing is None:
                good = good & ((s.to_series().diff().dropna() > 0).all() |
                               (s.to_series().diff().dropna() < 0).all())
            else:
                good = good & (s.to_series().diff().dropna() < 0).all()
        if not good:
            raise AssertionError
    return df

def is_shape(df, shape):
    """
    Asserts that the DataFrame is of a known shape.

    Parameters
    ==========

    df: DataFrame
    shape : tuple (n_rows, n_columns)
    """
    try:
        assert df.shape == shape
    except AssertionError as e:
        msg = ("Expected shape: {}\n"
               "\t\tActual shape:   {}".format(shape, df.shape))
        e.args = msg
        raise
    return df

def unique_index(df):
    """Assert that the index is unique"""
    try:
        assert df.index.is_unique
    except AssertionError as e:
        e.args = df.index.get_duplicates()
        raise
    return df


def within_set(df, items=None):
    """
    Assert that df is a subset of items

    Parameters
    ==========

    df : DataFrame
    items : dict
        mapping of columns (k) to array-like of values (v) that
        ``df[k]`` is expected to be a subset of
    """
    for k, v in items.items():
        if not df[k].isin(v).all():
            bad = df.loc[~df[k].isin(v), k]
            raise AssertionError('Not in set', bad)
    return df

def within_range(df, items=None):
    """
    Assert that a DataFrame is within a range.

    Parameters
    ==========
    df : DataFame
    items : dict
        mapping of columns (k) to a (low, high) tuple (v)
        that ``df[k]`` is expected to be between.
    """
    for k, (lower, upper) in items.items():
        if (lower > df[k]).any() or (upper < df[k]).any():
            bad = (lower > df[k]) | (upper < df[k])
            raise AssertionError("Outside range", bad)
    return df

def within_n_std(df, n=3):
    means = df.mean()
    stds = df.std()
    inliers = (np.abs(df - means) < n * stds)
    if not np.all(inliers):
        msg = bad_locations(~inliers)
        raise AssertionError(msg)
    return df

def has_dtypes(df, items):
    """
    Assert that a DataFrame has `dtypes`

    Parameters
    ==========
    df: DataFrame
    items: dict
        mapping of columns to dtype.
    """
    dtypes = df.dtypes
    for k, v in items.items():
        if not dtypes[k] == v:
            raise AssertionError("{} has the wrong dtype ({})".format(k, v))
    return df

__all__ = [is_monotonic, is_shape, none_missing, unique_index, within_n_std,
           within_range, within_set, has_dtypes]

