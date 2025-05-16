import { NotificationCenter, Settings, SettingsProps } from "@protzilla/app";
import { Button } from "@protzilla/core";
import { useToggleableState } from "@protzilla/hooks";
import { Meta } from "@storybook/react";
import { useState } from "react";


export default {
  component: Settings,
  title: "Settings Components / Settings",
  argTypes: { onClose: { action: "close" } },
  decorators: [
    (Story) => (
      <NotificationCenter>
        <Story />
      </NotificationCenter>
    ),
  ],
} as Meta;

export const Default = (args: SettingsProps): React.ReactNode => {
  const [isSettingsOpen, openSettings, closeSettings] = useToggleableState(false);
  const [hasChanges, setHasChanges] = useState(false);

  return (
    <div>
      <Button text={"Open settings"} icon={"settings"} onPress={openSettings} />
      <Settings
        {...args}
        isOpen={isSettingsOpen}
        onClose={closeSettings}
        hasChanges={hasChanges}
        setHasChanges={setHasChanges}
      />
    </div>
  );
};
