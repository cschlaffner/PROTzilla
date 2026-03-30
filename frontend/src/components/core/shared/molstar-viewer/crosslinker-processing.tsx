export interface CrosslinkerInformation {
  crosslinkerPosition1: number;
  crosslinkerPosition2: number;
  isValid: boolean;
  isIntraCrosslink: boolean;
  reactiveAtom1?: string;
  reactiveAtom2?: string;
}

interface CrosslinkerAtom {
  x: number;
  y: number;
  z: number;
  chain: string;
  seqPos: number;
  atomId: string;
}

interface AtomSiteIndices {
  atomIdIdx: number;
  seqIdIdx: number;
  chainIdIdx: number;
  xCoordIdx: number;
  yCoordIdx: number;
  zCoordIdx: number;
}

export enum CrosslinkerType {
  ValidIntra = "valid-intra-crosslink",
  InvalidIntra = "invalid-intra-crosslink",
  ValidInter = "valid-inter-crosslink",
  InvalidInter = "invalid-inter-crosslink",
}

// ------------------------- public API: -------------------------

export function generateCrosslinkCIF(
  cifString: string,
  crosslinks: CrosslinkerInformation[],
): { crosslinkerCifText: string; crosslinkerGroups: Record<CrosslinkerType, string[]> } {
  const atomLines: string[] = [];
  const connectionLines: string[] = [];
  let connectionId = 1;

  const crosslinkGroups: Record<CrosslinkerType, string[]> = Object.values(CrosslinkerType).reduce(
    (crosslinkGroups, type) => {
      crosslinkGroups[type] = [];
      return crosslinkGroups;
    },
    {} as Record<CrosslinkerType, string[]>,
  );

  for (const crosslink of crosslinks) {
    const [atom1, atom2] = extractCrosslinkerAtoms(cifString, crosslink);

    if (atom1 && atom2) {
      const atom1Id = `XL${String(connectionId)}A`;
      const atom2Id = `XL${String(connectionId)}B`;

      const crosslinkType = getCrosslinkerType(crosslink);
      crosslinkGroups[crosslinkType].push(atom1Id, atom2Id);

      const atom1Line = [
        `ATOM ${String(connectionId * 2 - 1)} ${atom1Id} ${atom1Id}`,
        `LIN ${atom1.chain} ${String(atom1.seqPos)}`,
        `${String(atom1.x)} ${String(atom1.y)} ${String(atom1.z)} 1.0 0.0`,
      ].join(" ");

      const atom2Line = [
        `ATOM ${String(connectionId * 2)} ${atom2Id} ${atom2Id}`,
        `LIN ${atom2.chain} ${String(atom2.seqPos)}`,
        `${String(atom2.x)} ${String(atom2.y)} ${String(atom2.z)} 1.0 0.0`,
      ].join(" ");

      atomLines.push(atom1Line);
      atomLines.push(atom2Line);

      const connectionLine = [
        `${String(connectionId)} covalent ${atom1Id}`,
        `X ${atom1.chain} ${String(atom1.seqPos)} ${atom2Id}`,
        `X ${atom2.chain} ${String(atom2.seqPos)}`,
      ].join(" ");

      connectionLines.push(connectionLine);

      connectionId++;
    }
  }

  const crosslinkCifText = `
    data_crosslink

    loop_
    _atom_site.group_PDB
    _atom_site.id
    _atom_site.type_symbol
    _atom_site.label_atom_id
    _atom_site.label_comp_id
    _atom_site.label_asym_id
    _atom_site.label_seq_id
    _atom_site.Cartn_x
    _atom_site.Cartn_y
    _atom_site.Cartn_z
    _atom_site.occupancy
    _atom_site.B_iso_or_equiv
    ${atomLines.join("\n")}

    loop_
    _struct_conn.id
    _struct_conn.conn_type_id
    _struct_conn.ptnr1_label_atom_id
    _struct_conn.ptnr1_label_comp_id
    _struct_conn.ptnr1_label_asym_id
    _struct_conn.ptnr1_label_seq_id
    _struct_conn.ptnr2_label_atom_id
    _struct_conn.ptnr2_label_comp_id
    _struct_conn.ptnr2_label_asym_id
    _struct_conn.ptnr2_label_seq_id
    ${connectionLines.join("\n")}
    `;

  return { crosslinkerCifText: crosslinkCifText, crosslinkerGroups: crosslinkGroups };
}

// ------------------------- internal helpers: -------------------------

function getReactiveAtom(reactiveAtom?: string): string {
  // right now we always return the central C atom
  // later we might want to return the reactive atom of the amino acid residue of the specific amino acid type
  // then we just have to define a reactiveAtom
  if (!reactiveAtom) return "CA";
  const mapping: Record<string, string> = {
    K: "NZ",
    S: "OG",
    T: "OG1",
  };
  return mapping[reactiveAtom] || "CA";
}

function findCrosslinkerAtomCoordinates(
  cifString: string,
  crosslinkerAtomId: string,
  crosslinkerSeqPos: number,
): CrosslinkerAtom | null {
  const lines = cifString.split(/\r?\n/);

  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) continue;
    const tokens = trimmed.split(/\s+/);
    if (tokens[0] !== "ATOM" && tokens[0] !== "HETATM") continue;

    const cifIndices = getCifAtomSiteIndices(cifString);

    const lineAtomId = tokens[cifIndices.atomIdIdx];
    const lineSeqPos = parseInt(tokens[cifIndices.seqIdIdx], 10);

    if (lineAtomId === crosslinkerAtomId && lineSeqPos === crosslinkerSeqPos) {
      return {
        x: parseFloat(tokens[cifIndices.xCoordIdx]),
        y: parseFloat(tokens[cifIndices.yCoordIdx]),
        z: parseFloat(tokens[cifIndices.zCoordIdx]),
        chain: tokens[cifIndices.chainIdIdx],
        seqPos: lineSeqPos,
        atomId: lineAtomId,
      };
    }
  }

  throw new Error(`No atom found for seq=${String(crosslinkerSeqPos)}, atom=${crosslinkerAtomId}`);
}

function extractCrosslinkerAtoms(
  cifString: string,
  crosslink: CrosslinkerInformation,
): [CrosslinkerAtom | null, CrosslinkerAtom | null] {
  const reactiveAtom1 = getReactiveAtom(crosslink.reactiveAtom1);
  const atom1 = findCrosslinkerAtomCoordinates(
    cifString,
    reactiveAtom1,
    crosslink.crosslinkerPosition1,
  );

  const reactiveAtom2 = getReactiveAtom(crosslink.reactiveAtom2);
  const atom2 = findCrosslinkerAtomCoordinates(
    cifString,
    reactiveAtom2,
    crosslink.crosslinkerPosition2,
  );

  return [atom1, atom2];
}

function getCifAtomSiteIndices(cifString: string): AtomSiteIndices {
  const lines = cifString.split(/\r?\n/);
  const atomSiteLines = lines.filter((line) => line.startsWith("_atom_site."));

  const indices: Record<string, number> = {};
  atomSiteLines.forEach((line, idx) => {
    const colName = line.trim();
    indices[colName] = idx;
  });

  const atomIdColNames = ["_atom_site.label_atom_id", "_atom_site.auth_atom_id"];
  const seqIdColNames = ["_atom_site.label_seq_id", "_atom_site.auth_seq_id"];
  const chainIdColNames = ["_atom_site.label_asym_id", "_atom_site.auth_asym_id"];
  const xCoordColNames = ["_atom_site.Cartn_x"];
  const yCoordColNames = ["_atom_site.Cartn_y"];
  const zCoordColNames = ["_atom_site.Cartn_z"];

  function findFirst(names: string[]): number {
    for (const name of names) {
      if (name in indices) return indices[name];
    }
    throw new Error(`None of the column names found: ${names.join(", ")}`);
  }

  return {
    atomIdIdx: findFirst(atomIdColNames),
    seqIdIdx: findFirst(seqIdColNames),
    chainIdIdx: findFirst(chainIdColNames),
    xCoordIdx: findFirst(xCoordColNames),
    yCoordIdx: findFirst(yCoordColNames),
    zCoordIdx: findFirst(zCoordColNames),
  };
}

function getCrosslinkerType(crosslink: CrosslinkerInformation): CrosslinkerType {
  if (crosslink.isIntraCrosslink) {
    return crosslink.isValid ? CrosslinkerType.ValidIntra : CrosslinkerType.InvalidIntra;
  } else {
    return crosslink.isValid ? CrosslinkerType.ValidInter : CrosslinkerType.InvalidInter;
  }
}
