import pandas as pd
import requests


def generate_alphafold_multimer_query_json(
    protein_ids: str, number_copies: str
) -> dict:
    # extract contents and make sure they have the same length -> otherwise raise error
    uniprot_ids = protein_ids.split()
    try:
        copies_per_id = [int(input) for input in number_copies.split()]
    except ValueError as e:
        raise ValueError(
            "Invalid copies_per_id: please provide space-separated integers"
        )
    if len(uniprot_ids) != len(number_copies):
        dict(messages={}, tmp_df=pd.DataFrame())

    data_for_query = {
        "name": "_".join(protein_ids.split()) + "_prediction",
        "modelSeeds": [],
        "sequences": [],
        "dialect": "alphafoldserver",
        "version": 1,
    }

    for uniprot_id, copies in zip(uniprot_ids, copies_per_id):
        url = f"https://rest.uniprot.org/uniprotkb/{uniprot_id}.fasta"

        response = requests.get(url)
        response.raise_for_status()  # TODO: was macht das?

        fasta = response.text
        amino_acid_sequence = "".join(
            line.strip() for line in fasta.splitlines() if not line.startswith(">")
        )
        data_for_query["sequences"].append(
            {
                "proteinChain": {
                    "sequence": amino_acid_sequence,
                    "count": copies,
                }
            }
        )

    return dict(messages={}, tmp_df=pd.DataFrame())
