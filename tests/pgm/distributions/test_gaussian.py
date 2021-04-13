import numpy as np

from pgm import distributions


def test_gaussian():
    d = distributions.Gaussian(
        np.array([5.0, 3.0]), np.array([[1.0, 0.8], [0.8, 1.0]]), ["a", "b"]
    )
    assert d.sample().shape == (2, )
    assert d.sample(5).shape == (5, 2)


def test_marginalization():
    d = distributions.Gaussian(
        np.array([5.0, 3.0]), np.array([[1.0, 0.8], [0.8, 1.0]]), ["a", "b"]
    )
    m = d.marginalize("a")
    assert m.mean[0] == 3.0
    assert m.covariance[0, 0] == 1.0


def test_reorder():
    d = distributions.Gaussian(
        np.array([5.0, 3.0]), np.array([[1.0, 0.8], [0.8, 1.0]]), ["a", "b"]
    )
    d = d.reorder(["b", "a"])
    assert d.variable_names == ["b", "a"]
