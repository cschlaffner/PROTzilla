import { useNotification } from "@protzilla/app";
import { callApi } from "@protzilla/utils";
import { OrderedSet } from "molstar/lib/mol-data/int";
import { Loci } from "molstar/lib/mol-model/loci";
import { StructureElement } from "molstar/lib/mol-model/structure";
import { PluginUIContext } from "molstar/lib/mol-plugin-ui/context";
import { MolScriptBuilder as MS } from "molstar/lib/mol-script/language/builder";

import {
  CrosslinkerInformation,
  CrosslinkerType,
  generateCrosslinkCIF,
} from "./crosslinker-processing";
import { CROSSLINK_DEFAULT_COLORS, CrosslinkColors } from "./molstar-viewer.config";

type PluginWithCrosslinks = PluginUIContext & {
  crosslinkerGroups?: Record<CrosslinkerType, string[]>;
};

interface LabelProvider {
  label: (loci: Loci) => string | undefined;
}

export async function addCrosslinks(
  plugin: PluginUIContext,
  cifText: string,
  crosslinks: CrosslinkerInformation[],
  crosslinkColors: CrosslinkColors,
) {
  const { crosslinkerCifText: crosslinkerCifText, crosslinkerGroups: crosslinkerGroups } =
    generateCrosslinkCIF(cifText, crosslinks);

  const lineData = await plugin.builders.data.rawData({
    data: crosslinkerCifText,
    label: "line",
  });
  const lineTrajectory = await plugin.builders.structure.parseTrajectory(lineData, "mmcif");
  const lineModel = await plugin.builders.structure.createModel(lineTrajectory);
  const lineStructure = await plugin.builders.structure.createStructure(lineModel);

  for (const type of Object.values(CrosslinkerType)) {
    const atomIds = crosslinkerGroups[type];

    const expression = MS.struct.generator.atomGroups({
      "atom-test": MS.core.set.has([MS.set(...atomIds), MS.ammp("label_atom_id")]),
    });

    const component = await plugin.builders.structure.tryCreateComponentFromExpression(
      lineStructure,
      expression,
      type,
    );

    if (component) {
      await plugin.builders.structure.representation.addRepresentation(component, {
        type: "line",
        color: "uniform",
        colorParams: { value: crosslinkColors[type] },
      });
    }
  }

  await highlightCrosslinkBindingSites(plugin, crosslinks);

  (plugin as PluginWithCrosslinks).crosslinkerGroups = crosslinkerGroups;
}

export function overrideLabels(plugin: PluginUIContext, crosslinkColors: CrosslinkColors) {
  const labelManager = plugin.managers.lociLabels as {
    providers: LabelProvider[];
    addProvider: (p: LabelProvider) => void;
  };

  const defaultProviders = [...labelManager.providers];
  labelManager.providers = [];

  const getDefaultLabel = (loci: Loci) =>
    defaultProviders
      .map((p) => p.label(loci))
      .filter(Boolean)
      .join(" | ");

  const getAtomIdsFromLoci = (loci: StructureElement.Loci): string[] => {
    const ids: string[] = [];

    for (const element of loci.elements) {
      const { indices, unit } = element;
      const atoms = unit.model.atomicHierarchy.atoms.label_atom_id;

      for (let i = 0; i < OrderedSet.size(indices); i++) {
        const idx = OrderedSet.getAt(indices, i);
        ids.push(atoms.value(idx));
      }
    }

    return [...new Set(ids)];
  };

  const findMatchingAtomPair = (ids: string[]) => {
    // since the atom-pair of one crosslink is always XL...A, XL...B those are the two ids we need
    // (there can be atoms of other crosslinks at the exact same place, which is why they are listed here)
    const seen = new Map<string, string>();

    for (const id of ids) {
      const number = /\d+/.exec(id)?.[0];
      if (!number) continue;

      const other = seen.get(number);

      if (other) {
        return [other, id] as const;
      }

      seen.set(number, id);
    }

    return undefined;
  };

  labelManager.addProvider({
    label: (loci) => {
      if (loci.kind !== "element-loci") {
        return getDefaultLabel(loci);
      }

      const crosslinkerGroups = (plugin as PluginWithCrosslinks).crosslinkerGroups;
      if (!crosslinkerGroups) {
        return getDefaultLabel(loci);
      }

      const atomIds = getAtomIdsFromLoci(loci);
      const pair = findMatchingAtomPair(atomIds);

      if (!pair) {
        return getDefaultLabel(loci);
      }

      const [atomId1, atomId2] = pair;

      const match = Object.entries(crosslinkerGroups).find(
        ([, ids]) => ids.includes(atomId1) && ids.includes(atomId2),
      );

      if (!match) {
        return getDefaultLabel(loci);
      }

      const [groupName] = match as [CrosslinkerType, string[]];
      const color = `#${crosslinkColors[groupName].toString(16).padStart(6, "0")}`;
      return `<span style="color:${color}">${groupName}</span>`;
    },
  });
}

export const initCrosslinkColors = async (): Promise<CrosslinkColors> => {
  try {
    const userColors = await callApi("get_cl_colors");

    if (userColors && Object.keys(userColors).length > 0) {
      return {
        ...CROSSLINK_DEFAULT_COLORS,
        ...userColors,
      };
    }

    return CROSSLINK_DEFAULT_COLORS;
  } catch {
    return CROSSLINK_DEFAULT_COLORS;
  }
};

async function highlightCrosslinkBindingSites(
  plugin: PluginUIContext,
  crosslinks: CrosslinkerInformation[],
) {
  const residuesPerChain = new Map<string, Set<number>>();

  function addResidue(chainId: string, seqId: number) {
    let residues = residuesPerChain.get(chainId);

    if (!residues) {
      residues = new Set<number>();
      residuesPerChain.set(chainId, residues);
    }

    residues.add(seqId);
  }

  for (const crosslink of crosslinks) {
    addResidue(crosslink.chainId1, crosslink.crosslinkerPosition1);

    addResidue(crosslink.chainId2, crosslink.crosslinkerPosition2);
  }

  await highlightSpecificResidues(plugin, residuesPerChain);
}

export async function highlightSpecificResidues(
  plugin: PluginUIContext,
  residuesPerChain: Map<string, Set<number>>,
) {
  const structure = plugin.managers.structure.hierarchy.current.structures[0];

  const selections = [...residuesPerChain.entries()].map(([chainId, residues]) =>
    MS.struct.generator.atomGroups({
      "residue-test": MS.core.logic.and([
        MS.core.set.has([MS.set(...residues), MS.ammp("label_seq_id")]),
        MS.core.rel.eq([MS.ammp("label_asym_id"), chainId]),
      ]),
    }),
  );

  if (selections.length === 0) return;

  const expression =
    selections.length === 1 ? selections[0] : MS.struct.combinator.merge(selections);

  const component = await plugin.builders.structure.tryCreateComponentFromExpression(
    structure.cell,
    expression,
    "crosslink-binding-sites",
  );

  if (!component) return;

  await plugin.builders.structure.representation.addRepresentation(component, {
    type: "ball-and-stick",
    color: "chain-id",
  });
}

export function handleError(
  error: unknown,
  errorTitle: string,
  notify: ReturnType<typeof useNotification>,
) {
  const errorMessage =
    typeof error === "string" ? error : error instanceof Error ? error.message : "Unknown error";
  notify({
    title: errorTitle,
    message: errorMessage,
    type: "error",
    isClosingAutomatically: true,
  });
}
