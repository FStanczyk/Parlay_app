"""
Goals are now predicted via ensemble ML classifiers (SVM, KNN, DT, RF, ET, AdaBoost, LR)
trained at runtime from assets/merge_no_missing.csv — exactly the same procedure as NHL-AI-App.

This file is no longer needed. Training happens automatically inside NhlAiModel._train_goal_ensembles()
each time runner.py is executed.
"""

if __name__ == "__main__":
    print("Goals ensemble training now happens automatically in runner.py.")
    print("No separate training step is required.")
