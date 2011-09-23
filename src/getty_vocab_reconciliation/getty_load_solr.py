"""
Load the Getty vocabularies into a SOLR installation
"""

from getty_vocab_reconciliation.getty import GettyAATCorpusReader,\
    GettyULANCorpusReader, GettyTGNCorpusReader
import solr

getty_path = '/home/cmoad/GettyVocab'
solr_url = 'http://localhost:8080/getty-solr'

def load(vocab_name, corpus_reader, sconn):
    """
    Given a solr connection, load terms from a Getty vocab
    """
    
    idx = 0
    bulk_size = 1000
    docs = []

    for term in corpus_reader.terms():
        
        idx += 1
        
        term_text = term.findtext('Term_Text'),
        
        docs.append({
            'id': term.findtext('Term_ID'),
            'vocab_name_s': vocab_name,
            'term_text_s': term_text,
            'term_text_t': term_text,
            'term_type_s': term.findtext('Term_Type'),
            'historic_flag_s': term.findtext('Historic_Flag'),
            'display_order_i': term.findtext('Display_Order'),
            'preferred_term_b': term.tag == 'Preferred_Term'
        })
        
        if idx % bulk_size == 0:
            sconn.add_many(docs)
            sconn.commit()
            docs = []
            print '  %s: Processed %d' % (vocab_name, idx)

    # perform a final commit
    sconn.commit()
    print 'Successfully imported %d records from %s' % (idx, vocab_name)

if __name__ == '__main__':
    # Open a solr connection
    sconn = solr.Solr(solr_url)
    
    # Open the AAT corpus XML file
    aat = GettyAATCorpusReader(getty_path)
    load('AAT', aat, sconn)
    
    ulan = GettyULANCorpusReader(getty_path)
    load('ULAN', ulan, sconn)
    
    tgn = GettyTGNCorpusReader(getty_path)
    load('TGN', tgn, sconn)

    sconn.optimize()
    sconn.close()
