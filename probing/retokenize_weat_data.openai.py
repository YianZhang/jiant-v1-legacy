#!/usr/bin/env python

# Helper script to retokenize edge-probing data using a BPE model.
# Uses the tokenizer for the OpenAI transformer LM, as described in
# https://blog.openai.com/language-unsupervised/ and using the code from
# https://github.com/openai/finetune-transformer-lm
#
# Like retokenize_edge_data.py, this saves the result alongside the original
# files.
#
# Usage:
#  python retokenize_edge_data.py /path/to/edge/probing/data/*.json
#
# Requirements: this requires the `spacy` and `ftfy` packages for running the
# preprocessing for the OpenAI model. These should only be needed for this
# script - main.py shouldn't need to do any further preprocessing.

import os
import sys
import json

import logging as log
log.basicConfig(format='%(asctime)s: %(message)s',
                datefmt='%m/%d %I:%M:%S %p', level=log.INFO)

from src.utils import utils
from src.utils import retokenize
from src.openai_transformer_lm import utils as openai_utils

def space_tokenize_with_eow(sentence):
    """Add </w> markers to ensure word-boundary alignment."""
    return [t + "</w>" for t in sentence.split()]

def retokenize_record(text):
    """Retokenize edge probing examples. Modifies in-place.

    This can be slow, so recommended to use as a pre-processing step.
    See retokenize_edge_data.py.
    """
    eow_tokens = space_tokenize_with_eow(text)
    bpe_tokens = openai_utils.tokenize(text)
    for bpe_tok in bpe_tokens:
        if bpe_tok not in openai_utils.encoder_dict:
            log.warn("Token %s not found in OpenAI vocab!", bpe_tok)

    ta = retokenize.TokenAligner(eow_tokens, bpe_tokens)
    new_text = " ".join(bpe_tokens)
    return new_text

def retokenize_file(fname):
    new_tokenizer_name = "OpenAI.BPE"
    new_name = fname + ".retokenized." + new_tokenizer_name
    log.info("Processing file: %s", fname)
    cat2rec = {}
    with open(fname) as fhandle:
        for row in fhandle:
            category, words = row.strip().split(':')
            cat2rec[category] = words.split(',')

    log.info("  saving to %s", new_name)
    with open(new_name, 'w') as fd:
        for cat, recs in cat2rec.items():
            new_recs = []
            for record in recs:
                new_record = retokenize_record(record)
                new_recs.append(new_record)
            fd.write("%s:%s\n" % (cat, ','.join(new_recs)))

def main(args):
    for fname in args:
        retokenize_file(fname)

if __name__ == '__main__':
    main(sys.argv[1:])
    sys.exit(0)
