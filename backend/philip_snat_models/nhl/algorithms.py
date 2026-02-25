import numpy as np


def predict_svm(attr, model):
    return {
        "algorithm": "svm",
        "prediction": model.predict_proba([attr])[0],
    }


def predict_knn(attr, model):
    return {
        "algorithm": "knn",
        "prediction": model.predict_proba([attr])[0],
    }


def predict_dt(attr, model):
    return {
        "algorithm": "decision tree",
        "prediction": model.predict_proba([attr])[0],
    }


def predict_gbdt(attr, model):
    return {
        "algorithm": "gradient boosted decision tree",
        "prediction": model.predict_proba([attr])[0],
    }


def predict_rf(attr, model):
    return {
        "algorithm": "random forest",
        "prediction": model.predict_proba([attr])[0],
    }


def predict_et(attr, model):
    return {
        "algorithm": "extra tree",
        "prediction": model.predict_proba([attr])[0],
    }


def predict_adaboost(attr, model):
    return {
        "algorithm": "adaboost",
        "prediction": model.predict_proba([attr])[0],
    }


def predict_lr(attr, model):
    return {
        "algorithm": "logistic regression",
        "prediction": np.round(model.predict_proba([attr])[0], 3),
    }


def run_ensemble(attr, models):
    results = []
    for name, model in models.items():
        try:
            proba = model.predict_proba([attr])[0]
            classes = model.classes_
            d = {str(int(c)): float(p) for c, p in zip(classes, proba)}
            results.append(d)
        except Exception as e:
            print(f"[ensemble] {name} failed: {e}")
    return results


def average_distributions(predictions, keys):
    if not predictions:
        return {k: 0.0 for k in keys}
    means = {}
    for key in keys:
        vals = [p.get(key, 0.0) for p in predictions]
        means[key] = sum(vals) / len(vals)
    return means
