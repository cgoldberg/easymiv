# EasyMIV

### easy minimal image viewer - full-screen image viewer and slideshow in Python

---

- Copyright (c) 2013-2025 [Corey Goldberg][github-home]
- Development: [GitHub][github-repo]
- Download/Install: [PyPI][pypi-easymiv]
- License: [GPLv3][gpl-license]

----

#### Requirements

- Python or 3.6+
- Tkinter
- PIL/Pillow


#### Installation

```
pip install easymiv
```

#### Command Line Usage

```
usage: easymiv [-h] [-s] [-r] [dir]

positional arguments:
  dir                   directory of images (scans recursive)

options:
  -h, --help            show this help message and exit
  -s, --slideshow       slideshow mode
  -r, --random          random shuffle images
```

#### Keyboard Controls

- Quit:
 - q
 - <escape>
 - <control>-c

- Show Next:
 - <space>
 - <right>
 - <down>
 - <return>

- Show Previous:
 - <left>
 - <up>

----

EasyMIV was originally forked from: Miv (Minimal Image Viewer) 0.0.2, (c) 2012 madebits

[github-home]: https://github.com/cgoldberg
[github-repo]: https://github.com/cgoldberg/easymiv
[pypi-easymiv]: https://pypi.org/project/easymiv
[gpl-license]: https://raw.githubusercontent.com/cgoldberg/easymiv/refs/heads/master/LICENSE

