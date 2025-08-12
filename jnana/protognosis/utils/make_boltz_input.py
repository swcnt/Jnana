import sys
from getSequence import getseq
import yaml
import re

DEBUG = True

def get_protein_name(s):
    result = re.findall(r'\b[A-Z-]{3,5}[A-Z\d]{1,2}\b',s)
    assert len(result) > 0, "Protein not found!!"
    if DEBUG:
        print(f"protein found! name: {result[0]}")
    return result[0]


def is_protein_present(s):
    result = re.findall(r'\b[A-Z-]{3,5}[A-Z\d]{1,2}\b',s)
    if len(result) > 0:
        return True
    else:
        return False

def prot_to_dict(pname):
    if DEBUG:
        print(f"Protein name input is {pname}")
    content = getseq(pname)
    if DEBUG:
        print(f"Retrieved content: {content}")
    assert len(content) == 2, "Currently only single-sequence proteins are supported"
    
    seq = content[1]
    if DEBUG:
        print(f"Protein sequence: {seq}")

    out_dict = {"version": 1,
            "sequences": {
                "protein": {
                    "id": "A",
                    "sequence":seq

            }
        }
    }

    if DEBUG:
        print(f"Output dictionary: {out_dict}")

    return out_dict

def dict_to_yaml(pdict,fname):
    with open(fname, 'w+') as ff:
        yaml.dump(pdict, ff, sort_keys=False)

def hypo_to_boltz_query(hypo_content, output_path):
    protein_name = get_protein_name(hypo_content)
    template_dict = prot_to_dict(protein_name)
    dict_to_yaml(template_dict, output_path)

def process_report(hypothesis_d: dict):
    protein_info = hypothesis_d['protein_data']
    name_residue_pairs = {}
    print(f"Info passed in: {protein_info}")
    for key in protein_info:
        print(f"Searching protein {key}")
        p_name = protein_info[key]["name"]
        p_res =  protein_info[key]["residue_connect"]
        name_residue_pairs[p_name] = p_res
    # get sequences to check
    for pname in name_residue_pairs:
        content = getseq(pname)
        print(f"Protein Sequence: {content}")




"""
if __name__ == "__main__":
    test_string = "Proteins such as ALKBH1 are very interesting to examine in the context of AI agent hypothesis generation at Argonne. The elo is 4214 today."
    hypo_to_boltz_query(test_string,"boltz_feed/hypoextract.yaml")

if  __name__ == "__main__":
    try:
        prot_name = sys.argv[1]
        out_fname = sys.argv[2]
    except:
        print("ERROR:arguments are [protein name] [output filename]")
        sys.exit(1)

    info_dict = prot_to_dict(prot_name)
    dict_to_yaml(info_dict,out_fname)
"""
    



