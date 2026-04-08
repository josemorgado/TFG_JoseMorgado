"""Detecta palabras ofensivas en el texto."""

import re
import unicodedata

# Lista base de palabras ofensivas

PALABRAS_PROHIBIDAS = {
    # Vulgaridades explícitas
    "mierd",
    "coñ",
    "put",
    "jod",
    "cag",
    "cul",
    # Insultos personales directos
    "gilipoll",
    "imbecil",
    "cabron",
    "subnormal",
    "mongol",
    "tonto",
    # Desprecio explícito
    "asqueros",
    "basur",
    "escori",
    # Expresiones prohibidas
    "hijo de",
    "vete a",
    "me cago en",
    "que te den",
}


def normalizar_texto(texto: str) -> str:
    texto = texto.lower()
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    return texto


def contiene_lenguaje_ofensivo(texto: str) -> bool:
    texto = normalizar_texto(texto)

    for raiz in PALABRAS_PROHIBIDAS:
        if re.search(rf"\b{re.escape(raiz)}\w*\b", texto):
            return True

    return False
