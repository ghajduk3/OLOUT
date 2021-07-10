"""
Tools for reading a nexus file
"""
import io
import gzip
import pathlib
import re
import warnings

from nexus.handlers import GenericHandler
from nexus.handlers import BEGIN_PATTERN, END_PATTERN
from nexus.handlers.taxa import TaxaHandler
from nexus.handlers.data import CharacterHandler, DataHandler
from nexus.handlers.tree import TreeHandler
from nexus.exceptions import NexusFormatException

HANDLERS = {
    'data': DataHandler,
    'characters': CharacterHandler,
    'trees': TreeHandler,
    # 'taxa': TaxaHandler,
}


class NexusReader(object):
    """A nexus reader"""
    def __init__(self, filename=None, **blocks):
        assert not (filename and blocks), 'cannot initialize from file *and* blocks'
        self.filename = None
        self.short_filename = None
        self.blocks = {}
        self.data = None
        self.characters = None
        self.trees = None
        self.taxa = None
        self.site_url = None

        if blocks:
            self._set_blocks(blocks)

        if filename:
            self.filename = filename
            self.short_filename = pathlib.Path(filename).name
            self._set_blocks(NexusReader._blocks_from_file(filename)[0])

    @classmethod
    def from_file(cls, filename, encoding='utf-8-sig'):
        """
        Loads and Parses a Nexus File
        :param filename: filename of a nexus file
        :raises IOError: If file reading fails.
        :return: `NexusReader` object.
        """
        res = cls()
        blocks, site_url = NexusReader._blocks_from_file(filename, encoding=encoding)
        res._set_blocks(blocks)
        res.site_url = site_url

        res.filename = filename
        res.short_filename = pathlib.Path(filename).name
        return res, site_url

    @classmethod
    def from_string(cls, string):
        """
        Loads and Parses a Nexus from a string
        :param contents: string or string-like object containing a nexus
        :type contents: string
        :return: None
        """
        res = cls()
        res._set_blocks(NexusReader._blocks_from_string(string))
        return res

    def _set_blocks(self, blocks):
        self.blocks = {}
        for block, lines in (blocks.items() if isinstance(blocks, dict) else blocks):
            # print(block)
            # if block in self.blocks:
            #     raise NexusFormatException("Duplicate Block %s" % block)
            # self.blocks[block] =
            self.blocks.setdefault(block,[]).append(HANDLERS.get(block, GenericHandler)(name=block, data=lines))

        if self.blocks.get('characters') and not self.blocks.get('data'):
            self.blocks['data'] = self.blocks['characters']

        for block in self.blocks:
            setattr(self, block, self.blocks[block])

    def read_file(self, filename, encoding='utf-8-sig'):
        warnings.simplefilter('always', DeprecationWarning)  # turn off filter
        warnings.warn(
            "Call to deprecated method NexusReader.read_file",
            category=DeprecationWarning,
            stacklevel=1)
        warnings.simplefilter('default', DeprecationWarning)  # reset filter
        self._set_blocks(NexusReader._blocks_from_file(filename, encoding=encoding)[0])
        self.filename = filename
        self.short_filename = pathlib.Path(filename).name

    def read_string(self, contents):
        warnings.simplefilter('always', DeprecationWarning)  # turn off filter
        warnings.warn(
            "Call to deprecated method NexusReader.read_string",
            category=DeprecationWarning,
            stacklevel=1)
        warnings.simplefilter('default', DeprecationWarning)  # reset filter
        self._set_blocks(NexusReader._blocks_from_string(contents))
        return self

    @staticmethod
    def _blocks_from_string(string):
        return NexusReader._iter_blocks(io.StringIO(string).readlines())

    @staticmethod
    def _iter_blocks(iterlines):
        block, lines = None, []

        for line in iterlines:
            line = line.strip()
            if not line:
                continue
            elif line.startswith('[') and line.endswith(']'):
                continue
            # if re.match(r'^TreeBASE Study URI',line):
            #     print("Found site url")
            #     site_url = re.search(r'http[A-Za-z.:/0-9]*',line).group()
            #     print(site_url)

            start = BEGIN_PATTERN.findall(line)
            if start:
                if block and lines:
                    # "end" is optional!
                    yield block, lines
                block, lines = start[0][0].lower(), []

            if block:
                lines.append(line)

            if END_PATTERN.search(line):
                if block:
                    yield block, lines
                block, lines = None, []

        if block and lines:
            # "end" is optional. Whatever we have left is counted as belonging to the last block.
            yield block, lines

    @staticmethod
    def _blocks_from_file(filename, encoding='utf-8-sig'):
        filename = pathlib.Path(filename)

        if not (filename.exists() and filename.is_file()):
            raise IOError("Unable To Read File %s" % filename)

        if filename.suffix == '.gz':
            handle = gzip.open(str(filename), 'rt', encoding=encoding)
        else:
            handle = filename.open('r', encoding=encoding)
        lines = handle.readlines()
        res = NexusReader._iter_blocks(lines)
        site_url = NexusReader._get_site_url(lines)

        handle.close()
        return res, site_url

    @staticmethod
    def _get_site_url(iterlines):
        for line in iterlines:
            line = line.strip()
            if not line:
                continue
            elif line.startswith('[') and line.endswith(']'):
                continue
            if re.match(r'^TreeBASE Study URI',line):
                site_url = re.search(r'http[A-Za-z.:/0-9]*',line).group()
                return site_url
    def write(self, **kw):
        """
        Generates a string containing a complete nexus from
        all the data.
        :return: String
        """
        out = ["#NEXUS\n"]
        for block in self.blocks:
            out.append(self.blocks[block].write())
            # empty line after block if needed
            if len(self.blocks) > 1:
                out.append("\n")
        return "\n".join(out)

    def write_to_file(self, filename):
        """
        Writes the nexus to a file.
        :return: None
        """
        with pathlib.Path(filename).open('w', encoding='utf8') as handle:
            handle.writelines(self.write())
