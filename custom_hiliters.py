from pygments.lexers.templates import DjangoLexer
from pygments.lexer import RegexLexer, inherit
from pygments.lexer import DelegatingLexer
from pygments.lexer import bygroups, using, default
from pygments.token import *

class NFTablesBaseLexer(RegexLexer):
    tokens = {
        'root': [
            (r'#.*?\n', Comment.Single),
            (r'[^#]+', Text),
            (r'\n', Punctuation),
        ],
    }

class NFTablesLexer(DelegatingLexer):
    name = 'NFTables'
    aliases = ['nftables', 'nft']
    filenames = ['nftables.conf']

    def __init__(self, **options):
        super().__init__(NFTablesBaseLexer, DjangoLexer, **options)

    #def analyse_text(text):
        #return DjangoLexer.analyse_text(text) - 0.05

CustomLexer = NFTablesLexer

__all__ = ['NFTablesLexer']
