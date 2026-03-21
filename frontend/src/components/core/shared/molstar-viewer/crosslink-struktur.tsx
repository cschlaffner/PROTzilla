export interface CrosslinkPosition {
  crosslinkerPosition1: number;
  crosslinkerPosition2: number;
  aa1?: string;
  aa2?: string;
}

export interface CrosslinkAtom {
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

function getReactiveAtom(aa?: string): string {
  // right now we always return the central C atom
  // later we might want to return the reactive atom of the amino acid residue of the specific amino acid type
  // then we just have to define aa
  if (!aa) return "CA";
  const mapping: Record<string, string> = {
    K: "NZ",
    S: "OG",
    T: "OG1",
  };
  return mapping[aa] || "CA";
}

function findCrosslinkAtomCoordinates(
  cifString: string,
  atomId: string,
  seqPos: number,
): CrosslinkAtom | null {
  const lines = cifString.split(/\r?\n/);

  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) continue;
    const tokens = trimmed.split(/\s+/);
    if (tokens[0] !== "ATOM" && tokens[0] !== "HETATM") continue;

    const cifIndices = getCifAtomSiteIndices(cifString);

    const atomName = tokens[cifIndices.atomIdIdx];
    const resSeq = parseInt(tokens[cifIndices.seqIdIdx], 10);

    if (atomName === atomId && resSeq === seqPos) {
      return {
        x: parseFloat(tokens[cifIndices.xCoordIdx]),
        y: parseFloat(tokens[cifIndices.yCoordIdx]),
        z: parseFloat(tokens[cifIndices.zCoordIdx]),
        chain: tokens[cifIndices.chainIdIdx],
        seqPos: resSeq,
        atomId: atomName,
      };
    }
  }

  throw new Error(`No atom found for seq=${String(seqPos)}, atom=${atomId}`);
}

function extractCrosslinkAtoms(
  cifString: string,
  crosslink: CrosslinkPosition,
): [CrosslinkAtom | null, CrosslinkAtom | null] {
  const reactiveAtom1 = getReactiveAtom(crosslink.aa1);
  const atom1 = findCrosslinkAtomCoordinates(
    cifString,
    reactiveAtom1,
    crosslink.crosslinkerPosition1,
  );

  const reactiveAtom2 = getReactiveAtom(crosslink.aa2);
  const atom2 = findCrosslinkAtomCoordinates(
    cifString,
    reactiveAtom2,
    crosslink.crosslinkerPosition2,
  );

  return [atom1, atom2];
}

export function generateCrosslinkCIF(cifString: string, crosslinks: CrosslinkPosition[]): string {
  const atomLines: string[] = [];
  const structConnLines: string[] = [];
  let structConnId = 1;

  for (const crosslink of crosslinks) {
    const [atom1, atom2] = extractCrosslinkAtoms(cifString, crosslink);

    if (atom1 && atom2) {
      const atom1Id = `XL${String(structConnId)}A`;
      const atom2Id = `XL${String(structConnId)}B`;

      const atom1Line = `ATOM ${String(structConnId * 2 - 1)} ${atom1Id} ${atom1Id} LIN ${atom1.chain} ${String(atom1.seqPos)} \
        ${String(atom1.x)} ${String(atom1.y)} ${String(atom1.z)} 1.0 0.0`;

      const atom2Line = `ATOM ${String(structConnId * 2)} ${atom2Id} ${atom2Id} LIN ${atom2.chain} ${String(atom2.seqPos)} \
        ${String(atom2.x)} ${String(atom2.y)} ${String(atom2.z)} 1.0 0.0`;

      atomLines.push(atom1Line);
      atomLines.push(atom2Line);

      const connLine = `${String(structConnId)} covalent ${atom1Id} X ${atom1.chain} ${String(atom1.seqPos)} \
        ${atom2Id} X ${atom2.chain} ${String(atom2.seqPos)}`;

      structConnLines.push(connLine);

      structConnId++;
    }
  }

  const cifCrosslink = `
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
    ${structConnLines.join("\n")}
    `;

  return cifCrosslink;
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
