# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "pysevsu"
copyright = "2026, linfer-developer"
author = "linfer-developer"
release = "0.1.0"
language = "ru"


# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

import os
import sys

sys.path.insert(0, os.path.abspath("../.."))

autodoc_default_options = {
    "members": True,  # Документировать все методы/функции
    "undoc-members": True,  # Включать функции без docstring
    "show-inheritance": True,  # Показывать базовые классы
    "member-order": "bysource",  # Сортировка по порядку в коде, а не по алфавиту
}
extensions = [
    "sphinx.ext.autodoc",  # Извлечение docstring из кода
    "sphinx.ext.napoleon",  # (Опционально) поддержка стилей Google/NumPy
    "sphinx.ext.viewcode",  # Ссылки на исходный код в HTML
    "docxbuilder",  # Генератор формата DOCX
    "sphinx_markdown_builder", # Для readme.md
]
templates_path = ["_templates"]
exclude_patterns = []
add_module_names = False

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
html_static_path = ["_static"]
