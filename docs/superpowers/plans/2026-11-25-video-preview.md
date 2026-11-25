# Video Preview Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Serve a single JPEG poster frame for video documents, MOV included.

**Architecture:** `preview-generator` already ships `VideoPreviewBuilderFFMPEG`. We allow its mimetypes in our allowlist and set its `page_nb` class attribute to 1, so every video has one page: the frame at 2% of its duration.

**Tech Stack:** Python, FastAPI, preview-generator 0.29 (ffmpeg builder), pytest + respx.

**Spec:** `docs/superpowers/specs/2026-11-25-video-preview-design.md`

## Global Constraints

- No new dependency: ffmpeg is already in `Dockerfile:15` and `Makefile:11`.
- Size limit unchanged: `ds.document.max.size = 50000000`.
- Tests run in the Docker image: `docker build -q -t dspreview-test . && docker run --rm -u root -e CACHE_PATH=/tmp dspreview-test sh -c "pip install -q pytest respx && python -m pytest -q <target>"`.

## Review Focus

1. A MOV request for `page=3` returns the same poster frame, not a 415 or a different frame (covered by `test_video_thumbnail_any_page_is_poster_frame`).
2. A file labelled `video/*` but without a video stream raises `NoVideoStream`, which is not in `NOT_PREVIEWABLE_ERRORS` and would return a 500. Not covered by a test, flagged as a follow-up.

---

### Task 1: Video poster frame

**Files:**
- Create: `tests/resources/dummy.mov`, `tests/resources/dummy.mp4`
- Modify: `dspreview/content_types.py` (`SUPPORTED_CONTENT_TYPES`)
- Modify: `dspreview/document.py` (imports, module level)
- Test: `tests/test_content_types.py`

**Interfaces:**
- Consumes: `VideoPreviewBuilderFFMPEG` from `preview_generator.preview.builder.video__ffmpeg`.
- Produces: nothing other tasks use.

- [ ] **Step 1: Generate fixtures** (inside the image, ffmpeg is not in the dev container)

`docker run --rm -u root -v $PWD/tests/resources:/out dspreview-test sh -c "ffmpeg -f lavfi -i testsrc=duration=1:size=64x48:rate=10 -pix_fmt yuv420p /out/dummy.mov && ffmpeg -f lavfi -i testsrc=duration=1:size=64x48:rate=10 -pix_fmt yuv420p /out/dummy.mp4"`
Expected: two files of a few KB.

- [ ] **Step 2: Write the failing tests** in `tests/test_content_types.py`

Add `VIDEO_CONTENT_TYPES = {'video/quicktime': 'dummy.mov', 'video/mp4': 'dummy.mp4'}` and merge it into `all_content_types` in `test_thumbnail`. Add:

```python
@respx.mock
def test_video_info_has_one_page(self):
    for content_type, resource_name in VIDEO_CONTENT_TYPES.items():
        with self.subTest(content_type=content_type):
            document_id = self.mock_document(resource_name, content_type)
            response = self.client.get(f'/api/v1/thumbnail/my-index/{document_id}.json', headers=auth_headers())
            self.assertEqual(response.json().get('previewable'), True)
            self.assertEqual(response.json().get('pages'), 1)

@respx.mock
def test_video_thumbnail_any_page_is_poster_frame(self):
    document_id = self.mock_document('dummy.mov', 'video/quicktime')
    first = self.client.get(f'/api/v1/thumbnail/my-index/{document_id}?page=0', headers=auth_headers())
    other = self.client.get(f'/api/v1/thumbnail/my-index/{document_id}?page=3', headers=auth_headers())
    self.assertEqual(other.status_code, 200)
    self.assertEqual(other.content, first.content)
```

- [ ] **Step 3: Run tests to verify they fail**

Run the Docker test command with `tests/test_content_types.py`.
Expected: FAIL, videos return 415 / `previewable: False`.

- [ ] **Step 4: Implement**

- `content_types.py`: append `*VideoPreviewBuilderFFMPEG.get_supported_mimetypes()` to `SUPPORTED_CONTENT_TYPES`.
- `document.py`: `VideoPreviewBuilderFFMPEG.page_nb = 1` right after the imports.

- [ ] **Step 5: Run the full suite to verify it passes**

Run the Docker test command without target.
Expected: all PASS.

- [ ] **Step 6: Commit** through the `icij:commit` skill, message `feat: preview video documents with a poster frame`.
