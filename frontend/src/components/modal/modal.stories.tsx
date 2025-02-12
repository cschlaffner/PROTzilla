import { Meta, StoryFn } from "@storybook/react";
import { Modal } from "./modal";
import { ModalProps } from "./modal.props";
import { useState } from "react";
import { Button } from "../button";

export default {
  component: Modal,
  title: "Overlay / Modal",
} as Meta<ModalProps>;

const Template: StoryFn<ModalProps> = (args) => {
  const [isOpen, setIsOpen] = useState(args.isOpen);

  return (
    <>
      <Button onClick={() => setIsOpen(true)}>Open Modal</Button>
      <Modal {...args} isOpen={isOpen} onClose={() => setIsOpen(false)}>
        <p>This is a modal with some content.</p>
      </Modal>
    </>
  );
};

export const Default = Template.bind({});
Default.args = {
  title: "Modal Title",
  isOpen: false,
};
