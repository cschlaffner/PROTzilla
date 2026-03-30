import { PluginUIContext } from "molstar/lib/mol-plugin-ui/context";
import { MolScriptBuilder as MS } from "molstar/lib/mol-script/language/builder";

import {
  CrosslinkerInformation,
  CrosslinkerType,
  generateCrosslinkCIF,
} from "./crosslinker-processing";

const CROSSLINKER_COLORS = {
  [CrosslinkerType.ValidIntra]: 0xe03e00, // kräftiges orange-rot
  [CrosslinkerType.InvalidIntra]: 0xfca311, // blasses gelb-orange
  [CrosslinkerType.ValidInter]: 0x8a2be2, // kräftiges lila
  [CrosslinkerType.InvalidInter]: 0xd8b4ff, // blasses lila
};

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
}
