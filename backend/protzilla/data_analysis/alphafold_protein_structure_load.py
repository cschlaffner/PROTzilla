import pandas as pd
import requests

def fetch_af_protein_structure(uniprot: str) -> dict:
    """
    Fetch AlphaFold protein structure prediction data from the AlphaFold Database.

    :param uniprot: UniProt accession or protein ID
    :type uniprot: str
    :return: Dictionary containing af_structure_df with structure metadata
    :rtype: dict
    :raises ValueError: If no AlphaFold predictions are found for the given protein
    """
    url = f"https://alphafold.ebi.ac.uk/api/prediction/{uniprot}"
    records = requests.get(url, timeout=30).json()
    if not records:
        raise ValueError(f"No AlphaFold DB predictions for {uniprot}")
    r = records[0]

    data = {
        "entryId": r.get("entryId"),
        "uniprotAccession": r.get("uniprotAccession"),
        "uniprotId": r.get("uniprotId"),
        "modelCreatedDate": r.get("modelCreatedDate"),
        "latestVersion": r.get("latestVersion"),
        "uniprotStart": r.get("uniprotStart"),
        "uniprotEnd": r.get("uniprotEnd"),
        "sequenceLength": len(r.get("uniprotSequence", ""))
        if isinstance(r.get("uniprotSequence"), str)
        else None,
    }

    """ Other things we could get:
        "pdbUrl": r.get("pdbUrl"),
        "cifUrl": r.get("cifUrl"),
        "paeDocUrl": r.get("paeDocUrl"),
        "plddtDocUrl": r.get("plddtDocUrl"), """

    af_structure_df = pd.DataFrame([data])

    return {"af_structure_df": af_structure_df}
