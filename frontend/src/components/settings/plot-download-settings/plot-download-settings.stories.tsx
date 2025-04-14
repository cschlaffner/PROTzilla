import { PlotDownloadSettings } from "./plot-download-settings";
import { PlotDownloadSettingsProps } from "./plot-download-settings.props";

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
