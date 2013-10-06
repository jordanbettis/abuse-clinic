
import abuse_clinic
import os
import imp
import sys

# This assumes we're running from the root directory of the
# abuse-clinic package
MOCK_DIR = os.path.join('test', 'mock_tests')

def make_argv(*args, **kwargs):
    """
    This creates an argv line based on the args passed in. Each should
    be a string forming one argument element.

    We automatically append the default mock_test location unless the
    keyword argument loc is used to override it.
    """
    if "loc" in kwargs.keys():
        mock_dir = kwargs['loc']
    else:
        mock_dir = os.path.join(MOCK_DIR, 'main')

    return ['test-ac'] + list(args) + [mock_dir]


def make_subdir(path):
    """ Shortcut to make paths to subdirectories of MOCK_DIR """
    return os.path.join(MOCK_DIR, path)


def is_in(name, section):
    """
    This ensures that the named test is in the given section of the
    result object.
    """
    return len([x for x in section if x[1].name == name]) == 1


def test_exit_status():
    """
    Check that the exit status returns properly.
    """
    (status, output, result) = abuse_clinic.main(
        make_argv("-i", ".*failure", "-vv"))
    print(output)
    assert status != 0, \
        "Test failure failed to produce nonzero exit status"
    (status, output, result) = abuse_clinic.main(
        make_argv("-i", ".*success", "-vv"))
    print(output)
    assert status == 0, \
        "Test success failed to produce nonzero exit status"


def test_dry_run():
    """ Check that dry run makes all tests succeed """
    (status, output, result) = abuse_clinic.main(make_argv("-d"))
    assert len(result.tests_failed) == 0, "Dry run didn't succeed all tests."


def test_verbosity():
    """ Make sure verbosity levels work """
    (status, output, result) = abuse_clinic.main(make_argv())
    assert "TEST RUN DETAILS" not in output, "zero verbosity has details"
    assert "STATISTICS" not in output, "zero verbosity has statistics"

    (status, output, result) = abuse_clinic.main(make_argv("-v"))
    assert "TEST RUN DETAILS" not in output, "one verbosity has details"
    assert "STATISTICS" in output, "one verbosity lacks statistics"

    (status, output, result) = abuse_clinic.main(make_argv("-vv"))
    assert "TEST RUN DETAILS" in output, "two verbosity lacks details"
    assert "STATISTICS" in output, "two verbosity lacks statistics"


def test_paths():
    """
    Verify adding directories to the path with '-p'
    """
    (status, output, result) = abuse_clinic.main(make_argv())
    assert is_in('test_try_import_one', result.tests_failed), \
        "import_one not failed for no args"
    assert is_in('test_try_import_two', result.tests_failed), \
        "import_two not failed for no args"

    (status, output, result) = abuse_clinic.main(make_argv(
            "-p", os.path.join(MOCK_DIR, "import_dir1")))

    assert is_in('test_try_import_one', result.tests_succeeded), \
        "import_one not succeeded for one arg"
    assert is_in('test_try_import_two', result.tests_failed), \
        "import_two not failed for one arg"

    (status, output, result) = abuse_clinic.main(make_argv(
            "-p", os.path.join(MOCK_DIR, "import_dir1"),
            "-p", os.path.join(MOCK_DIR, "import_dir2")))

    assert is_in('test_try_import_one', result.tests_succeeded), \
        "import_one not succeeded for two args"
    assert is_in('test_try_import_two', result.tests_succeeded), \
        "import_two not succeeded for two args"


def test_trace():
    """
    Verify that traces are getting printed with -t
    """
    (status, output, result) = abuse_clinic.main(make_argv())
    assert "Traceback" not in output, "traceback exists without -t"
    (status, output, result) = abuse_clinic.main(make_argv("-t"))
    assert "Traceback" in output, "traceback doesn't exist with -t"


def test_symlinks():
    """
    This tests following symlinks while recursing through directories
    with -f
    """
    (status, output, result) = abuse_clinic.main(
        make_argv(loc=make_subdir("subdir_direct")))
    assert len(result.modules) == 0, "modules not empty for no follow"
    (status, output, result) = abuse_clinic.main(
        make_argv("-vvf", loc=make_subdir("subdir_direct")))
    print(output)
    assert len(result.modules) == 1, "modules unexpected size for follow"


def test_test_prefix():
    """ Verify the test prefix -x option """
    (status, output, result) = abuse_clinic.main(make_argv())
    assert not is_in("assay_other_name", result.tests_succeeded), \
        "assay test found with default -x switch"

    (status, output, result) = abuse_clinic.main(make_argv("-x", "assay_"))
    assert is_in("assay_other_name", result.tests_succeeded), \
        "assay test not found with default -x switch"


def test_module_prefix():
    """ Verify the module prefix -X option """
    (status, output, result) = abuse_clinic.main(make_argv())
    assert not is_in("test_in_assay_module", result.tests_succeeded), \
        "in_assay_module found with default -X switch"

    (status, output, result) = abuse_clinic.main(make_argv("-X", "assay_"))
    assert is_in("test_in_assay_module", result.tests_succeeded), \
        "in_assay_module not found with -X assay_"


def test_test_exclude():
    """ Verify the test exclude -e option """
    (status, output, result) = abuse_clinic.main(make_argv())
    assert is_in("test_math_failure", result.tests_failed), \
        "math_failure not in result without -e"
    assert not is_in("test_math_failure", result.tests_skipped), \
        "math_failure in tests_skipped without -e"

    (status, output, result) = abuse_clinic.main(make_argv("-vv", "-e", "math"))
    assert not is_in("test_math_failure", result.tests_failed), \
        "math_failure in result with -e"
    assert is_in("test_math_failure", result.tests_skipped), \
        "math_failure not in tests_skipped without -e"
    assert "TESTS SKIPPED (matched -e)" in output, "no test run description"
    assert "Tests skipped (matched -e)" in output, "no stats listing"


def test_module_exclude():
    """ Verify the test exclude -E option """
    (status, output, result) = abuse_clinic.main(make_argv("-vv"))
    assert len(result.modules_skipped) == 0, \
        "module excluded with default args"
    assert len([x for x in result.modules if x.name == "test_import"]) == 1, \
        "test_import not in module list"
    print(output)

    (status, output, result) = abuse_clinic.main(
        make_argv("-vv", "-E", "import"))
    assert len(result.modules_skipped) == 1, \
        "module not excluded with -E"
    print(output)
    assert "MODULES SKIPPED (matched -E)" in output, "skip not in details"
    assert "Test modules skipped (matched -E)" in output, "skip not in stats"
    assert result.modules_skipped[0][0].name == "test_import", \
        "test_import not in module skipped list"


def test_test_include():
    """ Verify the test exclude -i option """
    (status, output, result) = abuse_clinic.main(make_argv())
    assert is_in("test_math_failure", result.tests_failed), \
        "math_failure not in result without -i"
    assert not is_in("test_math_failure", result.tests_skipped), \
        "math_failure in tests_skipped without -i"

    (status, output, result) = abuse_clinic.main(
        make_argv("-vv", "-i", ".*success"))
    assert not is_in("test_math_failure", result.tests_failed), \
        "math_failure in result with -e"
    print(output)
    assert is_in("test_math_failure", result.tests_skipped), \
        "math_failure not in tests_skipped without -e"
    assert "TESTS SKIPPED (failed to match -i)" in output, \
        "no test run description"
    assert "Tests skipped (failed to match -i)" in output, "no stats listing"


def test_module_include():
    """ Verify the test exclude -I option """
    (status, output, result) = abuse_clinic.main(make_argv("-vv"))
    assert len(result.modules_skipped) == 0, \
        "module excluded with default args"
    assert len([x for x in result.modules if x.name == "test_import"]) == 1, \
        "test_main not in module list"

    (status, output, result) = abuse_clinic.main(
        make_argv("-vv", "-I", "import"))
    print(output)
    assert len(result.modules_skipped) == 1, "module not excluded with -I"
    assert "MODULES SKIPPED (failed to match -I)" in output, \
        "skip not in details"
    assert "Test modules skipped (failed to match -I)" in output, \
        "skip not in stats"
    assert result.modules_skipped[0][0].name == "test_main", \
        "test_main not in module skipped list"
