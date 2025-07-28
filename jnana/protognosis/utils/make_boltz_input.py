import sys
from getSequence import getseq
import yaml

DEBUG = False

def prot_to_dict(pname):
    if DEBUG:
        print(f"Protein name input is {prot_name}")
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

if  __name__ == "__main__":
    try:
        prot_name = sys.argv[1]
        out_fname = sys.argv[2]
    except:
        print("ERROR:arguments are [protein name] [output filename]")
        sys.exit(1)

    info_dict = prot_to_dict(prot_name)
    dict_to_yaml(info_dict,out_fname)

    



