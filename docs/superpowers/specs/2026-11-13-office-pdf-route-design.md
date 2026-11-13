# Serve office documents as PDF

## Intent

Datashare's View tab has no proper viewer for several office formats (doc, ppt, odt, rtf...). The preview server already converts these to PDF with LibreOffice to build thumbnails. Serving that PDF lets the client open them in its pdf.js viewer, with selectable text, local search and highlights.

## Goals

- `GET /api/v1/pdf/{index}/{id}?routing=...` returns the whole document as `application/pdf`.
- Accepted types (the "common set"):
  - `application/msword` (doc)
  - `application/vnd.ms-powerpoint` (ppt)
  - `application/vnd.openxmlformats-officedocument.presentationml.presentation` (pptx)
  - `application/vnd.ms-powerpoint.presentation.macroEnabled.12` (pptm)
  - `application/vnd.openxmlformats-officedocument.presentationml.slideshow` (ppsx)
  - `application/vnd.oasis.opendocument.text` (odt)
  - `application/vnd.oasis.opendocument.presentation` (odp)
  - `application/rtf` and `text/rtf` (rtf)
- These types are also added to `SUPPORTED_CONTENT_TYPES`, so the thumbnail and `.json` routes work for them too. This fixes the client's paginated viewer for doc and pptx, which the server currently rejects.

## Non-goals

- docx: the client keeps its own docx viewer.
- Spreadsheets: they keep the spreadsheet viewer.
- Any other LibreOffice type (legacy sxw, templates, odg...).
- The client change that points `DocumentViewerPdf` at this route (it lives in datashare-client).

## Approaches

1. **New `/api/v1/pdf` route (picked).** One job per route, and the URL is exactly what pdf.js loads.
2. `?format=pdf` on the thumbnail route. Rejected: one route would return either a JPEG or a full PDF, and `page` and `size` would be ignored in PDF mode.
3. Convert to PDF at download time. Rejected: every first request would get slower, even for a thumbnail.

## Design

- Same flow as the thumbnail route: download meta, check authorization and size, download the source, then call `PreviewManager.get_pdf_preview(file_path, page=-1)`. The manager caches the result in the thumbnail directory, so the existing cache purge cleans it up.
- Errors match the thumbnail route: 400 unsafe identifier, 401 unauthorized, 413 too big / root too big, 415 not previewable.
- Calls I made:
  - A type that is previewable but not in the PDF set (e.g. a JPEG, or a PDF itself) gets a 415 on this route. The client already reads real PDFs from Datashare directly.
  - A LibreOffice timeout (`TimeoutExpired`) gets a 415 and the target directory is deleted, the same way the `.json` route handles it.

## Left to the builder

- Test fixtures: a small `.odt` (or `.doc`) in `tests/resources`, mocked Datashare responses with respx as in `tests/test_thumbnail.py`.
