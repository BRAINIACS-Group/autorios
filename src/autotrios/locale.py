#STL import
import locale

locale.setlocale(locale.LC_ALL, '')

DECIMAL_SEPARATOR=locale.localeconv()["decimal_point"]  #"," #"."