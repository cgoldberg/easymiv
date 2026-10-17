# EasyMIV

### Easy minimal image viewer (full-screen image slideshow)

---

- Copyright (c) 2013-2026 [Corey Goldberg][github-home]
- Development: [GitHub][github-repo]
- Download/Install: [PyPI][pypi-easymiv]
- License: [GPLv3][gpl-license]

----

## Status

<table>
  <tr>
    <td>Latest Version</td>
    <td>
      <a href="https://pypi.org/project/easymiv">
        <img src="https://img.shields.io/pypi/v/easymiv.svg">
      </a>
    </td>
  </tr>
  <tr>
    <td>Tests (CI)</td>
    <td>
      <a href="https://github.com/cgoldberg/easymiv/actions/workflows/test.yml">
        <img src="https://github.com/cgoldberg/easymiv/actions/workflows/test.yml/badge.svg">
      </a>
    </td>
  </tr>
  <tr>
    <td>Supported Python Versions</td>
    <td>
      <a href="https://pypi.org/project/easymiv">
        <img src="https://img.shields.io/pypi/pyversions/easymiv">
      </a>
    </td>
  </tr>
</table>

----

#### Requirements

- Python or 3.11+
- Tkinter
- PIL/Pillow

#### Installation

```
pip install easymiv
```

----

#### Command Line Usage

```
usage: easymiv [-h] [-s] [-r] [dir]

positional arguments:
  dir              directory of images (scans recursively)

options:
  -h, --help       show this help message and exit
  -s, --slideshow  slideshow mode
  -r, --random     randomly shuffle images
```

----

#### Keyboard Controls

- Quit:
  - `q`
  - `<escape>`
  - `<control>-c`

- Show Next:
  - `<space>`
  - `<right>`
  - `<down>`
  - `<return>`

- Show Previous:
  - `<left>`
  - `<up>`

----

EasyMIV was originally forked from: Miv (Minimal Image Viewer) 0.0.2, (c) 2012 madebits

[github-home]: https://github.com/cgoldberg
[github-repo]: https://github.com/cgoldberg/easymiv
[pypi-easymiv]: https://pypi.org/project/easymiv
[gpl-license]: https://raw.githubusercontent.com/cgoldberg/easymiv/refs/heads/master/LICENSE
