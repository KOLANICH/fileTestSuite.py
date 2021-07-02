from pathlib import Path
from sys import stderr

from plumbum import cli

from .formats import sourceExtToPairMapping


class MainCLI(cli.Application):
	pass


@MainCLI.subcommand("convert")
class CompilerCLI(cli.Application):
	def main(self, inputFilePath: cli.switches.ExistingFile):
		inputFilePath = Path(inputFilePath)
		fromFormat, toFormat = sourceExtToPairMapping[inputFilePath.suffix[1:]]
		outputFilePath = inputFilePath.parent / (inputFilePath.stem + "." + toFormat.metaFileExt)
		print("Converting to", outputFilePath.name, file=stderr)

		parsedMetaFile = fromFormat.loadMetadataFile(inputFilePath)
		toFormat.dumpMetadataFile(outputFilePath, parsedMetaFile)

if __name__ == "__main__":
	MainCLI.run()
