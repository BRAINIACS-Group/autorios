# -----------------------------------------------------------------------------
#
# SPDX-License-Identifier: MIT
#
# This file is part of the autorios project
#
# Detailed license information can be found in LICENSE
# at the top level directory.
#
# -----------------------------------------------------------------------------


#STL import
import locale

locale.setlocale(locale.LC_ALL, '')

DECIMAL_SEPARATOR=locale.localeconv()["decimal_point"]  #"," #"."