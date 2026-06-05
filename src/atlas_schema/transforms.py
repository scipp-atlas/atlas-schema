"""Form-transform helpers for vector coordinate materialization.

Tries to use coffea's built-in implementations first (available in coffea >=
2026.5.0). Falls back to local copies for older versions, and patches them into
``coffea.nanoevents.transforms`` so the coffea mapping dispatcher can find the
runtime functions via the ``!full_like_from_content`` form-key token.
"""

from __future__ import annotations

try:
    from coffea.nanoevents.transforms import (
        full_like_from_content,
        full_like_from_content_form,
    )
except ImportError:
    import copy

    import awkward
    from coffea.nanoevents import transforms as _coffea_transforms
    from coffea.nanoevents.util import concat

    def full_like_from_content_form(source_form: dict, fill_value: float) -> dict:
        form = copy.deepcopy(source_form)
        if not (
            form["class"] == "NumpyArray" or form["class"].startswith("ListOffset")
        ):
            raise RuntimeError
        if form["class"] == "NumpyArray":
            form["form_key"] = concat(
                source_form["form_key"], f"{fill_value},!full_like_from_content"
            )
            form["parameters"].pop("__doc__", None)
        elif form["class"].startswith("ListOffset"):
            form["content"]["form_key"] = concat(
                source_form["form_key"],
                f"{fill_value},!full_like_from_content",
                "!content",
            )
            form["parameters"].pop("__doc__", None)
            form["content"]["parameters"].pop("__doc__", None)
        return form

    def full_like_from_content(stack: list) -> None:
        fill_value = float(stack.pop())
        source = stack.pop()
        stack.append(awkward.full_like(source, fill_value))

    # Register with coffea's transforms module so the mapping dispatcher finds
    # the runtime function when decoding !full_like_from_content form-key tokens.
    _coffea_transforms.full_like_from_content_form = full_like_from_content_form
    _coffea_transforms.full_like_from_content = full_like_from_content

__all__ = ["full_like_from_content", "full_like_from_content_form"]
