import { FormData } from "../components/forms/form";

export const mockPlotData: Partial<Plotly.Data>[] = [
  {
    x: ["A", "B", "C", "D"],
    y: [10, 20, 30, 40],
    type: "bar",
    marker: { color: "purple" },
  },
];

export const mockPlotLayout: Partial<Plotly.Layout> = {
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

export const mockFormDataParameters: FormData = {
  label: "Parameters",
  isAutoSubmit: false,
  input_fields: [
    {
      type: "dropdown",
      name: "method",
      props: {
        label: "Protein Data Import MaxQuant",
        options: [
          { label: "MaxQuant Protein Groups Import", value: "maxQuant" },
          {
            label: "MaxQuant Peptide Groups Import",
            value: "maxQuantPeptides",
          },
          { label: "MaxQuant MS/MS Data Import", value: "maxQuantMSMS" },
          {
            label: "MaxQuant Post-Processing",
            value: "maxQuantPostProcessing",
          },
        ],
      },
    },
    {
      type: "file",
      name: "file",
      props: { label: "MaxQuant intensities file (proteinGroups.txt):" },
    },
    {
      type: "dropdown",
      name: "intensity",
      props: {
        label: "Intensity",
        options: [
          { label: "iBAQ", value: "ibaq" },
          { label: "LFQ Intensity", value: "lfq" },
          { label: "Total Intensity", value: "totalIntensity" },
          { label: "Normalized Intensity", value: "normalizedIntensity" },
        ],
      },
    },
  ],
};

export const mockFormDataPlotSettings: FormData = {
  label: "Plot Settings",
  isAutoSubmit: true,
  input_fields: [
    {
      type: "dropdown",
      name: "type",
      props: {
        label: "Select a Plot type",
        options: [
          { label: "Bar", value: "bar" },
          { label: "Line", value: "scatter" },
        ],
      },
    },
    {
      type: "multi-select",
      name: "colors",
      props: {
        label: "Select colors for the plot",
        options: [
          { label: "Purple", value: "purple" },
          { label: "Blue", value: "blue" },
          { label: "Red", value: "red" },
          { label: "Yellow", value: "yellow" },
          { label: "Green", value: "green" },
          { label: "Cyan", value: "cyan" },
          { label: "Black", value: "black" },
          { label: "Aqua", value: "aqua" },
        ],
      },
    },
  ],
};

export const dummyTextComponent1 =
  "😲 Ohh you shouldn't come here - we're not finished yet. \n Quickly click on the switch again. 👀";

export const dummyTextComponent2 =
  "🚧 Construction is still going on here \n and there is absolutely nothing to see 🚧";

export const footerMessages = [
  "Made with ❤️ from Potsdam",
  "Crafted with love in Potsdam ❤️",
  "Engineered with 99% love & 1% coffee in Potsdam ☕❤️",
  "Made in Potsdam – No bugs, only features! 🐞🚀",
  "100% Debugged in Potsdam (probably) 🤔❤️",
  "Potsdam tested, user approved! ✅",
  "Deployed from Potsdam ❤️🚀",
  "Error 404: Bugs not found (Made in Potsdam) 🛠️",
  '<code>Made.with(love).from("Potsdam");</code> 💻❤️',
  'print("Made with love from Potsdam ❤️")',
  "Now compiling... Made in Potsdam 🛠️",
  "100% hand-coded in Potsdam (except for the bugs, they write themselves) 🐞",
  "Loading... Made with ❤️ from Potsdam",
  "Exception thrown: Too much love from Potsdam ❤️",
  "Generated with AI? Nope, just Potsdam magic ✨",
  "Exported from Potsdam – No import taxes!",
  "99% caffeine, 1% Potsdam ☕",
  "This line of code traveled from Potsdam to your screen ✈️",
  "Made in Potsdam. Batteries not included.",
  "If this breaks, blame Potsdam! 😜",
  'System.out.println("Made with ❤️ in Potsdam");',
  "Greetings from Potsdam 👋",
  "Made with love, coffee, and an unhealthy amount of snacks 🍕💻",
  "Crafted with love and questionable decisions 😜❤️",
  "Made with love, caffeine, and some occasional panic 😅💖",
  "Built with love and a sprinkle of chaos ✨❤️",
  "Made with love (and maybe a little bit of magic) 🧙‍♂️❤️",
  "Created with love, teamwork, and a dash of procrastination ⏳💖",
  "Made with love, sweat, and lots of coffee ☕❤️",
  "Built with love and a pinch of inspiration 🎨❤️",
  "Made with love, code, and a few mistakes along the way 💻❤️",
  "Created with love, creativity, and some mild confusion 🤔❤️",
  "Made with love, a bit of sass, and some funky ideas 🦄❤️",
  "Crafted with love, late nights, and a touch of sparkle ✨❤️",
  "Made with love, passion, and a whole lot of caffeine ☕❤️",
  "Created with love and just the right amount of panic 🏃‍♂️💖",
  "Made with love, unicorns, and a dash of glitter 🦄✨❤️",
  "Built with love and a healthy dose of determination 💪❤️",
  "Made with love and a bit of nerdy magic 🧙‍♀️❤️",
  "Created with love, Wi-Fi, and endless inspiration 💡❤️",
  "Made with love, but don’t ask us to explain how 😅❤️",
  "Built with love, creativity, and a sprinkle of brilliance ✨❤️",
];
