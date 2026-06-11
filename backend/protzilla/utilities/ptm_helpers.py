"""
PTM helper functions, taken and adapted from https://github.com/usiGrabber/usiGrabber
"""

import re
from string import digits


def remove_brackets_before_index(s: str, cut_index: int) -> str:
    """
    Remove parentheses and their contents before a specified index in a string.
    This function removes all opening and closing brackets that appear before
    the specified cut_index position, along with any text contained within those
    brackets. Text at or after the cut_index is preserved, even if it contains
    brackets.
    Args:
        s (str): The input string to process.
        cut_index (int): The index position before which brackets should be removed.
                        Positions at or after this index are preserved.
    Returns:
        str: A new string with brackets and their contents removed from positions
             before cut_index, while preserving all text from cut_index onwards.
    Example:
        >>> remove_brackets_before_index("hello(world)test", 5)
        "hello(world)test"
        >>> remove_brackets_before_index("(a)b(c)d", 5)
        "b(c)d"
    """

    result = []
    i = 0
    n = len(s)
    cut_index -= 1

    depth = 0
    while i < n:
        if s[i] == "(" and i < cut_index:
            depth += 1
        elif s[i] == ")" and i < cut_index:
            depth -= 1
        elif depth == 0 or i >= cut_index:
            result.append(s[i])
        i += 1
    return "".join(result)


def get_mods_with_positions(
    seq: str, mods: list[str]
) -> tuple[dict[str, list[int]], str]:
    """
    Extract modifications and their positions from a sequence string.
    This function searches for modifications (specified in the mods list) within a sequence string.
    Each modification is expected to be enclosed in parentheses, e.g., "(MOD_NAME)".
    The function identifies all occurrences of each modification, records their positions,
    and removes them from the sequence.
    Args:
        seq (str): The sequence string containing modifications in the format "(MOD_NAME)".
        mods (list[str]): A list of modification identifiers to search for in the sequence.
    Returns:
        tuple[dict[str, list[int]], str]: A tuple containing:
            - A dictionary mapping each modification name to a list of positions where it was found.
            - The cleaned sequence string with all modifications removed.
    Example:
        >>> seq = "ABC(MOD1)DEF(MOD2)GHI(MOD1)"
        >>> mods = ["MOD1", "MOD2"]
        >>> positions, clean_seq = get_mods_with_positions(seq, mods)
        >>> positions
        {'MOD1': [3, 9], 'MOD2': [6]}
        >>> clean_seq
        'ABCDEFGHI'
    """

    mod_with_pos: dict[str, list[int]] = {mod: [] for mod in mods}
    for mod in mods:
        while seq.find(f"({mod})") != -1:
            cleaned_seq = remove_brackets_before_index(seq, seq.find(f"({mod})"))
            mod_index = cleaned_seq.find(f"({mod})")
            mod_with_pos[mod].append(mod_index)

            seq_index = seq.find(f"({mod})")
            seq = seq[:seq_index] + seq[seq_index + len(f"({mod})") :]
    # validation that no modifications where found that weren't passed as modifications to search for
    # shouldn't occur in well-formed files, but can happen if the evidence was manually edited
    # see issue #438
    remainder = re.findall(r"\(\w+?\)", seq)
    if remainder:
        raise ValueError(
            f"Sequence has remaining modifications {', '.join(remainder)} after searching for modifications {', '.join(mods)} that were passed"
        )
    return mod_with_pos, seq


def get_residues_for_mods_with_positions(
    seq: str, mod_with_pos: dict[str, list[int]]
) -> dict[str, list[tuple[int, str]]]:
    """
    Map modification types to their positions and corresponding residues in a sequence.
    This function takes a sequence and modification data, then retrieves the amino acid
    residue at each modification position. Special handling is applied for terminal
    positions: position 0 represents the N-terminus (marked as 'N') and position equal
    to sequence length represents the C-terminus (marked as 'C').
    Args:
        seq (str): The amino acid sequence.
        mods (list[str]): List of modification types to initialize in the result dictionary.
        mod_with_pos (dict[str, list[int]]): Dictionary mapping modification types to lists
                                             of positions where they occur in the sequence.
    Returns:
        dict[str, list[tuple[int, str]]]: Dictionary mapping each modification type to a list
                                          of tuples containing (position, residue) pairs.
                                          Terminal residues are represented as 'N' for N-terminus
                                          and 'C' for C-terminus.
    Example:
        >>> seq = "PEPTIDE"
        >>> mod_with_pos = {"Phospho": [0, 4], "Acetyl": [7]}
        >>> get_residues_for_mods_with_positions(seq, mods, mod_with_pos)
        {'Phospho': [(0, 'N'), (4, 'T')], 'Acetyl': [(7, 'C')]}
    """
    mod_with_pos_residues: dict[str, list[tuple[int, str]]] = {
        mod: [] for mod in mod_with_pos
    }

    for mod, positions in mod_with_pos.items():
        for position in positions:
            residue = ""
            if position == 0:
                residue = "N"
            elif position == len(seq):
                residue = "C"
            else:
                residue = seq[position - 1 : position]
            mod_with_pos_residues[mod].append((position, residue))

    return mod_with_pos_residues


def clear_mod_name(
    mods_with_pos_residues: dict[str, list[tuple[int, str]]],
) -> dict[str, list[tuple[int, str]]]:
    """
    Simplify modification names by removing additional details.
    This function processes a dictionary mapping modification names to their positions
    and corresponding residues. It simplifies each modification name by retaining only
    the primary identifier (the substring before the first space) and constructs a new
    dictionary with these simplified names.
    Args:
        mods_with_pos_residues (dict[str, list[tuple[int, str]]]): A dictionary mapping
            full modification names to lists of (position, residue) tuples.
    Returns:
        dict[str, list[tuple[int, str]]]: A new dictionary mapping simplified modification
            names to lists of (position, residue) tuples.
    """
    modnames_with_pos_residues: dict[str, list[tuple[int, str]]] = {}
    for mod, position_residue in mods_with_pos_residues.items():
        clean_mod_name = mod.split(" ")[0]
        modnames_with_pos_residues[clean_mod_name] = position_residue
    return modnames_with_pos_residues


def extract_mods(sequence: str, mods: list[str]) -> dict[str, list[tuple[int, str]]]:
    """
    Extract and simplify modification data from a sequence string.
    This function identifies modifications within a sequence string, retrieves their
    positions and corresponding residues, and simplifies the modification names.
    Args:
        sequence (str): The sequence string containing modifications.
        mods (list[str]): A list of modification identifiers to search for in the sequence.
    Returns:
        dict[str, list[tuple[int, str]]]: A dictionary mapping simplified modification
            names to lists of (position, residue) tuples.
    """
    seq = str(sequence).strip("_")

    try:
        mod_with_pos, seq = get_mods_with_positions(seq, mods)
        mod_with_pos_residues = get_residues_for_mods_with_positions(seq, mod_with_pos)
        modnames_with_pos_residues = clear_mod_name(mod_with_pos_residues)
        return modnames_with_pos_residues
    except Exception as e:
        raise ValueError(
            f"An error occurred while processing modifications of sequence {sequence}"
        ) from e


def clean_mod_list_of_numbers(mod_list: list[str]) -> list[str]:
    """
    Remove leading numbers and spaces from modification names in a list.
    This function processes a list of modification names, stripping any leading
    numeric characters and spaces from each name.
    Args:
        mod_list (list[str]): A list of modification names, potentially with leading numbers.
    Returns:
        list[str]: A new list of modification names with leading numbers and spaces removed.
    """
    cleaned_mods = []
    for mod in mod_list:
        mod = str(mod)
        cleaned_mods.append(mod.lstrip(digits).lstrip(" "))
    return cleaned_mods


def simple_mod_name(mod_name: str) -> str:
    """
    Simplify a modification name by removing leading numbers and spaces
    as well as cutting at the first following whitespace.
    This function takes a modification name string and removes any leading
    numeric characters and spaces and removes anything after the pure modification
    name to return a cleaner version of the name.
    Args:
        mod_name (str): The original modification name (i.e. Oxidation (M)).
    Returns:
        str: The simplified modification name (i.e. Oxidation).
    """
    mod_name = str(mod_name)
    return mod_name.lstrip(digits).lstrip(" ").split(" ")[0]
