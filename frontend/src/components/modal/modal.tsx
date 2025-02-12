import React from "react";
import styled from "styled-components";
import { ModalProps } from "./modal.props";
import { Card } from "../card"; // Reuse the Card component

const Backdrop = styled.div<{ isOpen: boolean }>`
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: ${(props) => (props.isOpen ? "flex" : "none")};
  justify-content: center;
  align-items: center;
  z-index: 1000;
`;

const ModalContent = styled.div`
  width: 400px;
  max-width: 90%;
`;

const CloseButton = styled.button`
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  position: absolute;
  top: 12px;
  right: 12px;
`;

export const Modal: React.FC<ModalProps> = ({ isOpen, onClose, title, children, className }) => {
  return (
    <Backdrop isOpen={isOpen} onClick={onClose}>
      <ModalContent className={className} onClick={(e) => e.stopPropagation()}>
        <Card title={title}>
          <CloseButton onClick={onClose}>×</CloseButton>
          {children}
        </Card>
      </ModalContent>
    </Backdrop>
  );
};
