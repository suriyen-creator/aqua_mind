# Synthetic model experiment

This directory is a technical demonstration of model training and explainability. The generated dataset is not field ground truth, and its metrics must not be reported as real-world AquaMind accuracy.

## Reproduce

From the project root:

```bash
python Model/generate_dataset.py
python Model/train.py
python Model/predict.py
```

`generate_dataset.py` creates same-time synthetic features and labels. It does not create a `t -> t+3..5` forecast dataset. The operational backend uses a different feature contract and will not load this model unless a separately trained model passes the validation gate.
