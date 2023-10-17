fileTestSuite.py[![Unlicensed work](https://raw.githubusercontent.com/unlicense/unlicense.org/master/static/favicon.png)](https://unlicense.org/)
===============
~~[wheel (GHA via `nightly.link`)](https://nightly.link/fileTestSuite/fileTestSuite.py/workflows/CI/master/fileTestSuite-0.CI-py3-none-any.whl)~~
~~[![GitHub Actions](https://github.com/fileTestSuite/fileTestSuite.py/workflows/CI/badge.svg)](https://github.com/fileTestSuite/fileTestSuite.py/actions/)~~
[![Libraries.io Status](https://img.shields.io/librariesio/github/fileTestSuite/fileTestSuite.py.svg)](https://libraries.io/github/fileTestSuite/fileTestSuite.py)
[![Code style: antiflash](https://img.shields.io/badge/code%20style-antiflash-FFF.svg)](https://codeberg.org/KOLANICH-tools/antiflash.py)

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
