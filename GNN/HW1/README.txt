Exercise 1 - Classical generative models

MAIN FILES
  generative-baselines.ipynb  Executed solution with code, outputs and analysis
  generative-baselines.pdf    Complete readable export of the executed notebook
  density_forest.py           Original implementation supplied by the course
  requirements.txt            Python dependencies for running the notebook
  moon_results.csv           All validation MMD measurements for moons
  digit_results.csv          All validation MMD measurements for digits
  digit_test_scores.csv      Final digit test and classifier diagnostics

REPRODUCE
  Install requirements.txt into a Python 3.10+ environment with Jupyter.
  Open generative-baselines.ipynb from this folder and Run All.
  Keep density_forest.py in the same folder as the notebook.
  The optional .packages bootstrap is only for the local authoring environment.
  It is not required and the dependency directory is not included in the zip.

METHOD NOTES
  Part 1 estimators and MMD are implemented from scratch.
  Part 2 uses sklearn and the supplied forest, as required.
  Forest trees are fitted sequentially with explicit seeds for reproducibility.
  Forest-only training jitter and a NumPy compatibility alias are documented.
  Validation selects hyperparameters; final test data are separate.
  Classifier confidence is a proxy for recognizability, not ground truth.
  The notebook reports limited repetition counts and modelling limitations.

Before submitting, review the notebook and confirm any course-specific rules.
Upload ex01.zip to the correct MaMPF submission and check the team membership.
