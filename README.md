# face recognition flask application

## development enviornment setup

create a virtual env

```bash
python3.8 -m venv myvenv
python -m venv myvenv

```

Activate the virtual environment.

```bash
source myvenv/bin/activate
```

install reuirements

```bash
pip install -r requirements/flasks.txt
pip install -r requirements/fr.txt
```

### run the application

```bash
flask run --host=0.0.0.0 --port=5000
```