"""
Load the Getty vocabularies into a SOLR installation
"""

from getty_vocab_reconciliation.getty import GettyAATCorpusReader
import solr

getty_path = '/usr/local/share/corpora/getty'
solr_url = 'http://127.0.0.1:8080/solr'

# Open the AAT corpus XML file
GettyAATCorpusReader._zipfile = 'aat_xml_utf8_sample11.zip'
aat = GettyAATCorpusReader(getty_path)

# Open a solr connection
s = solr.Solr(solr_url)

# Load each term into Solr
for term in aat.terms():
    doc = {
        'id': term.findtext('Term_ID'),
        'text': term.findtext('Term_Text'),
        'display_order_i': term.findtext('Display_Order'),
    }
    s.add(doc)
    
s.commit()
s.optimize()
s.close()

