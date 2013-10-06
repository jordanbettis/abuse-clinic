
def test_failure():
    """ Test that always fails """
    raise KeyError("foo")

def test_math_failure():
    """ Always fails slightly differently """
    assert 2 + 3 == 1, "What strange math we have."

def test_success():
    """ Test that always succeeds """
    pass

def test_return_success():
    """ Let's return something """
    return ["This is an object"]

def test_print_success():
    """ Print something but don't fail """
    pass

def assay_other_name():
    """ This is a test without the 'test_' prefix """
