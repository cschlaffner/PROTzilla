import { Meta, StoryFn } from "@storybook/react";

import { ContentCard } from "./content-card";
import { ContentCardProps } from "./content-card.props";
import { PlotComponent } from "../../plot";

export default {
  component: ContentCard,
  title: "Content Card",
} as Meta<ContentCardProps>;

const Template: StoryFn<ContentCardProps> = (args) => <ContentCard {...args} />;

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
  plotComponent: <PlotComponent data={plotData} layout={plotLayout} />,
};
