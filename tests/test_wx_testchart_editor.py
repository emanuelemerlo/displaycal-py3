"""Tests for the wx testchart editor (DisplayCAL.wx_testchart_editor)."""

from unittest import mock


def test_alternate_preview_builds(setup_argyll):
    """The editor opens with --alternate-preview (-ap).

    This used to fail with a TypeError in get_gradient_panel() (ord() applied
    to an int) and a NameError for the undefined ``grid_cls`` preview grid.
    """
    import wx

    from DisplayCAL import wx_testchart_editor
    from DisplayCAL.config import initcfg

    initcfg()
    app = wx.GetApp() or wx.App()  # noqa: F841

    with mock.patch.object(wx_testchart_editor, "TC_USE_ALTERNATE_PREVIEW", True):
        editor = wx_testchart_editor.TestchartEditor()
    try:
        assert isinstance(editor.preview, wx.grid.Grid)
    finally:
        editor.Destroy()


def test_gradient_panel_bitmap_is_brightened():
    """get_gradient_panel() scales the gradient bitmap without errors."""
    import wx

    from DisplayCAL.config import initcfg
    from DisplayCAL.wx_windows import bitmaps, get_gradient_panel

    initcfg()
    app = wx.GetApp() or wx.App()  # noqa: F841

    frame = wx.Frame(None)
    try:
        bitmaps.pop("gradient_panel", None)
        panel = get_gradient_panel(frame, "Preview")
        assert panel.GetLabel() == "Preview"
        assert bitmaps["gradient_panel"].IsOk()
    finally:
        frame.Destroy()
