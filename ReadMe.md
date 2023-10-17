fileTestSuite.py[![Unlicensed work](https://raw.githubusercontent.com/unlicense/unlicense.org/master/static/favicon.png)](https://unlicense.org/)
===============
~~[wheel (GHA via `nightly.link`)](https://nightly.link/fileTestSuite/fileTestSuite.py/workflows/CI/master/fileTestSuite-0.CI-py3-none-any.whl)~~
~~[![GitHub Actions](https://github.com/fileTestSuite/fileTestSuite.py/workflows/CI/badge.svg)](https://github.com/fileTestSuite/fileTestSuite.py/actions/)~~
[![Libraries.io Status](https://img.shields.io/librariesio/github/fileTestSuite/fileTestSuite.py.svg)](https://libraries.io/github/fileTestSuite/fileTestSuite.py)
[![Code style: antiflash](https://img.shields.io/badge/code%20style-antiflash-FFF.svg)](https://codeberg.org/KOLANICH-tools/antiflash.py)

**We have moved to https://codeberg.org/fileTestSuite/fileTestSuite.py , grab new versions there.**

Under the disguise of "better security" Micro$oft-owned GitHub has [discriminated users of 1FA passwords](https://github.blog/2023-03-09-raising-the-bar-for-software-security-github-2fa-begins-march-13/) while having commercial interest in success and wide adoption of [FIDO 1FA specifications](https://fidoalliance.org/specifications/download/) and [Windows Hello implementation](https://support.microsoft.com/en-us/windows/passkeys-in-windows-301c8944-5ea2-452b-9886-97e4d2ef4422) which [it promotes as a replacement for passwords](https://github.blog/2023-07-12-introducing-passwordless-authentication-on-github-com/). It will result in dire consequencies and is competely inacceptable, [read why](https://codeberg.org/KOLANICH/Fuck-GuanTEEnomo).

If you don't want to participate in harming yourself, it is recommended to follow the lead and migrate somewhere away of GitHub and Micro$oft. Here is [the list of alternatives and rationales to do it](https://github.com/orgs/community/discussions/49869). If they delete the discussion, there are certain well-known places where you can get a copy of it. [Read why you should also leave GitHub](https://codeberg.org/KOLANICH/Fuck-GuanTEEnomo).

---

An implementation of [`fileTestSuite` spec](https://codeberg.org/fileTestSuite/fileTestSuite) for Python.

## Authoring

```bash
fileTestSuiteTool --help
```

### `init`
Creates a boilerplate of `meta.json`.

### `convert`
1. Create a `meta.json` in a dir.
2. `fileTestSuiteTool convert meta.json` to convert into the binary representation
3. `fileTestSuiteTool convert meta.ftsmeta` to convert the binary representation back into JSON.

## Testing

### Via `withFTS` decorator
0. Download a suite of test files. It can be a `git submodule`.
1.
```python
from fileTestSuite.unittest import withFTS
```
2. Get path of the directory of the test suite:
```python
thisDir = Path(__file__).resolve().absolute().parent
thisDir = thisDir / "testDataset"
```
3. Create a test
```python
class Tests(unittest.TestCase):
	@withFTS(thisDir / "testDataset")  # the decorator, that must be within a `TestCase`
	def testProcessorImpl(self, challFile: Path, respFile: Path, paramsDict: typing.Optional[dict]=None) -> None:  # the signature must be this one!
		self._testChallengeResponsePair(challFile=challFile.read_bytes(), respFile=respFile.read_bytes(), paramsDict=paramsDict)  # your function
```

Pros:
* each file corresponds to a test
* it nicely interoperates with `pytest`

Cons:
* tests are loaded at class construction time.

### Via a `subTest`
1.
```python
from fileTestSuite.unittest import FileTestSuiteTestCaseMixin
```

3. Create a test

```python
class Tests(unittest.TestCase, FileTestSuiteTestCaseMixin):
	@property
	def fileTestSuiteDir(self) -> Path:
		return thisDir / "testDataset"

	def _testProcessorImpl(self, challFile: Path, respFile: Path, paramsDict: typing.Optional[dict]=None) -> None:  # the signature must be this one! Note the underscore.
		self._testChallengeResponsePair(challFile=challFile.read_bytes(), respFile=respFile.read_bytes(), paramsDict=paramsDict)  # your function
```

Pros, cons: the inversion of ones of `withFTS`.
