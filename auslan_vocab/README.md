# auslan_vocab/

Reserved location for **validated AUSLAN sign assets** produced by
the participatory consultation process documented in
[`docs/auslan_consultation/`](../docs/auslan_consultation/).

## Current state

This directory is empty by design. The eight provisional sign
animations that ship with the project are SVG illustrations of the
proposed motion, and they live in
`gui/static/auslan_videos/`. They are **not** validated AUSLAN
signs — every screen of the application labels them as such.

## Future state

Once the validation protocol described in
[`docs/auslan_consultation/validation_protocol.md`](../docs/auslan_consultation/validation_protocol.md)
has been completed for each species, this directory will hold the
consented assets:

```
auslan_vocab/
├── aquila_audax/
│   ├── sign.mp4               — final video, 1080p, 15 s
│   ├── sign.webm              — VP9 fallback for browsers
│   ├── consent_form.pdf       — signed by the consultant
│   └── README.md              — description, validator names,
│                                acceptance metrics
├── falco_peregrinus/
│   └── ...
└── ...
```

When the consented videos exist, swap the relevant entry of
`SPECIES_INFO[<key>]["auslan_video"]` in `gui/app.py` from
`<key>.svg` to `<key>.mp4` and the GUI's media renderer will
auto-detect the new format.

## Why this folder exists in the empty state

Keeping the folder reserved (with this README) signals to
collaborators that the project intends to receive validated assets
here. It also prevents the placeholder SVGs from being treated as
authoritative.

For the consultation roadmap, contact details, and budget see
[`docs/auslan_consultation/README.md`](../docs/auslan_consultation/README.md).
