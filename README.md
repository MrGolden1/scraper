This python script scrapes the data from the website https://www.elsevier.com/search-results?labels=journals&in-publication=true and outputs journals that have "Your paper Your way" option int their `Guide for Authors` section.

## Usage

```shell
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python script.py
```

You can find the output in the `results.xlsx` file.
