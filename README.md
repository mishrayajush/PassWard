# PassWard - Password Strength Checker

PassWard is a local Flask application that analyzes fictional passwords and explains their composition, predicted strength, 1-10 rating, and improvement suggestions.

## Run the Flask application

Requires Python 3.12 and Git. Clone the repository, then install dependencies and run:

```powershell
git clone https://github.com/mishrayajush/PassWard.git
cd PassWard
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
py -3.12 -m pip install -r requirements.txt
py -3.12 flask_app.py
```

Open `http://127.0.0.1:5000/check` in your browser. Keep the terminal open while using the website. Press `Ctrl+C` to stop Flask and `Ctrl+F5` to hard-refresh after code changes.

## Current model files

- `password_strength_svm.pkl` - trained Linear SVM classifier.
- `password_strength_features.pkl` - fitted character-level TF-IDF extractor.

## Retrain the model

The commented training workflow is `train_better_model.ipynb`. It loads and cleans `data.csv`, splits the data, extracts character n-gram TF-IDF features, trains a balanced Linear SVM, evaluates it, and saves the two current model artifacts.

Install notebook dependencies with `python -m pip install -r requirements-dev.txt`, then run the notebook with the Python 3.12 kernel. Do not retrain every time you run the website. Running the final saving cell replaces the bundled model artifacts.

The raw dataset is deliberately excluded from Git. To retrain, place your authorized dataset at `data.csv` in the project root, with columns `password` and `strength` (0 = Weak, 1 = Medium, 2 = Strong). The notebook uses an 80/20 stratified split with seed 42, a union of character and word-boundary TF-IDF features (2–5 character n-grams), and `LinearSVC(class_weight='balanced', C=2.0, random_state=42)`.

Four separate plots describe the data before training; a confusion matrix and per-class precision, recall, and F1 chart describe test performance. Actual results are generated when you run the notebook.

## Application behavior

The landing page introduces PassWard. The checker counts password characteristics, shows a model prediction, displays a 1-10 rating, provides live visual indicators, and generates improvement suggestions. Rating bands are: 1-3 Weak, 4-5 Below average, 6-7 Medium, 8-9 Strong, and 10 Very strong.

## Privacy and limitations

The browser sends entered text to the Flask server for analysis. The application does not intentionally persist entered passwords. Use fictional samples in demos. The model is an educational baseline and should not be treated as a production password-security control. The displayed rating combines heuristic scoring with the model prediction; it is not a calibrated probability or an estimate of cracking time. Future evaluation could include cross-validation and measured comparisons against baseline models.

The bundled pickle files must only be loaded from a trusted source. Python and scikit-learn versions can affect pickle compatibility; retrain both artifacts together if a version mismatch occurs. The direct run command starts Flask's local development server with debugging enabled.

## Project files

- `flask_app.py` - current Flask server, API, scoring logic, and routes.
- `train_better_model.ipynb` - commented training notebook.
- `data.csv` - local dataset used for retraining (not uploaded).
- `templates/landing.html` - landing page.
- `templates/index.html` - checker page.
- `requirements.txt` - dependencies.
- `requirements-dev.txt` - notebook development dependencies.
- `.github/workflows/checks.yml` - automated Python and notebook syntax checks.
