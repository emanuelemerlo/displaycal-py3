"""Tests for the DisplayCAL.jspacker module."""

import pytest

from DisplayCAL.jspacker import JavaScriptPacker

COMMENTS_AND_WHITESPACE_SRC = r"""// ----------------------------------------------------------------------
// public interface
// -----------------------------------------------------------------------

cssQuery.toString = function() {
    return "function cssQuery() {\n  [version " + version + "]\n}";
};"""

LOCAL_VARS_SRC = """function test(_localvar) {
    var $name = 'foo';
    var $$dummy = 2;

    return $name + $$dummy;
}"""

PRIVATE_NAMES_SRC = """function _test($localvar) {
    var $name = 1;
    var _dummy = 2;
    var __foo = 3;

    return $name + _dummy + $localvar + __foo;
}"""

PRIVATE_NAMES_TWO_FUNCTIONS_SRC = (
    PRIVATE_NAMES_SRC
    + """

function _bar(_ocalvar) {
    var $name = 1;
    var _dummy = 2;
    var __foo = 3;

    return $name + _dummy + $localvar + __foo;
}"""
)


@pytest.mark.parametrize(
    ("script", "encoding", "fast_decode", "special_chars", "expected"),
    [
        pytest.param(
            COMMENTS_AND_WHITESPACE_SRC,
            0,
            False,
            False,
            r'cssQuery.toString=function(){return"function cssQuery() {\n  '
            r'[version "+version+"]\n}"};',
            id="strips-comments-keeps-string-literals",
        ),
        pytest.param(
            LOCAL_VARS_SRC,
            0,
            False,
            True,
            "function test(_0){var n='foo';var du=2;return n+du}",
            id="shrinks-dollar-variables",
        ),
        pytest.param(
            PRIVATE_NAMES_SRC,
            0,
            False,
            True,
            "function _1(l){var n=1;var _0=2;var __foo=3;return n+_0+l+__foo}",
            id="encodes-private-names",
        ),
        pytest.param(
            PRIVATE_NAMES_TWO_FUNCTIONS_SRC,
            0,
            False,
            True,
            "function _3(l){var n=1;var _0=2;var __foo=3;return n+_0+l+__foo}"
            "function _2(_1){var n=1;var _0=2;var __foo=3;return n+_0+l+__foo}",
            id="encodes-private-names-across-functions",
        ),
    ],
)
def test_pack(script, encoding, fast_decode, special_chars, expected):
    """JavaScriptPacker.pack() produces the expected minified output."""
    packer = JavaScriptPacker()
    assert packer.pack(script, encoding, fast_decode, special_chars) == expected


@pytest.mark.parametrize("encoding", [10, 62, 95])
def test_pack_encoded_output_is_self_extracting(encoding):
    """Base-N encoded output is wrapped in the self-extracting eval() decoder."""
    packer = JavaScriptPacker()
    result = packer.pack("function test(a){var b=1;return a+b}", encoding, True, False)
    assert result.startswith("eval(function(p,a,c,k,e,d){")
