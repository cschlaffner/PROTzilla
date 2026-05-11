import { useNotification } from "@protzilla/app";
import { callApi } from "@protzilla/utils";
import { PluginUIContext } from "molstar/lib/mol-plugin-ui/context";
import { MolScriptBuilder as MS } from "molstar/lib/mol-script/language/builder";

import {
  CrosslinkerInformation,
  CrosslinkerType,
  generateCrosslinkCIF,
} from "./crosslinker-processing";
import { CROSSLINK_DEFAULT_COLORS, CrosslinkColors } from "./molstar-viewer.config";

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
