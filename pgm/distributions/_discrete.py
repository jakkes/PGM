from typing import Sequence, Optional, Tuple

import numpy as np

import pgm.distributions as distributions


class Discrete(distributions.Base):
    """Discrete multivariate distribution."""

    def __init__(
        self,
        values: Sequence[Sequence[float]],
        probabilities: np.ndarray,
        variable_names: Sequence[str],
    ):
        """
        Args:
            values (Sequence[Sequence[float]]): Values obtainable by each variable in
                the multivariate distribution. The first output can take values in the
                first sequence, second variable values in the second sequence, etc.
            probabilities (np.ndarray): Probabilities of each value combination. If
                there are `D` variables, each taking `n_i` possible values, then this
                array should be of shape `(n_1, n_2, ..., n_D)`.
            variable_names (Sequence[str]): Name of each variable output.
        """
        super().__init__(variable_names)
        self._values = np.array([np.array(x, copy=True) for x in values], dtype=object)
        self._probabilities = np.array(probabilities, copy=True, dtype=np.float32)
        self._cumsummed = self._probabilities.ravel().cumsum(0)

        if self._probabilities.sum() != 1.0:
            raise ValueError("Probabilities need to sum to one.")
        if np.any(self._probabilities < 0):
            raise ValueError("Probabilities cannot be negative.")
        for values, dim in zip(self._values, self._probabilities.shape):
            if len(values) != dim:
                raise ValueError("Probabilities were not of expected shape.")

    @property
    def values(self) -> np.ndarray:
        """Values obtainable by the distribution."""
        return self._values.copy()

    @property
    def probabilities(self) -> np.ndarray:
        """Probabilities of taking each value."""
        return self._probabilities.copy()

    def sample(self, batches: Optional[int] = None) -> np.ndarray:
        if batches is None:
            return self.sample(1)[0]

        w = np.random.random(size=(batches, 1))
        i = np.unravel_index(
            np.sum(w > self._cumsummed, axis=1), self._probabilities.shape
        )
        return np.stack([value[j] for value, j in zip(self._values, i)], axis=1)

    def marginalize(self, variable_name: str) -> "Discrete":
        i = self.variable_names.index(variable_name)
        return Discrete(
            np.concatenate((self._values[:i], self._values[i+1:]), axis=0),
            self._probabilities.sum(axis=i),
            [*self.variable_names[:i], *self.variable_names[i+1:]]
        )

    def _reorder(self, variable_names: Sequence[str]) -> "Discrete":
        values = self._values
        probs = self._probabilities
        current_order = list(self.variable_names)

        for i, name in enumerate(variable_names):
            j = current_order.index(name)
            values[i], values[j] = values[j].copy(), values[i].copy()
            probs = np.swapaxes(probs, j, i)
            current_order[i], current_order[j] = current_order[j], current_order[i]

        return Discrete(values, probs, current_order)
