import types
import yaml
import pytest


def test_generate_stream_is_generator():
    from src.data.synthetic import generate_stream
    g = generate_stream("uniform", 100, seed=0)
    assert isinstance(g, types.GeneratorType), "generate_stream must return a generator"


def test_generate_stream_correct_length():
    from src.data.synthetic import generate_stream
    items = list(generate_stream("uniform", 100, seed=0))
    assert len(items) == 100


def test_generate_stream_exhausts():
    from src.data.synthetic import generate_stream
    g = generate_stream("uniform", 10, seed=0)
    list(g)  # exhaust
    assert list(g) == [], "generator must be exhausted after single pass"


def test_generate_stream_deterministic():
    from src.data.synthetic import generate_stream
    a = list(generate_stream("zipf_1_1", 50, seed=7))
    b = list(generate_stream("zipf_1_1", 50, seed=7))
    assert a == b


def test_load_dataset_returns_generator():
    from src.data.datasets import load_dataset
    cfg = yaml.safe_load(open("configs/main.yaml"))
    g = load_dataset("uniform", cfg, seed=0)
    assert isinstance(g, types.GeneratorType)


def test_two_independent_passes_same_items():
    """Two calls with same seed yield identical streams."""
    from src.data.datasets import load_dataset
    cfg = yaml.safe_load(open("configs/main.yaml"))
    # Only consume first 5 items for speed
    a = [next(load_dataset("uniform", cfg, seed=0)) for _ in range(5)]
    b = [next(load_dataset("uniform", cfg, seed=0)) for _ in range(5)]
    assert a == b