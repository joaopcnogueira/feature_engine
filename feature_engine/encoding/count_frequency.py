# Authors: Soledad Galli <solegalli@protonmail.com>
# License: BSD 3 clause

from collections import defaultdict
from typing import List, Optional, Union

import pandas as pd

from feature_engine._docstrings.fit_attributes import (
    _feature_names_in_docstring,
    _n_features_in_docstring,
    _variables_attribute_docstring,
)
from feature_engine._docstrings.methods import (
    _fit_transform_docstring,
    _inverse_transform_docstring,
)
from feature_engine._docstrings.substitute import Substitution
from feature_engine.dataframe_checks import check_X
from feature_engine.encoding._docstrings import (
    _errors_docstring,
    _ignore_format_docstring,
    _transform_docstring,
    _variables_docstring,
)
from feature_engine.encoding._helper_functions import check_parameter_errors
from feature_engine.encoding.base_encoder import (
    CategoricalInitMixin,
    CategoricalMethodsMixin,
)

_errors_docstring = (
    _errors_docstring
    + """ If `'encode'`, unseen categories will be encoded as 0 (zero)."""
)


@Substitution(
    ignore_format=_ignore_format_docstring,
    variables=_variables_docstring,
    errors=_errors_docstring,
    variables_=_variables_attribute_docstring,
    feature_names_in_=_feature_names_in_docstring,
    n_features_in_=_n_features_in_docstring,
    fit_transform=_fit_transform_docstring,
    transform=_transform_docstring,
    inverse_transform=_inverse_transform_docstring,
)
class CountFrequencyEncoder(CategoricalInitMixin, CategoricalMethodsMixin):
    """
    The CountFrequencyEncoder() replaces categories by either the count or the
    percentage of observations per category.

    For example in the variable colour, if 10 observations are blue, blue will
    be replaced by 10. Alternatively, if 10% of the observations are blue, blue
    will be replaced by 0.1.

    The CountFrequencyEncoder() will encode only categorical variables by default
    (type 'object' or 'categorical'). You can pass a list of variables to encode.
    Alternatively, the encoder will find and encode all categorical variables
    (type 'object' or 'categorical').

    With `ignore_format=True` you have the option to encode numerical variables as well.
    The procedure is identical, you can either enter the list of variables to encode, or
    the transformer will automatically select all variables.

    The encoder first maps the categories to the counts or frequencies for each
    variable (fit). The encoder then replaces the categories with those numbers
    (transform).

    More details in the :ref:`User Guide <count_freq_encoder>`.

    Parameters
    ----------
    encoding_method: str, default='count'
        Desired method of encoding.

        **'count'**: number of observations per category

        **'frequency'**: percentage of observations per category

    {variables}

    {ignore_format}

    {errors}

    Attributes
    ----------
    encoder_dict_:
        Dictionary with the count or frequency per category, per variable.

    {variables_}

    {feature_names_in_}

    {n_features_in_}

    Methods
    -------
    fit:
        Learn the count or frequency per category, per variable.

    {fit_transform}

    {inverse_transform}

    {transform}

    Notes
    -----
    NAN will be introduced when encoding categories that were not present in the
    training set. If this happens, try grouping infrequent categories using the
    RareLabelEncoder(), or set `errors='encode'`.

    There is a similar implementation in the open-source package
    `Category encoders <https://contrib.scikit-learn.org/category_encoders/>`_

    See Also
    --------
    feature_engine.encoding.RareLabelEncoder
    category_encoders.count.CountEncoder
    """

    def __init__(
        self,
        encoding_method: str = "count",
        variables: Union[None, int, str, List[Union[str, int]]] = None,
        ignore_format: bool = False,
        errors: str = "ignore",
    ) -> None:

        if encoding_method not in ["count", "frequency"]:
            raise ValueError(
                "encoding_method takes only values 'count' and 'frequency'. "
                f"Got {encoding_method} instead."
            )

        check_parameter_errors(errors, ["ignore", "raise", "encode"])
        super().__init__(variables, ignore_format)
        self.encoding_method = encoding_method
        self.errors = errors

    def fit(self, X: pd.DataFrame, y: Optional[pd.Series] = None):
        """
        Learn the counts or frequencies which will be used to replace the categories.

        Parameters
        ----------
        X: pandas dataframe of shape = [n_samples, n_features]
            The training dataset. Can be the entire dataframe, not just the
            variables to be transformed.

        y: pandas Series, default = None
            y is not needed in this encoder. You can pass y or None.
        """
        X = check_X(X)
        self._fit(X)
        self._get_feature_names_in(X)

        self.encoder_dict_ = {}
        dct_init = defaultdict(lambda: 0) if self.errors == "encode" else {}

        # learn encoding maps
        for var in self.variables_:
            if self.encoding_method == "count":
                self.encoder_dict_[var] = X[var].value_counts().to_dict(dct_init)

            elif self.encoding_method == "frequency":
                self.encoder_dict_[var] = (
                    X[var].value_counts(normalize=True).to_dict(dct_init)
                )

        self._check_encoding_dictionary()

        return self
