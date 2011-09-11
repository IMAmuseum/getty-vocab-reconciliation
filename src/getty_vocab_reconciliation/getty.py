"""
Corpora support for Getty vocabularies
 - AAT, TGN, ULAN

All vocabularies are read from the original zip packages
containing the XML versions of the vocabs.

Code adapted from the Text, Tagging, and Trust (T3) IMLS
National Leadership Grant.
  http://code.google.com/p/steve-museum/
Charles Moad <cmoad@imamuseum.org>
Ed Bachta <ebachta@imamuseum.org>
"""

from nltk.corpus.reader.api import CorpusReader
from nltk.corpus.reader.util import concat
from nltk.corpus.reader.xmldocs import XMLCorpusView
from nltk.data import PathPointer, FileSystemPathPointer, ZipFilePathPointer
from nltk.util import LazyMap
from string import Template
import re


class VCSTemplate(Template):
    idpattern = '[_0-9][_0-9][_a-zA-Z]'


class GettyXMLCorpusView(XMLCorpusView):
    """
    A simple extension of XMLCorpusView to better detect the
    xml file encodings and handle element return
    """
    
    def _detect_encoding(self, fileid):
        if isinstance(fileid, PathPointer): 
            s = fileid.open().readline() 
        else: 
            s = open(fileid, 'rb').readline()
        
        m = re.search(r'encoding="([^"]+)"', s)
        if m: return m.group(1)
        m = re.search(r"encoding='([^']+)'", s)
        if m: return m.group(1)

        return XMLCorpusView._detect_encoding(self, fileid)
    
    @staticmethod
    def handle_elt_text(elt, context):
        return elt.text


class GettyVocabCorpusReader(CorpusReader):
    """
    Common vocab reader functionality for the different Getty vocabs.
    """
    
    _vcs_to_uni = {}
    
    def __init__(self, root, zipfile, fileids):
        if isinstance(root, basestring):
            root = FileSystemPathPointer(root)
        elif not isinstance(root, PathPointer): 
            raise TypeError('CorpusReader: expected a string or a PathPointer')
        
        # convert to a ZipFilePathPointer
        root = ZipFilePathPointer(root.join(zipfile))
        
        CorpusReader.__init__(self, root, fileids)
        
        self._parse_char_replacements()
    
    def words(self, fileids=None):
        xpath = 'Vocabulary/Subject/Terms/(Preferred_Term|Non-Preferred_Term)/Term_Text'
        if fileids is None: fileids = self.fileids()
        
        return LazyMap(self._replace_chars, concat([GettyXMLCorpusView(fileid, xpath, GettyXMLCorpusView.handle_elt_text)
                                                    for fileid in self.abspaths(fileids)]))
    
    def subjects(self, fileids=None):
        xpath = 'Vocabulary/Subject'
        if fileids is None: fileids = self.fileids()
        
        return concat([GettyXMLCorpusView(fileid, xpath)
                       for fileid in self.abspaths(fileids)])
    
    def terms(self, fileids=None):
        xpath = 'Vocabulary/Subject/Terms/(Preferred_Term|Non-Preferred_Term)'
        if fileids is None: fileids = self.fileids()
        
        return concat([GettyXMLCorpusView(fileid, xpath)
                       for fileid in self.abspaths(fileids)])

    def _parse_char_replacements(self):
        xpath = 'Vocabulary/Character'
        chars = GettyXMLCorpusView(self.abspaths(self._char_file)[0], xpath)
        #for char in chars[:10]:
        for char in chars:
            if (char.find('VCS_Code') != None) and (char.find('Unicode') != None):
                unicode = char.find('Unicode').text
                if ' ' in unicode:
                    self._vcs_to_uni[char.find('VCS_Code').text[1:]] = ''.join([unichr(int(c, 16)) for c in unicode.split()])
                else:
                    self._vcs_to_uni[char.find('VCS_Code').text[1:]] = unichr(int(unicode, 16))            
        #print self._vcs_to_uni
    
    def _replace_chars(self, word):
        """
        Replace any vcs codes with the unicode char
        """
        if not '$' in word: return word

        return VCSTemplate(word).substitute(self._vcs_to_uni)


class GettyAATCorpusReader(GettyVocabCorpusReader):
    """
    """
    
    _zipfile = 'aat_xml_07.zip'
    _fileids = ['AAT.xml']
    _char_file = ['AAT_CHARS.xml']
    _other_files = ['AAT_CONTRIBS.xml',
                    'AAT_LANGUAGES.xml',
                    'AAT_MERGE.xml',
                    'AAT_SOURCES.xml']
    
    def __init__(self, root):
        GettyVocabCorpusReader.__init__(self, root, self._zipfile, self._fileids)


class GettyTGNCorpusReader(GettyVocabCorpusReader):
    """
    """
    
    _zipfile = 'tgn_xml_07.zip'
    _fileids = ['TGN1.xml',
                'TGN12.xml',
                'TGN2.xml',
                'TGN3.xml',
                'TGN4.xml',
                'TGN5.xml',
                'TGN6.xml',
                'TGN7.xml',
                'TGN8.xml',
                'TGN9.xml',
                'TGN10.xml',
                'TGN11.xml']
    _char_file = ['TGN_CHARS.xml']
    _other_files = ['TGN_CONTRIBS.xml',
                    'TGN_LANGUAGES.xml',
                    'TGN_MERGE.xml',
                    'TGN_PTYPES.xml',
                    'TGN_SOURCES.xml']
    
    def __init__(self, root):
        GettyVocabCorpusReader.__init__(self, root, self._zipfile, self._fileids)


class GettyULANCorpusReader(GettyVocabCorpusReader):
    """
    """
    
    _zipfile = 'ulan_xml_07.zip'
    _fileids = ['ULAN1.xml',
                'ULAN2.xml']
    _char_file = ['ULAN_CHARS.xml']
    _other_files = ['ULAN_NATIONALITIES.xml',
                    'ULAN_CONTRIBS.xml',
                    'ULAN_EVENTS.xml',
                    'ULAN_LANGUAGES.xml',
                    'ULAN_MERGE.xml',
                    'ULAN_SOURCES.xml',
                    'ULAN_ROLES.xml',
                    'ULAN_PLACES.xml']
    
    def __init__(self, root):
        GettyVocabCorpusReader.__init__(self, root, self._zipfile, self._fileids)
