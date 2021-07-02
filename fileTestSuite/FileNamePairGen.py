import typing
from pathlib import Path

from . import ParsedMetadataJSONLikeT


class IFileNamePairGen:
	__slots__ = ("processedExt",)

	def __init__(self, processedExt: str) -> None:
		self.processedExt = processedExt

	@property
	def challFileGlobPattern(self) -> str:
		raise NotImplementedError

	@property
	def respFileGlobPattern(self):
		return "*." + self.processedExt

	def getChallFileNameFromResp(self, fn: Path):
		raise NotImplementedError

	def globChallFiles(self, subDataSetDir):
		return subDataSetDir.glob(self.challFileGlobPattern)

	def globRespFiles(self, subDataSetDir):
		return subDataSetDir.glob(self.respFileGlobPattern)

	def getChallengeResponseFilePairs(self, subDataSetDir):
		for respFile in self.globRespFiles(subDataSetDir):
			challFile = subDataSetDir / (self.getChallFileNameFromResp(respFile))
			yield challFile, respFile

class FileNamePairGenCompPostfix(IFileNamePairGen):
	__slots__ = ()

	@property
	def challFileGlobPattern(self):
		raise NotImplementedError

	def getChallFileNameFromResp(self, fn: Path):
		return fn.stem


class FileNamePairGenCompReplace(IFileNamePairGen):
	__slots__ = ("rawExt",)

	def __init__(self, processedExt: str, rawExt: str) -> None:
		super().__init__(processedExt)
		self.rawExt = rawExt

	@property
	def challFileGlobPattern(self):
		raise NotImplementedError

	def getChallFileNameFromResp(self, fn: Path) -> str:
		return fn.stem + "." + self.rawExt


def parserGenFactory(parsedMetaFile: ParsedMetadataJSONLikeT) -> FileNamePairGenCompReplace:
	if parsedMetaFile.rawExt:
		return FileNamePairGenCompReplace(parsedMetaFile.processedExt, parsedMetaFile.rawExt)
	else:
		return FileNamePairGenCompPostfix(parsedMetaFile.processedExt)
