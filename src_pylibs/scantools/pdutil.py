from typing import Union
import pandas as pd

def fill_df(
        df_or_series: Union[pd.DataFrame, pd.Series], limit: int,
        fill_method='interpolate',
        **fill_method_kwargs) -> Union[pd.DataFrame, pd.Series]:
    """The fill methods from Pandas such as ``interpolate`` or ``bfill``
    will fill ``limit`` number of NaNs, even if the total number of
    consecutive NaNs is larger than ``limit``. This function instead
    does not fill any data when the number of consecutive NaNs
    is > ``limit``.

    Adapted from: https://stackoverflow.com/a/30538371/11052174
    Obtained from: https://stackoverflow.com/questions/30533021/interpolate-or-extrapolate-only-small-gaps-in-pandas-dataframe on 2021-03-30 09:36:29
    :param df_or_series: DataFrame or Series to perform interpolation
        on.
    :param limit: Maximum number of consecutive NaNs to allow. Any
        occurrences of more consecutive NaNs than ``limit`` will have no
        filling performed.
    :param fill_method: Filling method to use, e.g. 'interpolate',
        'bfill', etc.
    :param fill_method_kwargs: Keyword arguments to pass to the
        fill_method, in addition to the given limit.

    :returns: A filled version of the given df_or_series according
        to the given inputs.
    """

    # Keep things simple, ensure we have a DataFrame.
    try:
        df = df_or_series.to_frame()
    except AttributeError:
        df = df_or_series

    # Initialize our mask.
    mask = pd.DataFrame(True, index=df.index, columns=df.columns)

    # Get cumulative sums of consecutive NaNs.
    grp = (df.notnull() != df.shift().notnull()).cumsum()

    # Add columns of ones.
    grp['ones'] = 1

    # Loop through columns and update the mask.
    for col in df.columns:

        mask.loc[:, col] = (
                (grp.groupby(col)['ones'].transform('count') <= limit)
                | df[col].notnull()
        )

    # Now, interpolate and use the mask to create NaNs for the larger
    # gaps.
    method = getattr(df, fill_method)
    out = method(limit=limit, **fill_method_kwargs)[mask]

    # Be nice to the caller and return a Series if that's what they
    # provided.
    if isinstance(df_or_series, pd.Series):
        # Return a Series.
        return out.loc[:, out.columns[0]]

    return out
