#!/usr/bin/env python3
"""Assemble the standalone dice converter HTML: template + tested core + wordlist."""
import ast, json, sys

import os
TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(TOOLS_DIR))
SRC = os.path.join(REPO_ROOT, 'kit', 'bip39_dice_converter.py')

def main(out):
    src = open(SRC).read()
    tree = ast.parse(src)
    words = None
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and getattr(node.targets[0], 'id', '') == 'WORDLIST':
            words = ast.literal_eval(node.value)
    assert words and len(words) == 2048, 'wordlist problem'

    core = open(os.path.join(TOOLS_DIR, 'dice-tool-core.js')).read()
    core = core.replace('/*__WORDLIST__*/[]', json.dumps(words))
    assert '/*__WORDLIST__*/' not in core

    tpl = open(os.path.join(TOOLS_DIR, 'dice-tool-template.html')).read()
    html = tpl.replace('/*__CORE__*/', core)
    assert '/*__CORE__*/' not in html

    open(out, 'w').write(html)
    print(f'wrote {out} ({len(html)} bytes)')

if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(REPO_ROOT, 'docs', 'dice-converter.html'))
