import React from "react";

import {
  BigButton,
  BorderButton,
  Button,
  CircularButton,
  GrayButton,
  GraySquareButton,
  GreenButton,
  InvisibleButton,
  RedButton,
  RedSecondaryButton,
  SecondaryButton,
  SquareButton,
  ToggleableButton,
} from "./button";
import { ButtonProps } from "./button.props";

export default {
  component: Button,
  title: "Button",
  argTypes: { onPress: { action: "pressed" } },
};

export const primary = (args: ButtonProps): React.ReactNode => <Button {...args} />;
primary.args = {
  isDisabled: false,
  text: "Primary Button",
  tag: "",
};

export const primaryCautious = (args: ButtonProps): React.ReactNode => <Button {...args} />;
primaryCautious.args = {
  isCautious: true,
  isDisabled: false,
  text: "Primary Button",
  tag: "",
};

export const secondary = (args: ButtonProps): React.ReactNode => <SecondaryButton {...args} />;
secondary.args = {
  isDisabled: false,
  text: "Secondary Button",
  tag: "",
};

export const gray = (args: ButtonProps): React.ReactNode => <GrayButton {...args} />;
gray.args = {
  isDisabled: false,
  text: "Gray Button",
  tag: "",
};

export const grayShy = (args: ButtonProps): React.ReactNode => <GrayButton {...args} />;
grayShy.args = {
  isShy: true,
  isDisabled: false,
  text: "Gray Button",
  tag: "",
};

export const big = (args: ButtonProps): React.ReactNode => <BigButton {...args} />;
big.args = {
  isDisabled: false,
  icon: "add",
  isBig: true,
};

export const green = (args: ButtonProps): React.ReactNode => <GreenButton {...args} />;
green.args = {
  isDisabled: false,
  text: "Green Button",
  tag: "",
};

export const red = (args: ButtonProps): React.ReactNode => <RedButton {...args} />;
red.args = {
  isDisabled: false,
  text: "Red Button",
  tag: "",
};

export const redSecondary = (args: ButtonProps): React.ReactNode => (
  <RedSecondaryButton {...args} />
);
redSecondary.args = {
  isDisabled: false,
  text: "Red Secondary Button",
  tag: "",
};

export const small = (args: ButtonProps): React.ReactNode => <SecondaryButton {...args} />;
small.args = {
  isDisabled: false,
  isShy: false,
  text: "Small Button",
  icon: "add",
  isSmall: true,
};

export const icon = (args: ButtonProps): React.ReactNode => <Button {...args} />;
icon.args = {
  isDisabled: false,
  icon: "add",
  tag: "",
};

export const grayIcon = (args: ButtonProps): React.ReactNode => <GrayButton {...args} />;
grayIcon.args = {
  isDisabled: false,
  icon: "add",
  tag: "",
};

export const iconAndText = (args: ButtonProps): React.ReactNode => <Button {...args} />;
iconAndText.args = {
  isDisabled: false,
  icon: "add",
  text: "Add",
  tag: "",
};

export const iconRight = (args: ButtonProps): React.ReactNode => (
  <Button style={{ width: "240px" }} {...args} />
);
iconRight.args = {
  isDisabled: false,
  icon: "add",
  iconRight: true,
  text: "Add",
  tag: "",
};

export const square = (args: ButtonProps): React.ReactNode => <SquareButton {...args} />;
square.args = {
  isDisabled: false,
  text: "S",
};

export const graySquare = (args: ButtonProps): React.ReactNode => <GraySquareButton {...args} />;
graySquare.args = {
  isDisabled: false,
  text: "1",
};

export const circular = (args: ButtonProps): React.ReactNode => <CircularButton {...args} />;
circular.args = {
  isDisabled: false,
  text: "C",
};

export const invisible = (args: ButtonProps): React.ReactNode => <InvisibleButton {...args} />;
invisible.args = {
  isDisabled: false,
  icon: "add",
  text: "Home",
};

export const tooltip = (args: ButtonProps): React.ReactNode => <Button {...args} />;
tooltip.args = {
  isDisabled: false,

  text: "Hover Me",
  tooltip: "Tooltip!",
};

export const notification = (args: ButtonProps): React.ReactNode => <Button {...args} />;
notification.args = {
  isDisabled: false,
  text: "Button with Notification",
  tag: "",
  notifications: 100,
};

export const toggleable = (args: ButtonProps & { isActive?: boolean }): React.ReactNode => (
  <ToggleableButton {...args} />
);
toggleable.args = {
  isDisabled: false,
  icon: "add",
  text: "Navigation Button",
  isActive: false,
  isCollapsed: true,
};

export const border = (args: ButtonProps): React.ReactNode => <BorderButton {...args} />;
border.args = {
  isDisabled: false,
  text: "Border Button",
};
