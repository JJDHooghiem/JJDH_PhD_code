import numpy as np


def table_init(header, file_object):
    header = """

    """
    pass


def any2str(val, prec):
    try:
        val = float(val)
        if prec==0 and np.round(val,prec)==0:
            val=0
        string = "%.{}f".format(prec) % val
    except ValueError:
        string = "%s" % val
    return string


def npa_to_tex_table(array, prec,  file_object, pre='', post=''):

    if isinstance(prec, int):
        a = [pre+any2str(i, prec)+post for i in array]
    if isinstance(prec, np.ndarray):
        if isinstance(pre, str):
            pre = ['']*len(prec)
        if isinstance(post, str):
            post = ['']*len(prec)
        a = [pr+any2str(i, p)+po for i, p, pr,
             po in zip(array, prec, pre, post)]
    a = " & ".join(a)
    a += "\\\\\n"
    file_object.write(a)
    return
