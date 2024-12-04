import locale

locale.setlocale(locale.LC_ALL, '')
print("decimal_point:", locale.localeconv()["decimal_point"])