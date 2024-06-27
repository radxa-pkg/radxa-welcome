# radxa-welcome
RadxaOS Greeter

# Run from source
```bash
python3 ./launch.py
```

# Packaging

To package for debian, run the following command:

```
debuild --no-lintian --lintian-hook "lintian --fail-on error,wa
rning --suppress-tags bad-distribution-in-changes-file -- %p_%v_*.changes" --no-sign -b
```

# Contributing

Use Cambalache to edit the UI files. .cmb file is located at `data/ui/welcome.cmb`