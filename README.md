# Visual Kopasu

Visko (Visual-kopasu) is a web-based software suite for Computational Linguistic Analysis based on deep parsing with construction grammars and ontologies (HPSG, SBCG, xMRS, Wordnet, texttaglib).

## Install

`visko` is available on [PyPI](https://pypi.org/project/visko/) and can be installed with pip

```bash
pip install visko
```

1. Visko requires [coolisf](https://pypi.org/project/coolisf/) library in order to function.
   Please follow installation instructions at https://pypi.org/project/coolisf/
2. Visko is a Django site. To run Visko locally, please download the pre-packaged `visko_site.tar.gz` from a [compatible release here](https://github.com/letuananh/visualkopasu/releases) and unzip it to a local folder. To start the development server use:
   ```bash
   python manage.py runserver
   ```
   and Visko should be ready at http://localhost:8000

## Useful link

- Open Science Framework project page: https://osf.io/9udjk/
- Visko documentation: https://visko.readthedocs.io/
- Source code: https://github.com/letuananh/visualkopasu
- PyPI: https://pypi.org/project/visko/
