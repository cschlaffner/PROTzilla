import { Card, CircularButton, Icon, SectionTitle } from "@protzilla/core";
import { color, zIndex } from "@protzilla/theme";
import React from "react";
import { styled } from "styled-components";

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

export const Modal: React.FC<ModalProps> = ({ isOpen, onClose, title, children, className }) => {
  return (
    <Backdrop isOpen={isOpen} onClick={onClose}>
      <ModalContent
        className={className}
        onClick={(e) => {
          e.stopPropagation();
        }}
      >
        <Card
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
        </Card>
      </ModalContent>
    </Backdrop>
  );
};
