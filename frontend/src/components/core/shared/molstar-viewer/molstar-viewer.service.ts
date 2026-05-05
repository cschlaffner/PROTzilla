import { useNotification } from "@protzilla/app";
import { OrderedSet } from "molstar/lib/mol-data/int";
import { PluginUIContext } from "molstar/lib/mol-plugin-ui/context";
import { MolScriptBuilder as MS } from "molstar/lib/mol-script/language/builder";

import {
  CrosslinkerInformation,
  CrosslinkerType,
  generateCrosslinkCIF,
} from "./crosslinker-processing";
import { CROSSLINKER_COLORS } from "./molstar-viewer.config";

type PluginWithCrosslinks = PluginUIContext & {
  crosslinkerGroups?: Record<CrosslinkerType, string[]>;
};

interface LabelProvider {
  label: (loci: any) => string | undefined;
}

export async function addCrosslinks(
  plugin: PluginUIContext,
  cifText: string,
  crosslinks: CrosslinkerInformation[],
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
        colorParams: { value: CROSSLINKER_COLORS[type] },
      });
    }
  }

  (plugin as PluginWithCrosslinks).crosslinkerGroups = crosslinkerGroups;
}

export function overrideLabels(plugin: PluginUIContext) {
  const labelManager = plugin.managers.lociLabels as {
    providers: LabelProvider[];
    addProvider: (p: LabelProvider) => void;
  };

  const defaultLabelProviders = [...labelManager.providers];
  labelManager.providers = [];

  plugin.managers.lociLabels.addProvider({
    label: (loci) => {
      if (loci.kind !== "element-loci") {
        return defaultLabelProviders
          .map((p) => p.label(loci))
          .filter(Boolean)
          .join(" | ");
      }

      const structureElements = loci.elements[0];
      const firstElement = OrderedSet.getAt(structureElements.indices, 0);

      const crosslinkerGroups = (plugin as PluginWithCrosslinks).crosslinkerGroups;
      if (!crosslinkerGroups) {
        return defaultLabelProviders
          .map((p) => p.label(loci))
          .filter(Boolean)
          .join(" | ");
      }

      const atomId =
        structureElements.unit.model.atomicHierarchy.atoms.label_atom_id.value(firstElement);

      const crosslinkerGroupWithAtomIds = Object.entries(crosslinkerGroups).find(([, ids]) =>
        ids.includes(atomId),
      );

      if (crosslinkerGroupWithAtomIds) {
        const [crosslinkerGroupName] = crosslinkerGroupWithAtomIds as [CrosslinkerType, string[]];
        const stringColor = getCrosslinkerColor(crosslinkerGroupName);
        return `<span style="color:${stringColor}">${crosslinkerGroupName}</span>`;
      }

      return defaultLabelProviders
        .map((p) => p.label(loci))
        .filter(Boolean)
        .join(" | ");
    },
  });
}

export function getCrosslinkerColor(type: CrosslinkerType) {
  return `#${CROSSLINKER_COLORS[type].toString(16).padStart(6, "0")}`;
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
