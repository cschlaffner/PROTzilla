import { color, zIndex } from "@protzilla/theme";
import React from "react";
import { styled } from "styled-components";

import { CircularButton } from "../button";
import { Card } from "../cards/card";
import { Form } from "../forms/form";
import { Icon } from "../icon";
import { SectionTitle } from "../section-title";
import { ModalProps } from "./modal.props";

const Backdrop = styled.div<{ isOpen: boolean }>`
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: ${color("popUpBackdrop")};
  display: ${(props) => (props.isOpen ? "flex" : "none")};
  justify-content: center;
  align-items: center;
  z-index: ${zIndex("modal")};
`;

const ModalContent = styled.div`
  width: 400px;
  max-width: 90%;
`;

const CloseButton = styled(CircularButton)`
  background-color: ${color("protzillaGray")};
  color: ${color("primary")};
  display: flex;
  justif-content: center;
  flex-shrink: 0;
  width: 40px;
  height: 30px;
`;

const CardHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
`;

const StyledCard = styled(Card)`
  overflow-y: visible;
`;

export const Modal: React.FC<ModalProps> = ({ isOpen, onClose, title, children, className }) => {
  return (
    isOpen && (
      <Backdrop isOpen={isOpen} onClick={onClose}>
        <ModalContent
          className={className}
          onClick={(e) => {
            e.stopPropagation();
          }}
        >
          <StyledCard
            title={
              <CardHeader>
                <SectionTitle baseComponent={"h2"} title={title} />
                <CloseButton onClick={onClose}>
                  <Icon icon="close"></Icon>
                </CloseButton>
              </CardHeader>
            }
          >
            {children}
          </StyledCard>
        </ModalContent>
      </Backdrop>
    )
  );
};

export const NameModal: React.FC<{
  isOpen: boolean;
  title: string;
  label: string;
  submitLabel: string;
  initialValue?: string;
  onClose: () => void;
  onSubmit: (name: string) => void;
}> = ({ isOpen, title, label, submitLabel, initialValue = "", onClose, onSubmit }) => (
  <Modal title={title} isOpen={isOpen} onClose={onClose}>
    <Form
      formData={{
        label: "",
        labelSubmitButton: submitLabel,
        isAutoSubmit: false,
        hasChangeIndicator: false,
        input_fields: [{ type: "text", name: "name", label, value: initialValue, isVisible: true }],
      }}
      onChange={({ name }) => {
        if (typeof name === "string" && name.trim()) onSubmit(name);
      }}
    />
  </Modal>
);
