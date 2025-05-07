import { useCallback, useState } from "react";
import { styled } from "styled-components";

import { Button } from "../button";
import { PopUp } from "./popup";
import { PopUpProps } from "./popup.props";
import { color, radius } from "../../theme";

export default {
  component: PopUp,
  title: "Pop Up",
  argTypes: {
    onOutsidePress: { action: "outside press" },
    onConfirm: { action: "confirm" },
    onDismiss: { action: "dismiss" },
  },
};

const PopupWithState = ({ onConfirm, onDismiss, onOutsidePress, ...rest }: PopUpProps) => {
  const [isOpen, setIsOpen] = useState(true);
  const open = useCallback(() => {
    setIsOpen(true);
  }, []);
  const close = useCallback(() => {
    setIsOpen(false);
  }, []);

  const confirm = useCallback(() => {
    onConfirm?.();
    close();
  }, [onConfirm, close]);

  const dismiss = useCallback(() => {
    onDismiss?.();
    close();
  }, [onDismiss, close]);

  const outsidePress = useCallback(() => {
    onOutsidePress?.();
    close();
  }, [onOutsidePress, close]);

  return (
    <>
      <Button onPress={open} text="Open Pop Up" />
      <PopUp
        {...rest}
        onConfirm={confirm}
        onDismiss={dismiss}
        onOutsidePress={outsidePress}
        isOpen={isOpen}
      />
    </>
  );
};

export const primary = (args: PopUpProps): React.ReactNode => <PopupWithState {...args} />;
primary.args = {
  title: "Popup",
  description: "Description",
  text: "This is popup text. Click one of the buttons or outside the pop up to close it.",
  icon: "warning",
  confirmAutoFocus: true,
  dismissAutoFocus: false,
  confirmButtonKind: "primary",
  dismissButtonKind: "secondary",
};

const Box = styled.div`
  width: 100px;
  height: 100px;
  background-color: ${color("secondary")};
  border-radius: ${radius("default")};
`;
export const withChildren = (args: PopUpProps): React.ReactNode => (
  <PopUp {...args}>
    <Box />
    <Box />
  </PopUp>
);
withChildren.args = {
  title: "Popup with children",
  description: "Description",
  text: "This pop up has children.",
  isOpen: true,
};

export const customButtonText = (args: PopUpProps): React.ReactNode => <PopUp {...args} />;
customButtonText.args = {
  title: "Popup with custom button text",
  description: "Description",
  text: "This pop up has custom button text.",
  isOpen: true,
  dismissTx: "dismiss-translation-key",
  confirmTx: "confirm-translation-key",
};
