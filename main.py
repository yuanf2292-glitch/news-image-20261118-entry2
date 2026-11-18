"""news-image-20261118 entry: validated, chunked copy of the finished artwork.

The artwork (entry.png, "The World in One Page - Wednesday 18 November
2026") is a fixed, pre-made image that lives in this same directory. The
program copies it byte-for-byte to the output directory, but only after
proving the source is a real, in-limits image, and it checks the copy
afterwards by size and by hash.

The artwork is JPEG bytes under the name entry.png: the competition tells
PNG and JPEG apart by their first bytes and keeps the name entry.png either
way, so this program accepts both.

What is checked, in order:
  1. The source is at most 1 MiB (1_048_576 bytes); otherwise refuse.
  2. The first bytes are the PNG signature or the JPEG start-of-image
     marker; anything else is refused.
  3. The image header declares a width and height, each greater than 0
     and at most 1024 px; for PNG that is the IHDR chunk, for JPEG the
     first start-of-frame segment.
  4. The copy is written in 64 KiB blocks (the whole file is never held
     in memory), then the destination is re-read: its size must equal the
     source size and its SHA-256 must equal the source SHA-256. On any
     mismatch the output is deleted and the run fails.

Standard library only, no network, deterministic. A failed check writes
nothing and exits non-zero; a bad input never produces a silent output.
"""

import hashlib
import os
import struct

IMAGE_NAME = "entry.png"
SIZE_LIMIT = 1_048_576         # 1 MiB
DIM_LIMIT = 1024               # px, width and height
BLOCK = 65_536                 # 64 KiB
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
JPEG_MAGIC = b"\xff\xd8\xff"


def _digest(path):
    """SHA-256 of a file, streamed in BLOCK-sized pieces."""
    total = hashlib.sha256()
    with open(path, "rb") as handle:
        while True:
            piece = handle.read(BLOCK)
            if not piece:
                break
            total.update(piece)
    return total.hexdigest()


def _png_size(head):
    """(width, height) from a 33-byte PNG prefix, or raise ValueError."""
    chunk_len, chunk_kind = struct.unpack(">I4s", head[8:16])
    if chunk_kind != b"IHDR" or chunk_len != 13:
        raise ValueError("entry.png first chunk is not a 13-byte IHDR")
    width, height = struct.unpack(">II", head[16:24])
    return width, height


def _jpeg_size(handle):
    """(width, height) from the first JPEG start-of-frame segment.

    Scans marker by marker, tolerating the 0xFF fill bytes a real encoder
    may put between segments. A start-of-frame segment always precedes
    the entropy data, so the scan never has to look inside it.
    """
    while True:
        byte = handle.read(1)
        if not byte:
            raise ValueError("entry.png JPEG stream has no SOF segment")
        if byte != b"\xff":
            continue  # stray byte before a marker; keep scanning
        code_byte = handle.read(1)
        if not code_byte:
            raise ValueError("entry.png JPEG stream ends mid-marker")
        code = code_byte[0]
        if code == 0xFF:
            continue  # fill byte: another 0xFF follows the marker prefix
        if code in (0xD8, 0xD9) or 0xD0 <= code <= 0xD7:
            continue  # SOI, EOI, RSTn: no length field follows
        raw_len = handle.read(2)
        if len(raw_len) < 2:
            raise ValueError("entry.png JPEG stream ends mid-segment")
        (seg_len,) = struct.unpack(">H", raw_len)
        if seg_len < 2:
            raise ValueError("entry.png JPEG segment length is invalid")
        if 0xC0 <= code <= 0xCF and code not in (0xC4, 0xC8, 0xCC):
            body = handle.read(5)
            if len(body) < 5:
                raise ValueError("entry.png JPEG SOF segment is truncated")
            height, width = struct.unpack(">xHH", body)
            return width, height
        handle.seek(seg_len - 2, os.SEEK_CUR)


def _probe_image(path):
    """Check the source image against every gate.

    Returns (kind, size, width, height); raises ValueError on any failure.
    """
    size = os.path.getsize(path)
    if size > SIZE_LIMIT:
        raise ValueError(
            f"entry.png is {size} bytes, over the {SIZE_LIMIT} byte limit"
        )
    if size < 33:
        raise ValueError("entry.png is too small to hold an image header")
    with open(path, "rb") as handle:
        head = handle.read(33)
        if head[:8] == PNG_MAGIC:
            kind = "PNG"
            width, height = _png_size(head)
        elif head[:3] == JPEG_MAGIC:
            kind = "JPEG"
            handle.seek(0)
            width, height = _jpeg_size(handle)
        else:
            raise ValueError(
                "entry.png starts with neither the PNG signature nor "
                "the JPEG start-of-image marker"
            )
    if width == 0 or height == 0:
        raise ValueError("entry.png has a zero dimension")
    if width > DIM_LIMIT or height > DIM_LIMIT:
        raise ValueError(
            f"entry.png is {width}x{height}, over the "
            f"{DIM_LIMIT}x{DIM_LIMIT} limit"
        )
    return kind, size, width, height


def _copy_checked(src, dst):
    """Copy src to dst in blocks, then verify size and hash. Returns the hash."""
    want_hash = _digest(src)
    with open(src, "rb") as src_handle, open(dst, "wb") as dst_handle:
        while True:
            piece = src_handle.read(BLOCK)
            if not piece:
                break
            dst_handle.write(piece)
    got_size = os.path.getsize(dst)
    want_size = os.path.getsize(src)
    if got_size != want_size:
        os.remove(dst)
        raise SystemExit(
            f"copy verification failed: destination is {got_size} bytes, "
            f"source is {want_size}"
        )
    got_hash = _digest(dst)
    if got_hash != want_hash:
        os.remove(dst)
        raise SystemExit(
            "copy verification failed: destination sha256 "
            f"{got_hash} != source {want_hash}"
        )
    return got_hash


def run():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, IMAGE_NAME)
    kind, size, width, height = _probe_image(src)

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, IMAGE_NAME)

    sha = _copy_checked(src, dst)
    print(
        f"wrote {dst} ({kind}, {size} bytes, {width}x{height}, "
        f"sha256 {sha})"
    )


if __name__ == "__main__":
    run()
