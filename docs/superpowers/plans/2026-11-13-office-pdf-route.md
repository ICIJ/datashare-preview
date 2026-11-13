# Office Documents PDF Route Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Serve common office documents as a full PDF on `GET /api/v1/pdf/{index}/{id}` so the Datashare client can open them in its pdf.js viewer.

**Architecture:** A new FastAPI route reuses the existing meta download, authorization, size checks and document download, then calls `PreviewManager.get_pdf_preview` (LibreOffice, cached in the thumbnail directory). The office types are also added to the global whitelist so thumbnails and page counts work for them.

**Tech Stack:** Python, FastAPI, preview-generator 0.29 (LibreOffice builder), pytest + respx.

**Spec:** `docs/superpowers/specs/2026-11-13-office-pdf-route-design.md`

## Global Constraints

- Route path: `/api/v1/pdf/{index}/{id}`, optional `routing` query param, response `Content-Type: application/pdf`.
- PDF set (exact MIME strings): `application/msword`, `application/vnd.ms-powerpoint`, `application/vnd.openxmlformats-officedocument.presentationml.presentation`, `application/vnd.ms-powerpoint.presentation.macroEnabled.12`, `application/vnd.openxmlformats-officedocument.presentationml.slideshow`, `application/vnd.oasis.opendocument.text`, `application/vnd.oasis.opendocument.presentation`, `application/rtf`, `text/rtf`.
- Not in the set: docx, spreadsheets, anything else. Those get 415 on the PDF route.
- Status codes: 400 unsafe identifier, 401 unauthorized, 413 too big / root too big, 415 not previewable or LibreOffice timeout.
- No new dependency.
- Tests that convert need LibreOffice. It is not installed in the dev container. Run tests in the project image:
  `docker build -q -t dspreview-test . && docker run --rm -u root dspreview-test sh -c "pip install -q pytest respx && python -m pytest <target> -v"`
  (`.dockerignore` keeps `tests/`; rebuild before every run since the code is copied in.)

## Review Focus

1. A JPEG (or real PDF) requested on `/api/v1/pdf` gets 415 and must NOT delete its cached download (the thumbnail route still uses it). Test in Task 2.
2. pdf.js sends the session as the `X-Ds-Session-Id` header, not a cookie: the route must accept header auth. Test in Task 2.
3. Embedded document whose root is too big: 413, same as the thumbnail route. Test in Task 2.
4. LibreOffice timeout (`subprocess.TimeoutExpired`): 415 and the target directory removed, not a 500. Test in Task 2.
5. Path traversal in `routing`: 400. Test in Task 2.

---

### Task 1: Whitelist the office types (thumbnails and page count)

**Files:**
- Create: `tests/resources/dummy.odt`
- Create: `tests/test_pdf.py`
- Modify: `dspreview/content_types.py`

**Interfaces:**
- Produces: `PDF_CONTENT_TYPES: tuple[str, ...]` in `dspreview/content_types.py` (the 9 MIME strings above); `SUPPORTED_CONTENT_TYPES` includes all of them.

- [ ] **Step 1: Create the fixture**

A one-page ODT containing the text `Hello Datashare`. Generate it inside the image (no LibreOffice locally), e.g. `docker run --rm -u root dspreview-test sh -c "echo 'Hello Datashare' > /tmp/d.txt && cd /tmp && soffice --headless --convert-to odt d.txt >/dev/null && base64 -w0 d.odt"`, then decode into `tests/resources/dummy.odt`.

- [ ] **Step 2: Write the failing test**

In `tests/test_pdf.py`, class `PdfTest(AbstractTest)` with
`_source = {"contentType": "application/vnd.oasis.opendocument.text", "path": "dummy.odt", "contentLength": <fixture size>}`
and `document_url` helper copied from `ThumbnailTest`.

```python
@respx.mock
def test_info_json_for_odt(self):
    respx.get(self.document_url('my-index', 'id-for-dummy-odt')).mock(return_value=Response(200, json={'_source': self._source}))
    create_file_ondisk_from_resource('dummy.odt', '/tmp/documents/my-index/id-for-dummy-odt/raw.odt')
    response = self.client.get('/api/v1/thumbnail/my-index/id-for-dummy-odt.json', headers=auth_headers())
    self.assertEqual(response.status_code, 200)
    self.assertTrue(response.json()['previewable'])
    self.assertEqual(response.json()['pages'], 1)
```

- [ ] **Step 3: Run it, verify it fails**

Run the docker command with `tests/test_pdf.py::PdfTest::test_info_json_for_odt`.
Expected: FAIL, `previewable` is False (type not whitelisted). Show this output to Pierre.

- [ ] **Step 4: Add `PDF_CONTENT_TYPES` and append it to `SUPPORTED_CONTENT_TYPES`**

- [ ] **Step 5: Run it, verify it passes**, then run the whole suite in the image: all green.

- [ ] **Step 6: Commit** `feat: preview common office documents`

---

### Task 2: `/api/v1/pdf` route

**Files:**
- Modify: `dspreview/document.py` (new method)
- Modify: `dspreview/main.py` (new route)
- Test: `tests/test_pdf.py`

**Interfaces:**
- Consumes: `PDF_CONTENT_TYPES` from Task 1.
- Produces:
  - `Document.get_pdf_preview(self) -> str`: `self.manager.get_pdf_preview(file_path=self.target_path, page=-1)`.
  - `GET /api/v1/pdf/{index}/{id}` in `main.py`.

- [ ] **Step 1: Write the failing tests** (all in `PdfTest`)

```python
def test_pdf_for_odt(self):            # mock meta + src download (bytes of dummy.odt), rmtree target dir first
    # 200, headers['Content-Type'] == 'application/pdf', response.content.startswith(b'%PDF')

def test_pdf_with_session_header(self): # same as above but headers={'X-Ds-Session-Id': '<auth cookie value>'}, no cookie
    # 200

def test_pdf_rejects_jpeg_and_keeps_cache(self):  # meta contentType image/jpeg, dummy.jpg already on disk at raw.jpg
    # 415, os.path.exists('/tmp/documents/my-index/id-jpg-on-pdf/raw.jpg') is True

def test_pdf_unauthorized(self):        # meta returns 401
    # 401

def test_pdf_root_too_big(self):        # routing=rooting-id, root contentLength 60000000
    # 413

def test_pdf_timeout(self):             # patch.object(Document, 'get_pdf_preview', side_effect=TimeoutExpired('soffice', 60)), file on disk
    # 415, target dir no longer exists

def test_pdf_rejects_routing_with_path_traversal(self):
    # GET /api/v1/pdf/my-index/some-id?routing=../../../traversal-target -> 400
```

- [ ] **Step 2: Run them, verify they fail**

Docker command with `tests/test_pdf.py`. Expected: the 7 new tests FAIL with 404 (route missing). Show this output to Pierre.

- [ ] **Step 3: Add `get_pdf_preview` to `Document`**, next to `get_jpeg_preview`

- [ ] **Step 4: Add the route `pdf(request: Request) -> FileResponse` in `main.py`**

Order inside `try`: build document, read cookies with `get_cookies_from_forwarded_headers`, `download_meta`, `check_user_authorization`, then if `document.target_content_type not in PDF_CONTENT_TYPES` raise `HTTPException(415)` directly (not `DocumentNotPreviewable`, so the cached download is kept), then `download_document`, then `run_in_threadpool(document.get_pdf_preview)`, return `FileResponse(path, media_type='application/pdf')`. Exception mapping copied from `thumbnail`, plus `TimeoutExpired` in the same branch as `DocumentNotPreviewable` (delete target dir, 415).

- [ ] **Step 5: Run `tests/test_pdf.py`, verify it passes**, then the whole suite: all green.

- [ ] **Step 6: Commit** `feat: serve office documents as pdf`
