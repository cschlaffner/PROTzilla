import { Meta, StoryFn } from "@storybook/react";

import { PlotComponent, SwitchCardProps, SwitchCard } from "@protzilla/core";

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

export const Default = Template.bind({});
Default.args = {
  nameComponent1: "Plot",
  component1: <PlotComponent data={plotData} layout={plotLayout} />,
  nameComponent2: "Table",
  component2: <p>Caution, construction is in progress here! Come back later</p>,
};
