# Video preview design

## Intent

Datashare users should see a thumbnail for video documents, MOV (`video/quicktime`) included. Today every video is rejected as not previewable.

## Goals

- `/api/v1/thumbnail/{index}/{id}` returns a JPEG poster frame for videos.
- `/api/v1/thumbnail/{index}/{id}.json` reports `previewable: true` and `pages: 1` for videos.

## Non-goals

- Playing the video in the browser (no transcoding, no streaming route).
- Several frames per video.
- A separate size limit for videos: the existing `ds.document.max.size` (50 MB) applies, bigger videos get a 413 like any other document.

## Constraints

- `preview-generator` (`>=0.29,<0.30`) already ships `VideoPreviewBuilderFFMPEG`, which handles `video/quicktime`, `video/mp4`, `video/webm` and about 30 other video types.
- ffmpeg is already installed in the Docker image and by `make install_dependencies`.
- The only blocker is our allowlist `SUPPORTED_CONTENT_TYPES` in `dspreview/content_types.py`.

## Approaches

1. **Set `VideoPreviewBuilderFFMPEG.page_nb = 1` (picked).** One line. The library builds a new builder per call from this class attribute, so every video reports 1 page and every page resolves to the frame at 2% of the duration.
2. Override the page count in our code for `video/*` types. Leaves the library at 10 frames, so `page=5` would still return a different frame unless clamped too. More code for the same result.

Picked by Pierre: approach 1.

## Design

- `dspreview/content_types.py`: add the video types to `SUPPORTED_CONTENT_TYPES`.
- `dspreview/document.py`: `VideoPreviewBuilderFFMPEG.page_nb = 1` at import.
- Tests: a small MOV fixture in `tests/resources`, plus tests for the thumbnail and `.json` routes.

## Left to the builder

- Builder's call: take the video types from `VideoPreviewBuilderFFMPEG.get_supported_mimetypes()` instead of typing the list by hand, so the allowlist follows the library.
- Builder's call: generate the MOV fixture with ffmpeg (1 second, tiny resolution) to keep it a few KB.
