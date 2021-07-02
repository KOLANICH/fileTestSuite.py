import unittest
from pathlib import Path

from .formats import loadMetadataFile
from .FileNamePairGen import parserGenFactory


class FileTestSuiteTestCaseMixin:
	__slots__ = ()

	@property
	def fileTestSuiteDir(self):
		raise NotImplementedError

	def _testProcessorImpl(self, challFile: Path, respFile: Path, paramsDict=None):
		raise NotImplementedError

	def _testImplodeDecoderForASubDataSet(self, subDataSetDir: Path, metaData):
		fnpg = parserGenFactory(metaData)
		for challFile, respFile in fnpg.getChallengeResponseFilePairs(subDataSetDir):
			with self.subTest(chall=challFile.stem):
				self._testProcessorImpl(challFile, respFile, paramsDict=None)

	def testUsingDataset(self):
		for subDataSetDir in self.fileTestSuiteDir.iterdir():
			if subDataSetDir.is_dir():
				metaData, metaDataFile = loadMetadataFile(subDataSetDir)
				if metaData:
					with self.subTest(dataset=subDataSetDir.name, metaData=metaData, metaDataFile=metaDataFile):
						self._testImplodeDecoderForASubDataSet(subDataSetDir, metaData)
