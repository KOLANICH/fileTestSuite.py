import inspect
import sys
import typing
import unittest
from os import environ
from pathlib import Path

try:
	from typing import Self  # 3.11
except ImportError:
	from typing_extensions import Self

try:
	from typing import Protocol  # 3.8
except ImportError:
	from typing_extensions import Protocol

from . import FTSMetadata
from .FileNamePairGen import parserGenFactory, FileNameSet
from .formats import loadMetadataFile

TRACING_ENV_VAR_NAME = "FILE_TEST_SUITE_TRACING"
SHOULD_TRACE = int(environ.get(TRACING_ENV_VAR_NAME, 0))

__all__ = ("withFTS", "FileTestSuiteTestCaseMixin")


class ProtoTest:
	__slots__ = ("sampleName", "files", "metaData", "datasetName", "params")

	# std::filesystem::path chall, resp;
	# TesteeSpecificContextSharedLibFactoryT& testeeContextFactory;
	def __init__(self, datasetName: str, sampleName: str, files: FileNameSet, metaData: FTSMetadata, params: typing.Mapping[str, typing.Any]):
		self.datasetName = datasetName
		self.sampleName = sampleName
		self.files = files
		self.metaData = metaData
		self.params = params

	def __repr__(self) -> str:
		return self.__class__.__name__ + "<" + genNameForProtoTest(self) + ">"


def genNameForProtoTest(t: ProtoTest):
	return t.datasetName + ":" + t.sampleName


class TestCasesGen:
	__slots__ = ("suiteDir",)

	def __init__(self, suiteDir: Path) -> None:
		self.suiteDir = suiteDir

	def _testForASubDataSet(self, subDataSetDir: Path, metaData: FTSMetadata, dirMeta: typing.Dict[str, Path]) -> typing.Iterator[ProtoTest]:
		fnpg = parserGenFactory(metaData, SHOULD_TRACE)
		for fileNameSet in fnpg.getChallengeResponseFilePairs(subDataSetDir):
			challFile, respFile = fileNameSet
			if SHOULD_TRACE >= 2:
				print(challFile, respFile)

			yield ProtoTest(datasetName=subDataSetDir.name, sampleName=challFile.stem, files=fileNameSet, metaData=metaData, params=None)

	def __iter__(self) -> typing.Iterator[typing.Dict[str, typing.Any]]:
		if SHOULD_TRACE >= 1:
			cwd = Path(".").absolute()

		for subDataSetDir in self.suiteDir.iterdir():
			if SHOULD_TRACE >= 1:
				print("subDataSetDir", subDataSetDir.relative_to(cwd), subDataSetDir.is_dir(), file=sys.stderr)
			if subDataSetDir.is_dir():
				metaData, metaDataFile = loadMetadataFile(subDataSetDir)
				if SHOULD_TRACE >= 1:
					print("Metadata file found:", metaDataFile.relative_to(cwd), file=sys.stderr)
					print("Metadata:", metaData, file=sys.stderr)
				if metaData:
					dirMeta = {
						"metaDataFile": metaDataFile,
					}
					yield from self._testForASubDataSet(subDataSetDir, metaData, dirMeta)


class PairCallable(Protocol):
	def __call__(self: Self, challFile: Path, respFile: Path, params: typing.Optional[dict], *args, **kwargs) -> None:
		raise NotImplementedError


def _closureHelper(func: PairCallable, case: ProtoTest) -> typing.Callable:
	def decF(self):
		challFile, respFile = case.files
		return func(self, challFile=challFile, respFile=respFile, paramsDict=case.params)

	decF.__name__ = func.__name__ + ":" + genNameForProtoTest(case)
	decF.__doc__ = func.__doc__
	return decF


def withFTS(suiteDir: Path) -> typing.Callable[[PairCallable], None]:
	tg = list(TestCasesGen(suiteDir))
	if not tg:
		raise RuntimeError("No test cases found! Use " + TRACING_ENV_VAR_NAME + " to trace")

	def decoratorFunc(func: PairCallable) -> None:
		frame_locals = inspect.currentframe().f_back.f_locals

		for case in tg:
			decF = _closureHelper(func, case)
			frame_locals[decF.__name__] = decF

		return None

	return decoratorFunc


class FileTestSuiteTestCaseMixin:
	__slots__ = ()

	@property
	def fileTestSuiteDir(self) -> Path:
		raise NotImplementedError

	def _testProcessorImpl(self, challFile: Path, respFile: Path, paramsDict=None):
		raise NotImplementedError

	def testUsingDataset(self):
		tg = list(TestCasesGen(self.fileTestSuiteDir))
		if not tg:
			raise RuntimeError("No test cases found! Use " + TRACING_ENV_VAR_NAME + " to trace")

		for case in tg:
			with self.subTest(case):
				self._testProcessorImpl(challFile=case.files["unprocessed"], respFile=case.files["processed"], paramsDict=case.params)
