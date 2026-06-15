Put source font files here for conversion.

Suggested naming:
- `Name36.ttf` or `Name36.otf` for a 36 pixel font
- `Name12.bdf` or `Name12.pcf` if the height is already encoded in the file

Then run:

```bash
python3 tools/build_fonts.py
```

This generates Python font modules into `firmware/fonts/`.
