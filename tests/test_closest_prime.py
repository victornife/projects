"""Tests for closest_prime module."""
from importlib.machinery import SourceFileLoader
from pathlib import Path

module_path = Path(__file__).resolve().parents[1] / "closest-prime-project" / "closest_prime.py"
closest_prime_module = SourceFileLoader("closest_prime", str(module_path)).load_module()


def test_is_prime_basic_cases():
    """Test is_prime function with basic cases."""
    assert closest_prime_module.is_prime(2)
    assert closest_prime_module.is_prime(3)
    assert closest_prime_module.is_prime(13)
    assert not closest_prime_module.is_prime(1)
    assert not closest_prime_module.is_prime(0)
    assert not closest_prime_module.is_prime(-7)
    assert not closest_prime_module.is_prime(9)


def test_closest_prime_exact_prime():
    """Test closest_prime when input is already prime."""
    assert closest_prime_module.closest_prime(29) == 29


def test_closest_prime_lower_tie_breaker():
    """Test closest_prime returns lower prime when equidistant."""
    assert closest_prime_module.closest_prime(12) == 11


def test_closest_prime_edge_values():
    """Test closest_prime with edge case values."""
    assert closest_prime_module.closest_prime(2) == 2
    assert closest_prime_module.closest_prime(-100) == 2
