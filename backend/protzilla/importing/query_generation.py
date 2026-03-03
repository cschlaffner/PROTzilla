import json
import logging

import pandas as pd
import requests


def generate_alphafold_multimer_query_json(
    protein_ids: str, number_copies: str, model_seed: int, name: str
) -> dict:
    """
    Generates an AlphaFold Multimer JSON query for a set of UniProt protein IDs.
    For each provided UniProt ID, the corresponding amino acid sequence is fetched
    from the UniProt REST API and added to the query with the specified copy number.
    Format of the json is as defined here: https://github.com/google-deepmind/alphafold/blob/main/server/README.md

    Protein IDs and copy numbers must be provided as space- or comma-separated strings and
    must have the same length. If an invalid copy number is provided or if the
    lengths do not match, an error message is generated and an exception may be raised.

    :param protein_ids: Space- or comma-separated list of UniProt protein IDs (e.g. "P69905 P68871").
    :param number_copies: Space- or comma-separated list of integers specifying the number of copies
                          for each protein ID (e.g. "2 2").
    :param model_seed: Model seed for the AlphaFold query. If -1 we want AlphaFold to use a random seed.
    :param name: How the AlphaFold job and the generated file should be named.
    :return: dict (messages, downloads), downloads contains a dictionary mapping a generated filename
             to the AlphaFold Multimer query JSON string (wrapped in square brackets as required by AlphaFold server)
    :raises ValueError: If the number of copies or the model seeds cannot be parsed as integers.
    :raises requests.exceptions.HTTPError: If fetching a UniProt FASTA sequence fails.
    """
    messages = []

    # extract protein_ids and number of copies per id and make sure they have the same length
    uniprot_ids = protein_ids.replace(",", " ").split()
    try:
        copies_per_id = [
            int(input) for input in number_copies.replace(",", " ").split()
        ]
    except ValueError as e:
        msg = f"Invalid list of number of copies per id: please provide space-separated integers"
        messages.append(
            dict(
                level=logging.ERROR,
                msg=msg,
            )
        )
        raise ValueError(msg)
    if len(uniprot_ids) != len(copies_per_id):
        messages.append(
            dict(
                level=logging.ERROR,
                msg=f"For at least one protein id, the number of copies is missing in the input.",
            )
        )
        return dict(messages=messages, downloads={})
    if min(copies_per_id) < 1:
        messages.append(
            dict(
                level=logging.ERROR,
                msg=f"There can't be a non-positive number of copies.",
            )
        )
        return dict(messages=messages, downloads={})
    if sum(copies_per_id) < 2:
        messages.append(
            dict(
                level=logging.ERROR,
                msg=f"Please use the monomer steps to validate only one protein.",
            )
        )
        return dict(messages=messages, downloads={})

    # create the json query for alphafold
    query = {
        "name": name,
        "modelSeeds": [],
        "sequences": [],
        "dialect": "alphafoldserver",
        "version": 1,
    }

    if model_seed != -1:
        query["modelSeeds"] = [model_seed]

    for uniprot_id, copies in zip(uniprot_ids, copies_per_id):
        url = f"https://rest.uniprot.org/uniprotkb/{uniprot_id}.fasta"

        response = requests.get(url, timeout=20)
        response.raise_for_status()

        fasta = response.text
        amino_acid_sequence = "".join(
            line.strip() for line in fasta.splitlines() if not line.startswith(">")
        )
        query["sequences"].append(
            {
                "proteinChain": {
                    "sequence": amino_acid_sequence,
                    "count": copies,
                }
            }
        )
    query_as_string = f"[{json.dumps(query)}]"
    messages.append(
        dict(
            level=logging.INFO, msg=f"Successfully generated a json file for AlphaFold."
        )
    )
    return dict(
        messages=messages,
        downloads={name: query_as_string},
    )
