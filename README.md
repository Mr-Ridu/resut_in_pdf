# PixelIQ Result Generator

**A free lead-magnet tool by [PixelIQ](https://pixeliqit.com) — pixeliqit.com**

Turn a spreadsheet of student marks into beautifully designed, print-ready PDF
result sheets in one click. Upload an Excel file, map your columns, and get an
individual academic report card for every student — complete with grades,
GPA, class position, school logo, signature and seal.

Originally released as an open-source "School Result Generator", now fully
branded and maintained by PixelIQ.

---

## ✨ Features

- 📤 Upload `.xlsx` / `.xls` student result files
- 🗺️ Visual column mapping (name, roll, class, section, shift, semester, subjects)
- 📊 Auto-calculated totals, averages, grades, GPA and class position
- 🖨️ Print-ready PDF output (A4/A5, portrait/landscape, 5 color themes)
- 🏫 School branding: logo, signature, seal on every result sheet
- 🔐 Login system with per-user settings and result history
- 🖥️ **Desktop app** — runs as a standalone program on Windows/Linux/macOS

## 🎨 Branding

Everything — the web UI, login page, generated PDFs (content + document
metadata) and the Django admin — carries the PixelIQ identity:

| Surface | Branding |
|---|---|
| Page titles / navbar / footer | `PixelIQ Result Generator · pixeliqit.com` |
| Generated PDFs | Footer credit + `Title`/`Author`/`Creator` metadata |
| Django admin | `PixelIQ Result Generator Admin` |
| Logo / favicon | `result_app/static/result_app/images/pixeliq_logo.png` |
| Color palette | Navy `#021024`, blue `#5483B3`, sky `#C1E8FF` |

## 🚀 Run from source

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirments.txt
.venv/bin/python manage.py migrate
.venv/bin/python manage.py createsuperuser
.venv/bin/python manage.py runserver 0.0.0.0:3000
```

Open http://127.0.0.1:3000/ — static assets and Bootstrap/Font Awesome load
from CDNs, so an internet connection is needed for the full UI.

## 🖥️ Desktop app

The desktop edition starts the app on `127.0.0.1`, signs you in automatically
(no login screen), opens a native window (pywebview on Windows) or your
default browser, and stores its database/media in a per-user data folder:

- Windows: `%APPDATA%\PixelIQResultGenerator`
- macOS: `~/Library/Application Support/PixelIQResultGenerator`
- Linux: `~/.local/share/PixelIQResultGenerator`

### Build it yourself

```bash
# Linux / macOS
./desktop/build.sh          # -> dist/PixelIQResultGenerator
```

```bat
:: Windows (also installs pywebview for the native window)
desktop\build_windows.bat   # -> dist\PixelIQResultGenerator.exe
```

Or push a `v*` tag (or run the **Desktop builds** workflow manually) and grab
the installers from the GitHub Actions artifacts — builds for Windows, Linux
and macOS are produced on every run.

Run straight from a source checkout without building:

```bash
python desktop/launch.py
```

> The auto-login middleware (`PIXELIQ_DESKTOP=1`) is only active when the
> desktop launcher starts the app, and the desktop server binds to loopback
> only. Web deployments never set that variable, so normal login still applies.

## ✅ Tests

```bash
.venv/bin/python manage.py test result_app
```

Covers PixelIQ branding on every page, the full upload → map → preview →
generate workflow, PDF content/metadata branding, and grading logic.

## 📁 Project layout

```
school_result_generator/   Django project (settings, admin branding)
result_app/                Web app: views, forms, models, PDF engine, templates
desktop/                   Desktop launcher + build scripts (PyInstaller)
.github/workflows/         CI: desktop builds for Windows/Linux/macOS
media/                     Uploaded logos/signatures + generated PDFs
```

## 🔗 Links

- Website: [pixeliqit.com](https://pixeliqit.com)
- Institute Management System & more: [PixelIQ products](https://pixeliqit.com)
- Support: [pixeliqit.com contact](https://pixeliqit.com)

---

© PixelIQ · pixeliqit.com — free tool, attribution appreciated.
