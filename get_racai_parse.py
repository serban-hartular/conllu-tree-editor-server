import json
import urllib.request

CHILDREN = 'children'

teprolin_url = 'http://relate.racai.ro:5000/'
teprolin_cmd = 'process'
data_prefix = "text="

def get_racai_parse(text : str, lang : str) -> list:
    """
    Takes a text, asks the racai site to parse it, and returns the tree as a conllu-format dict
    with a list of children. Currently only returns one sentence
    :param text: Sentence text (in Romanian)
    :return: list of dicts, each dict a tree
    """
    racai_obj = get_racai_object(text)
    text_list, sentence_list = racai_json_to_sentence_list(racai_obj)
    if not sentence_list or not sentence_list[0]: return []
    tree_list = []
    for text, sentence in zip(text_list, sentence_list):
        sentence = [teprolin_token_2_conllu(w) for w in sentence]
        tree_list.append(conllu_list_to_tree(sentence))
    return tree_list

def get_racai_object(text : str):
    teprolin_request = teprolin_url + teprolin_cmd
    text = data_prefix + text
    with urllib.request.urlopen(teprolin_request, text.encode('utf-8')) as response:
        html = response.read()
    parse = html.decode('utf-8')
    parse = json.loads(parse)
    return parse


def racai_json_to_sentence_list(racai_json_dict : dict) -> tuple:
    """
    Used to extract info from json object returned by racai site.
    :param racai_json_dict: json object/dict received from racai request
    :return: list of sentence texts, list of sentence parses (which are also dicts)
    """
    teprolin_result = racai_json_dict['teprolin-result']
    parse_list = teprolin_result['tokenized']
    text_list = teprolin_result['sentences']
    return text_list, parse_list

def conllu_list_to_tree(sentence : list) -> dict:
    # now build tree
    tree = [w for w in sentence]
    for w in tree: # add children list
        w[CHILDREN] = []
    for word in sentence:
        # find head
        head = [h for h in sentence if h['ID'] == word['HEAD']]
        if len(head) == 1:
            head = head[0]
            head[CHILDREN].append(word)
            tree.remove(word)
    if len(tree) == 1:
        return tree[0]
    return None


connlu_fields = ('ID', 'FORM', 'LEMMA', 'UPOS', 'XPOS', 'FEATS', 'HEAD', 'DEPREL', 'DEPS', 'MISC')
conllu_field_dict = {'ID':'_id', 'FORM':'_wordform', 'LEMMA':'_lemma', 'UPOS':'_ctg', 'XPOS':'_msd',
                     'FEATS':None, 'HEAD':'_head', 'DEPREL':'_deprel', 'DEPS':None, 'MISC':None}

import ro_msd_types

def teprolin_token_2_conllu(teprolin : dict) -> dict:
    conllu = dict()
    for field in connlu_fields:
        t_key = conllu_field_dict[field]
        conllu[field] = teprolin[t_key] if t_key else '_'
    # get UPOS from XPOS
    if 'DEPREL' in conllu and conllu['DEPREL'] == 'punct':
        conllu['UPOS'] = 'PUNCT'
    else:
        conllu['UPOS'] = MSD_to_UPOS(teprolin['_msd'], ro_msd_types.msd_to_upos_dict)

    return conllu

def MSD_to_attribs(MSD: str, MSD_dict : dict) -> dict:
    attribs = dict()
    for pos in range(0, len(MSD)):
        code = MSD[pos]
        if code == '-': continue
        if not MSD_dict[MSD[0]]:
            raise Exception('Error in MSD %s type %s' % (MSD, MSD[0]))
        if not MSD_dict[MSD[0]][pos]:
            raise Exception('Error in MSD %s at pos %d' % (MSD, pos))
        if not MSD_dict[MSD[0]][pos][code]:
            raise Exception('Error in MSD %s at pos %d, code %s' % (MSD, pos, code))
        (attribute, value) =  MSD_dict[MSD[0]][pos][code]
        attribs[attribute] = value
    return attribs

def MSD_to_UPOS(msd : str, msd_to_upos_dict : dict) -> str:
    key = msd[0]
    # try first letter
    if key in msd_to_upos_dict:
        return msd_to_upos_dict[key]
    # try first two letters
    key = msd[0:2]
    if key in msd_to_upos_dict:
        return msd_to_upos_dict[key]
    # unknown. return msd and hope
    return msd