# ClipGuard

ClipGuard is a cross-platform clipboard guard that monitors everything you copy, detects sensitive patterns, and stores a masked history you can safely revisit. It ships with a modern PySide6 desktop UI, granular filters, and configurable rules so you stay in control of what leaves your clipboard.

## Highlights
- **Real-time protection** – Background worker watches the clipboard and reacts instantly without blocking the UI.
- **Sensitive pattern masking** – Built-in rules cover ID cards, bank cards, phone numbers, emails, and IP addresses; add your own keywords at runtime.
- **Rich history browser** – Filter by content type or source application, search the backlog, pin favorites, or send items to the trash.
- **Context-aware details** – Each record keeps the desensitised preview, optional raw content, originating application, and detection types for auditability.
- **Configurable experience** – Tweak polling interval, notification preferences, raw-content retention, and more through the settings dialog.
- **Packaging ready** – `build.py` wraps PyInstaller so you can produce distributable bundles with one command.

## Project Structure

```
├── main.py                   # PySide6 entry point
├── core/
│   └── clipboard_worker.py   # Background clipboard polling thread
├── ui/
│   ├── main_window.py        # Main window layout & behaviour
│   ├── settings_dialog.py    # Runtime configuration dialog
│   ├── models.py             # Table model for history view
│   └── components/           # Sidebar, top bar, list widgets, styling helpers
├── config.py                 # JSON-backed user settings loader/saver
├── database.py               # SQLite persistence & FTS helpers
├── clipboard_monitor.py      # Platform clipboard helpers & fallbacks
├── sensitive_detector.py     # Masking rules for common sensitive data
├── classifier.py             # Content categorisation heuristics
├── platform_utils.py         # Active application name detection
├── assets/                   # Icons & branding assets
└── build.py                  # PyInstaller build script
```

## Requirements

- Python 3.9 or newer (3.11+ recommended)
- [PySide6](https://doc.qt.io/qtforpython/) for the Qt UI
- [pyperclip](https://github.com/asweigart/pyperclip) (macOS/Linux clipboard access)
- [psutil](https://pypi.org/project/psutil/) and [pywin32](https://pypi.org/project/pywin32/) (Windows foreground app detection)
- [pyobjc-framework-AppKit](https://pypi.org/project/pyobjc-framework-AppKit/) (macOS foreground app detection)
- SQLite is bundled with Python and used for history storage

Optional but recommended:
- `pytest` for future automated tests
- `pipx` or virtual environments to isolate dependencies

## Getting Started

```bash
# Clone the repository
git clone https://github.com/<your-account>/ClipGuard.git
cd ClipGuard

# Create & activate a virtual environment (optional but recommended)
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install runtime dependencies
python -m pip install PySide6 pyperclip psutil
# Platform extras
python -m pip install pywin32       # on Windows
python -m pip install pyobjc-framework-AppKit  # on macOS
```

Launch the app in development mode:

```bash
python main.py
```

The UI will start monitoring immediately (if permissions allow). Copy text from different applications and watch ClipGuard populate the history list with masked previews.

## Configuration & Storage

- **Settings file**: `~/.clipguard/config.json` is created on first launch. Editable fields include polling interval (`poll_interval`), raw-content retention (`save_raw_content`), custom sensitive keywords (`custom_sensitive_keywords`), monitoring toggles, theme, language, and more. Use the in-app *Settings* dialog to keep the file consistent.
- **Database**: SQLite history lives at `~/.clipguard/clipboard.db`. Full-text search tables are maintained automatically.
- **Attachments & assets**: UI resources are bundled under `assets/`; adjust icons or themes there if you want to reskin the app.

## Building a Bundle

`build.py` wraps PyInstaller with sensible defaults for macOS, Windows, and Linux. After installing PyInstaller:

```bash
python -m pip install pyinstaller
python build.py
```

Artifacts are created under `dist/`. macOS users will get a `.app` bundle alongside the single-file binary; Windows/Linux receive a standalone executable.

## Development Notes

- **Clipboard monitoring**: `core/clipboard_worker.ClipboardWorker` runs on a `QThread`, relaying new clipboard entries back to the UI thread via Qt signals.
- **Filtering & search**: The sidebar dynamically lists observed applications and content types. Full-text search leverages a SQLite FTS virtual table for responsive results.
- **Sensitive detection**: `sensitive_detector.detect_and_mask` applies regex-based scrubbing and supports runtime user keywords. Extend this module for additional patterns or ML-based classification.
- **Packaging**: Remember to clear `build/` and `dist/` before committing. Icons under `assets/icons` are referenced in both the UI and PyInstaller spec.

## Roadmap Ideas

- ML-assisted content classification and risk scoring
- Cloud sync and encrypted history storage
- Rule-based automation (auto-delete, auto-tag)
- Cross-platform shortcut integration (global hotkeys)

## Contributing

Community contributions are welcome! Until a dedicated `CONTRIBUTING.md` lands, please:

1. Open an issue describing the bug or feature you intend to work on.
2. Keep pull requests focused and reference related issues.
3. Run the app (`python main.py`) and, if applicable, `python build.py` before submitting.
4. Attach screenshots or recordings for visible UI changes.

---

**Need help or have ideas?** Open an issue or discussion thread once the repository is public—ClipGuard’s roadmap is flexible and community feedback is invaluable.
