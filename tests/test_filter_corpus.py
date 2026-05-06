"""Tests for tools/filter_corpus.py — apply physics-context filter locally."""
import json
import sys

import pytest


def test_is_physics_paper_pinn():
    import filter_corpus
    assert filter_corpus.is_physics_paper("Physics-informed neural networks solve PDEs.")


def test_is_physics_paper_dft():
    import filter_corpus
    assert filter_corpus.is_physics_paper("DFT surrogate models for electronic structure.")


def test_is_physics_paper_quantum():
    import filter_corpus
    assert filter_corpus.is_physics_paper("Quantum machine learning for many-body systems.")


def test_is_physics_paper_plasma():
    import filter_corpus
    assert filter_corpus.is_physics_paper("Tokamak control for fusion plasma.")


def test_is_physics_paper_cosmology():
    import filter_corpus
    assert filter_corpus.is_physics_paper("Deep learning for cosmological simulations with dark matter.")


def test_is_physics_paper_sciml():
    """Generic model paper with scientific physics context passes the filter."""
    import filter_corpus
    text = "We propose diffusion models for scientific discovery in physics."
    assert filter_corpus.is_physics_paper(text)


def test_is_not_physics_paper_pure_ml():
    """Pure ML/CS paper with no physics context fails."""
    import filter_corpus
    text = "We propose a Large Language Model for code generation tasks."
    assert not filter_corpus.is_physics_paper(text)


def test_is_not_physics_paper_robotics():
    import filter_corpus
    text = "Diffusion models for robot motion planning in cluttered environments."
    assert not filter_corpus.is_physics_paper(text)


def test_is_not_physics_paper_image():
    import filter_corpus
    text = "Generative adversarial networks for high-resolution image synthesis."
    assert not filter_corpus.is_physics_paper(text)


def test_is_physics_paper_empty_abstract():
    import filter_corpus
    assert not filter_corpus.is_physics_paper("")


def test_is_physics_paper_no_false_positive_on_generic_words():
    """Generic model terms alone do not trigger."""
    import filter_corpus
    assert not filter_corpus.is_physics_paper("Random text about networks and graphs.")
    assert not filter_corpus.is_physics_paper("Diffusion models for image editing.")
    assert not filter_corpus.is_physics_paper("Cosmological simulations with dark matter.")


def test_filter_corpus_writes_kept_papers(isolated_data_dir):
    """filter_corpus.run reads data/papers-*.json, writes to out_dir keeping
    only physics-relevant papers."""
    import filter_corpus
    import data_io
    physics_paper = {
        "title": "PINN PDE solver", "first_author": "A", "authors": ["A"],
        "abstract": "Physics-informed neural networks solve Navier-Stokes equations.",
        "primary_category": "physics.comp-ph",
        "categories": ["physics.comp-ph"],
        "published": "2025-04-01", "updated": "2025-04-05",
        "comment": None, "pdf_url": "http://arxiv.org/pdf/2504.00100",
        "topics": ["Scientific Machine Learning & PINNs"], "tags": [],
    }
    noise_paper = {
        "title": "LLM for code", "first_author": "B", "authors": ["B"],
        "abstract": "We use Large Language Models for code completion in IDEs.",
        "primary_category": "cs.LG", "categories": ["cs.LG"],
        "published": "2025-04-10", "updated": "2025-04-12",
        "comment": None, "pdf_url": "http://arxiv.org/pdf/2504.00200",
        "topics": ["Generative Models & Discovery"], "tags": [],
    }
    by_month = {"2025-04": {"2504.00100": physics_paper, "2504.00200": noise_paper}}
    data_io.save_month(by_month, "2025-04")

    out_dir = isolated_data_dir.root / "data_filtered"
    stats = filter_corpus.run(out_dir=out_dir)

    assert stats["kept"] == 1
    assert stats["dropped"] == 1
    out_file = out_dir / "papers-2025-04.json"
    assert out_file.exists()
    kept = json.loads(out_file.read_text(encoding="utf-8"))
    assert "2504.00100" in kept
    assert "2504.00200" not in kept


def test_filter_corpus_stats_per_topic(isolated_data_dir):
    """Stats report dropped count per topic — useful to see which topic is noisy."""
    import filter_corpus
    import data_io
    base = {
        "title": "x", "first_author": "x", "authors": ["x"],
        "abstract": "We propose a Large Language Model for code generation.",
        "primary_category": "cs.LG", "categories": ["cs.LG"],
        "published": "2025-04-01", "updated": "2025-04-05",
        "comment": None, "pdf_url": "http://arxiv.org/pdf/x",
        "tags": [],
    }
    by_month = {"2025-04": {
        "p1": {**base, "topics": ["Topic A"]},
        "p2": {**base, "topics": ["Topic A"]},
        "p3": {**base, "topics": ["Topic B"]},
    }}
    data_io.save_month(by_month, "2025-04")

    out_dir = isolated_data_dir.root / "data_filtered"
    stats = filter_corpus.run(out_dir=out_dir)

    assert stats["dropped_by_topic"]["Topic A"] == 2
    assert stats["dropped_by_topic"]["Topic B"] == 1
