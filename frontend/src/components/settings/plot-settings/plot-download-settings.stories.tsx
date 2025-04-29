import {
  PlotDownloadSettings,
  PlotDownloadSettingsProps,
} from "./plot-download-settings";

export default {
  component: PlotDownloadSettings,
  title: "Settings Components / Plot Download",
};

export const primary = (args: PlotDownloadSettingsProps): React.ReactNode => (
  <PlotDownloadSettings {...args} />
);
primary.args = {
  isOpen: true,
};
