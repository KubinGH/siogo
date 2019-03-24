import os
import itertools

try:
    import texttable
except ImportError:
    pass

def grouper(iterable, n, fillvalue=None):
    args = [iter(iterable)] * n
    return itertools.zip_longest(*args, fillvalue=fillvalue)

def table_formatted_list(elements):
    columns = os.get_terminal_size().columns
    t_columns = 30
    n = max(1, columns // t_columns)
    table = texttable.Texttable(max_width=columns - 2)
    table.set_cols_align(["l"] * n)
    table.set_cols_width([t_columns - 4] * n)
    rows = [list(g) for g in grouper(elements, n, fillvalue="")]
    table.add_rows(rows, header=False)
    return table.draw()
