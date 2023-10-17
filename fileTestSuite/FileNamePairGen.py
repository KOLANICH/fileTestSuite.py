import typing
from pathlib import Path

from . import FTSMetadata, ParsedMetadataJSONLikeT


class RoleIntMapper:
	__slots__ = ("mapper",)

	def __init__(self, rolesToPlaceMapping: typing.Mapping[str, int]):
		self.mapper = type(rolesToPlaceMapping)(sorted(rolesToPlaceMapping.items(), key=lambda x: x[1]))

	def __getitem__(self, k):
		return self.mapper[k]

	def __repr__(self):
		return self.__class__.__name__ + "<" + repr(tuple(self.roles.keys()))[1:-1] + ">"

	def __iter__(self):
		return self.mapper.items()


class FileNameSet:
	__slots__ = ("mapper", "setList")

	def __init__(self, mapper: RoleIntMapper, setList: typing.Tuple[Path]):
		self.mapper = mapper
		self.setList = setList

	def __repr__(self):
		return self.__class__.__name__ + "(" + repr(self.mapper) + ", " + repr(self.setList) + ")"

	def __iter__(self):
		return iter(self.toTuple())

	def __getitem__(self, k):
		return self.setList[self.mapper[k]]

	def toDict(self) -> typing.Mapping[str, Path]:
		return {nm: self.setList[v] for nm, i in self.mapper}

	def toTuple(self) -> typing.Tuple[Path]:
		return self.setList


pairMapper = RoleIntMapper({"unprocessed": 0, "processed": 1})


class FileNamePair(FileNameSet):
	__slots__ = ()

	def __init__(self, *setList: typing.Tuple[Path]):
		super().__init__(pairMapper, setList)


class IFileNameSetGen:
	__slots__ = ("processedExt", "debug")

	def __init__(self, processedExt: str, debug: int = 0) -> None:
		self.processedExt = processedExt
		self.debug = debug

	@property
	def challFileGlobPattern(self) -> str:
		raise NotImplementedError

	@property
	def respFileGlobPattern(self) -> str:
		return "*." + self.processedExt

	def getChallFileNameFromResp(self, fn: Path):
		raise NotImplementedError

	def globChallFiles(self, subDataSetDir):
		return subDataSetDir.glob(self.challFileGlobPattern)

	def globRespFiles(self, subDataSetDir: Path) -> typing.Iterator[typing.Any]:
		return subDataSetDir.glob(self.respFileGlobPattern)

	def getChallengeResponseFilePairs(self, subDataSetDir: Path) -> typing.Iterator[FileNameSet]:
		for respFile in self.globRespFiles(subDataSetDir):
			challFile = subDataSetDir / (self.getChallFileNameFromResp(respFile))
			yield FileNamePair(challFile, respFile)


class FileNamePairGenCompPostfix(IFileNameSetGen):
	__slots__ = ()

	@property
	def challFileGlobPattern(self):
		raise NotImplementedError

	def getChallFileNameFromResp(self, fn: Path) -> str:
		return fn.stem


class FileNamePairGenCompReplace(IFileNameSetGen):
	__slots__ = ("rawExt",)

	def __init__(self, processedExt: str, rawExt: str, debug: int = 0) -> None:
		super().__init__(processedExt, debug)
		self.rawExt = rawExt

	@property
	def challFileGlobPattern(self):
		raise NotImplementedError

	def getChallFileNameFromResp(self, fn: Path) -> str:
		return fn.stem + "." + self.rawExt


class FileNamePairGenCompGlob(FileNamePairGenCompReplace):
	__slots__ = ()

	def getChallFileNameFromResp(self, fn: Path) -> str:
		globExpr = super().getChallFileNameFromResp(fn)
		globbed = tuple(set(fn.parent.glob(globExpr)) - {fn})

		if self.debug >= 2:
			print("globExpr", globExpr, "globbed", globbed)

		if len(globbed) != 1:
			raise ValueError("Zero/multiple challenge files match the response file", fn, globbed)
		return globbed[0]


def parserGenFactory(parsedMetaFile: FTSMetadata, debug: int = 0) -> FileNamePairGenCompReplace:
	if parsedMetaFile.rawExt:
		if "*" in parsedMetaFile.rawExt:
			return FileNamePairGenCompGlob(parsedMetaFile.processedExt, parsedMetaFile.rawExt, debug)
		else:
			return FileNamePairGenCompReplace(parsedMetaFile.processedExt, parsedMetaFile.rawExt, debug)
	else:
		return FileNamePairGenCompPostfix(parsedMetaFile.processedExt, debug)
