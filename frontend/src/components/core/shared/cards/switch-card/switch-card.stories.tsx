import { Meta, StoryFn } from "@storybook/react";
import { SwitchComponent } from "utils/protzilla-types";

import { SwitchCard, SwitchCardProps } from "./";
import { PlotComponent } from "../../plot";

export default {
  component: SwitchCard,
  title: "Switch Card",
} as Meta<SwitchCardProps>;

const Template: StoryFn<SwitchCardProps> = (args) => <SwitchCard {...args} />;

const plotData: Partial<Plotly.Data>[] = [
  {
    x: ["A", "B", "C", "D"],
    y: [10, 20, 30, 40],
    type: "bar",
    marker: { color: "purple" },
  },
];

const plotLayout: Partial<Plotly.Layout> = {
  title: { text: "Title" },
  xaxis: {
    anchor: "y",
    domain: [0.0, 1.0],
    title: { text: "Categories" },
  },
  yaxis: {
    anchor: "x",
    domain: [0.0, 1.0],
    title: { text: "Values" },
  },
};

const components: SwitchComponent[] = [
  { name: "Plot", value: <PlotComponent data={plotData} layout={plotLayout} /> },
  { name: "Table", value: <p>Caution, construction is in progress here! Come back later</p> },
];

export const Default = Template.bind({});
Default.args = {
  components: components,
};
