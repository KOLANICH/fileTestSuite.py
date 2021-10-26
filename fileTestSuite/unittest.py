import unittest
from pathlib import Path

from .formats import loadMetadataFile
from .FileNamePairGen import parserGenFactory


def combineSuites(testSuites):
	s = unittest.TestSuite()
	for testSuite in testSuites:
		s.addTests(testSuite._tests)
	return s


class FTSTestClass(unittest.TestCase):
	@classmethod
	def getFileTestSuiteDir(cls):
		raise NotImplementedError

	def _testProcessorImpl(self, challFile: Path, respFile: Path, paramsDict=None):
		raise NotImplementedError


class GeneratedTestProgram(unittest.TestProgram):
	# __slots__ = ()

	def __init__(self, tests=None, defaultTest=None, argv=None, testRunner=None, testLoader=unittest.loader.defaultTestLoader, exit=True, verbosity=1, failfast=None, catchbreak=None, buffer=None, warnings=None, testClass=None, *args, **kwargs):
		if issubclass(tests, FTSTestClass):
			testClass = tests
			tests = None

		self.testClass = testClass

		if tests is None:
			tests = self.generateTestsForDataSets()
		runTestsBackup = self.runTests
		self.testz = tests
		super().__init__(object(), defaultTest, argv, testRunner, testLoader, exit, verbosity, failfast, catchbreak, buffer, warnings, *args, **kwargs)

	def createTests(self):
		self.test = combineSuites(map(self.testLoader.loadTestsFromTestCase, self.testz))
		if self.testNames:
			self.testNames = set(self.testNames)
			self.test._tests = type(self.test._tests)(filter(lambda e: e[1] in self.testNames, self.test._tests.items()))

	def _generateTestsForASubDataSet(self, subDataSetDir: Path, metaData, metaDataName, paramsDict=None):
		fnpg = parserGenFactory(metaData)
		for challFile, respFile in fnpg.getChallengeResponseFilePairs(subDataSetDir):
			yield self._generateTest(challFile, respFile, metaData, metaDataName, paramsDict=paramsDict)

	def genTestMethod(sself, challFile, respFile):
		def testFunc(self):
			self._testProcessorImpl(challFile, respFile, paramsDict=None)

		testFunc.__name__ = "test_" + challFile.stem
		# testFunc.__doc__=model["model"]
		return testFunc

	def _generateTest(sself, challFile, respFile, metaData, metaDataName, paramsDict=None):
		class DatasetTestMeta(type):
			def __new__(cls, className, parents, attrs, *args, **kwargs):
				testFunc = sself.genTestMethod(challFile, respFile)
				attrs[testFunc.__name__] = testFunc

				res = super().__new__(cls, className, parents, attrs, *args, **kwargs)
				return res

		class Test(sself.testClass, metaclass=DatasetTestMeta):
			maxDiff = None

		Test.__name__ = metaDataName
		return Test

	def generateTestsForDataSets(self):
		for subDataSetDir in self.testClass.getFileTestSuiteDir().iterdir():
			if subDataSetDir.is_dir():
				metaData, metaDataFile = loadMetadataFile(subDataSetDir)
				if metaData:
					yield from self._generateTestsForASubDataSet(subDataSetDir, metaData, metaDataFile.stem)
