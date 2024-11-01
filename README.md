# `artifactcache`
A minimalistic python package providing a convenient API to change the default download location for different libraries.

[![CodeQL](https://github.com/Impelon/artifactcache/actions/workflows/codeql.yml/badge.svg)](https://github.com/Impelon/artifactcache/actions/workflows/codeql.yml)

The library is intended as a way to programmatically and conveniently change the default download location for libraries requiring large files (_artifacts_) to be downloaded as part of their normal utilization:
```python
from artifactcache.nltk import cache as NLTK_CACHE
NLTK_CACHE.path = "/tmp/custom-location" # specify a Linux temporary directory new location for NLTK downloads
NLTK_CACHE.enable() # enable the new location

import nltk
# NLTK will search for the punkt-model at the new location and download it if not present already.
# Otherwise NLTK would have chosen the default location of `C:\nltk_data` (Windows) or `/usr/share/nltk_data` / `~/nltk_data` (Unix).
# Under the hood this simply configures the environment variable `NLTK_DATA` accordingly.
nltk.download("punkt")
```

_Cache_ is a bit of a misnomer here and mostly comes from huggingface traditionally using the environment variable `TRANSFORMERS_CACHE` to point to the default download location for models.
_This library does in no way provide software caches that can be used to speed-up access to often used data._

## Installation

pip allows installation from a git-repository directly:

```
pip install git+https://github.com/Impelon/artifactcache.git
```

<details>
<summary>You can also include this in your project as a <a href="https://git-scm.com/book/en/v2/Git-Tools-Submodules">git submodule</a>:</summary>

```
git submodule add https://github.com/Impelon/artifactcache.git
```

Using/Importing the library should be the same. The ability to do this is mostly mentioned out of "historical" reasons, as this project originates as a [part of one of my other projects](https://github.com/Impelon/log-summarization/tree/6c72f1f3b139b63fdfaa386f262ff5086da37a52/code/util/localcache).
One possible advantage of using the library it this way:
You can store library models and other artifacts within your local repo without needing a [virtual environment](https://docs.python.org/3/library/venv.html) - and without the need to specify a central default location.
Any downloaded artifacts will be automatically ignored. ([See below](#git-submodule-behaviour).)

</details>

## Usage

After setting the `path` for a `cache`, it may be enabled to instruct its corresponding library to use the given `path` as the default download location.
The cache will create the path to the new location in case directories are missing.

```shell
$ tree --noreport folder-with-nltk-artifacts # folder does not exist yet
folder-with-nltk-artifacts [error opening dir]
$
$ python3 -q
>>> from artifactcache.nltk import cache as NLTK_CACHE
>>> NLTK_CACHE.path = "folder-with-nltk-artifacts" # save in local directory
>>> NLTK_CACHE.enable()
>>>
>>> import nltk # import after cache was enabled
>>> nltk.download("punkt")
[nltk_data] Downloading package punkt to folder-with-nltk-artifacts...
[nltk_data]   Unzipping tokenizers/punkt.zip.
True
>>> exit()
$
$ tree --noreport folder-with-nltk-artifacts # NLTK downloaded its model to the local path
folder-with-nltk-artifacts
`-- tokenizers
    |-- punkt
    |   |-- czech.pickle
    |   |-- [...]
    |   |-- PY3
    |   |   |-- czech.pickle
    |   |   `-- [...]
    |   |-- README
    |   `-- [...]
    `-- punkt.zip
```

Some libraries do not support changing the default download location _after_ they have been imported.
This means that usually you want to enable the cache corresponding to a library _before_ importing the library.

### Using Multiple Caches

Where `artifactcache` really begins to shine is when you use multiple libraries which require additional files to be downloaded.
Instead of setting a new location for each library manually, you can use the special cache created by `centralized_cache` when setting up your other caches.
This will allow you to specify a central location for all your downloaded files:

```python3
import artifactcache
with artifactcache.centralized_cache("folder-with-artifacts"):
    # Caches created within this context will be within the centralized location.
    from artifactcache.nltk import cache as NLTK_CACHE
    from artifactcache.huggingface import cache as HF_CACHE

NLTK_CACHE.enable()
HF_CACHE.enable()

# Import libraries after their caches were enabled.
import nltk
nltk.download("brown")
import tokenizers
tokenizer = tokenizers.Tokenizer.from_pretrained("distilbert-base-uncased")
from datasets import load_dataset
data = load_dataset("squad_v2")
```

<details>
<summary>Here is the folder structure after executing above example:</summary>

```shell
$ dir
folder-with-artifacts venv
$ tree --noreport folder-with-artifacts
folder-with-artifacts
|-- huggingface
|   |-- datasets
|   |   |-- downloads
|   |   |   `-- [...]
|   |   |-- [...]
|   |   `-- squad_v2
|   |       `-- squad_v2
|   |           `-- 2.0.0
|   |               `-- [...]
|   |-- hub
|   |   `-- models--distilbert-base-uncased
|   |       `-- [...]
|   |-- modules
|   |   |-- datasets_modules
|   |   |   |-- datasets
|   |   |   |   |-- __init__.py
|   |   |   |   |-- [...]
|   |   |   |   |-- squad_v2
|   |   |   |   |   `-- [...]
|   |   |   |   `-- [...]
|   |   |   `-- [...]
|   |   `-- __init__.py
|   |-- tokenizers
|   `-- transformers
`-- nltk
    `-- corpora
        |-- brown
        |   |-- ca01
        |   |-- [...]
        |   `-- README
        `-- brown.zip
```

</details>

### Git Submodule Behaviour

When used as a submodule the example from above can be simplified.
This is because caches will have a default location relative to their source files.
This means that you do not need to specify a centralized location for all caches, the files will be downloaded to the already existing directory-structure created by the library itself.

```python3
# When used as a git submodule there is no need to specify a separate centralized location.
from artifactcache.nltk import cache as NLTK_CACHE
from artifactcache.huggingface import cache as HF_CACHE

NLTK_CACHE.enable()
HF_CACHE.enable()

import nltk
nltk.download("brown")
import tokenizers
tokenizer = tokenizers.Tokenizer.from_pretrained("distilbert-base-uncased")
from datasets import load_dataset
data = load_dataset("squad_v2")
```

<details>
<summary>Here is the folder structure after executing above example within the repository, one level above the git submodule:</summary>

```shell
$ git status
On branch main
nothing to commit, working tree clean
$
$ # As can be seen next, the downloaded files are located within the submodule.
$ # Still, the working tree remains clean, because all downloaded files are correctly ignored.
$
$ tree --noreport artifactcache
artifactcache
|-- artifactcache
|   |-- _cachetypes.py
|   |-- [...]
|   |-- huggingface
|   |   |-- datasets
|   |   |   |-- downloads
|   |   |   |   `-- [...]
|   |   |   |-- [...]
|   |   |   `-- squad_v2
|   |   |       `-- squad_v2
|   |   |           `-- 2.0.0
|   |   |               `-- [...]
|   |   |-- hub
|   |   |   `-- models--distilbert-base-uncased
|   |   |       |-- blobs
|   |   |       |   `-- 949a6f013d67eb8a5b4b5b46026217b888021b88
|   |   |       |-- refs
|   |   |       |   `-- main
|   |   |       `-- snapshots
|   |   |           `-- 6cdc0aad91f5ae2e6712e91bc7b65d1cf5c05411
|   |   |               `-- tokenizer.json -> ../../blobs/949a6f013d67eb8a5b4b5b46026217b888021b88
|   |   |-- __init__.py
|   |   |-- modules
|   |   |   |-- datasets_modules
|   |   |   |   `-- [...]
|   |   |   `-- __init__.py
|   |   |-- [...]
|   |   |-- tokenizers
|   |   |   |-- __init__.py
|   |   |   |   `-- [...]
|   |   `-- transformers
|   |       |-- __init__.py
|   |   |   |   `-- [...]
|   |-- __init__.py
|   |-- __init__.pyc
|   |-- nltk
|   |   |-- corpora
|   |   |   |-- brown
|   |   |   |   |-- [...]
|   |   |   |   `-- README
|   |   |   `-- brown.zip
|   |   |-- __init__.py
|   |   `-- [...]
|   `-- [...]
|-- __init__.py
|-- [...]
`-- tests.py
```

</details>

This behaviour is also available if installed through pip, but cannot be recommended since pip will not automatically remove the downloaded files when uninstalling `artifactcache`.

## Contributing

Missing support for your favourite library? Open an issue! :innocent:

In many cases adding support is as easy as adapting an example [`__init__.py` file](artifactcache/nltk/__init__.py) for the desired library by changing the environment variable. Feel free to open a pull-request in that case! If possible, also link to documentation that explains the environment variable for that library.
