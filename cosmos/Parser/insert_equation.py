import sys, os
sys.path.append(os.path.dirname(__file__))
from fonduer.meta import Meta
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.dialects import postgresql
import json
from fonduer.parser.models import Document, Sentence
from collections import defaultdict
from latex_parser.variable_extractor import get_variables
from itertools import chain
from os.path import join

INT_ARRAY_TYPE = postgresql.ARRAY(Integer)
STR_ARRAY_TYPE = postgresql.ARRAY(String)

# Grab pointer to global metadata
db_connect_str = "postgres://postgres:password@localhost:5432/cosmos8"
_meta = Meta.init()


class Equation(_meta.Base):
    """A Sentence subclass with Lingual, Tabular, Visual, and HTML attributes."""

    __tablename__ = "equation"

    #: The unique id for the ``Sentence``.
    id = Column(Integer, primary_key=True)

    # #: The position of the ``Sentence`` in the ``Document``.
    # position = Column(Integer, nullable=False)  # unique sentence number per document

    #: The name of a ``Sentence``.
    name = Column(String, unique=False, nullable=True)

    #: The id of the parent ``Document``.
    document_id = Column(Integer)

    #: The id of the parent ``Section``.
    section_id = Column(Integer)
    #: The parent ``Section``.

    #: The id of the parent ``Paragraph``.
    paragraph_id = Column(Integer)

    #: The full text of the ``Sentence``.
    latex = Column(Text, nullable=False)

    #: A list of the words in a ``Sentence``.
    variables = Column(STR_ARRAY_TYPE)

    top = Column(Integer)

    bottom = Column(Integer)

    left = Column(Integer)

    right = Column(Integer)

    page = Column(Integer)


def insert_equation_tuple(db, resource_loc):
    session = Meta.init(db).Session()
    for doc in session.query(Document):
        locs = json.load(open(join(resource_loc, '%s.html.json' % doc.name)))
        print(join(resource_loc, '%s.html.json' % doc.name))
        print("locs:")
        print(len(locs))
        locs_counter = 0
        eqs_groupby_section_para = defaultdict(lambda: defaultdict(list))
        for sent in session.query(Sentence).filter(Sentence.document_id == doc.id):
            if sent.name == 'Equation':
                eqs_groupby_section_para[sent.section_id][sent.paragraph_id].append(
                    {
                        'text': sent.text,
                        'page': sent.page
                    }
                )

        for sec_id, para_dic in eqs_groupby_section_para.items():
            for paragraph_id, eqs in para_dic.items():
                latex_code = ''.join(map(lambda x: x['text'], eqs))
                variables = list(get_variables(latex_code))
                if len(variables) == 0 or variables[0] == -1:
                    variables = None

                print('counter: '+str(locs_counter))
                print('doc_id: '+str(doc.id))
                e = Equation(
                    name='Equation', document_id=doc.id, section_id=sec_id, paragraph_id=paragraph_id,
                    latex=latex_code, variables=variables,
                    top=locs[locs_counter]['ymin'],
                    bottom=locs[locs_counter]['ymax'],
                    left=locs[locs_counter]['xmin'],
                    right=locs[locs_counter]['xmax'],
                    page=locs[locs_counter]['page_num']
                )

                session.add(e)
                locs_counter += 1
        session.commit()


if __name__ == '__main__':
    insert_equation_tuple(db_connect_str, 'out/equations/')
    # session = Meta.init(db_connect_str).Session()
    # session.add(Equation(name="Equation", latex="\\tfrac{a}{b}"))
    # session.commit()
