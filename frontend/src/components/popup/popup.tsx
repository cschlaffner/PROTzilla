import { observer } from "mobx-react-lite";
import React, { useEffect, useRef } from "react";
import ReactDOM from "react-dom";
import { styled } from "styled-components";

import { useModalRoot, useOutsidePress } from "../../hooks";
import { FlexRow, Spacer } from "../box";
import { coverMixin } from "../mixins";
import { Text } from "../text";
import { PopUpProps } from "./popup.props";
import { color, radius, size, spacing, zIndex } from "../../theme";
import { SectionTitle } from "../section-title";
import { buttonComponents } from "./button-components";

const InvisiblePopUpBackdrop = styled.div`
  ${coverMixin}

  pointer-events: auto;
  z-index: ${zIndex("modal")};
`;
const PopUpBackdrop = styled.div`
  ${coverMixin}

  backdrop-filter: blur(20px);
  background: ${color("popUpBackdrop")};
  z-index: ${(props) => (zIndex("modal")(props) as number) - 1};
  display: flex;
  justify-content: center;
  align-items: center;
  pointer-events: auto;
`;

const PopUpContainer = styled.div`
  align-items: stretch;
  background: ${color("background")};
  border-radius: ${radius("card")};
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  gap: ${spacing("medium")};
  width: 850px;
  max-width: 80vw;
  max-height: 80vh;
  min-height: 300px;
  overflow: auto;
  padding: ${spacing("large")};
  pointer-events: auto;

  .confirm-button,
  .dismiss-button {
    width: ${size("navigationItemWidth")};
  }
`;

const ButtonRow = styled(FlexRow)`
  align-self: stretch;
  gap: 20px;
  justify-content: space-between;
`;

const stopPropagation = (event: React.WheelEvent) => {
  event.stopPropagation();
};

// eslint-disable-next-line @typescript-eslint/no-empty-function
const emptyAction = () => {};

export const PopUp = observer<PopUpProps>(
  ({
    title,
    titleTx,
    titleData,
    titleComponents,
    description,
    descriptionTx,
    descriptionData,
    descriptionComponents,
    confirm,
    confirmTx,
    confirmData,
    confirmComponents,
    confirmIcon = "checkmark",
    confirmButtonKind = "primary",
    confirmAutoFocus,
    isConfirmDisabled,
    dismiss,
    dismissTx,
    dismissData,
    dismissComponents,
    dismissIcon = "close",
    dismissButtonKind = "secondary",
    dismissAutoFocus,
    isDismissDisabled,
    text,
    tx,
    txComponents,
    txData,
    isOpen,
    onConfirm,
    onDismiss,
    onOutsidePress,
    children,
    ...rest
  }) => {
    const ref = useRef<HTMLDivElement>(null);
    useOutsidePress(ref, onOutsidePress ?? emptyAction, isOpen, false);

    useEffect(() => {
      if (!onDismiss || isOpen === false) return;

      ref.current?.scrollTo(0, 0);

      const handleKeyDown = (event: KeyboardEvent) => {
        if (event.key === "Escape") {
          onDismiss();
        }
      };
      window.addEventListener("keydown", handleKeyDown);

      return () => {
        window.removeEventListener("keydown", handleKeyDown);
      };
    }, [isOpen, onDismiss]);

    const modalRootRef = useModalRoot();

    const ConfirmButton = buttonComponents[confirmButtonKind];
    const DismissButton = buttonComponents[dismissButtonKind];

    const popup = (
      <InvisiblePopUpBackdrop>
        <PopUpBackdrop onWheel={stopPropagation}>
          <PopUpContainer {...rest} ref={ref}>
            {(title ?? titleTx ?? description ?? descriptionTx) && (
              <SectionTitle
                baseComponent="h2"
                title={title}
                titleTx={titleTx}
                titleData={titleData}
                titleComponents={titleComponents}
                description={description}
                descriptionTx={descriptionTx}
                descriptionData={descriptionData}
                descriptionComponents={descriptionComponents}
              />
            )}
            {(tx ?? text) && (
              <Text
                tx={tx}
                text={text}
                txData={txData}
                txComponents={txComponents}
                className="popup-text"
              />
            )}
            {children}
            {(onConfirm ?? onDismiss) && (
              <>
                <Spacer />
                <ButtonRow className="button-row">
                  {onDismiss && (
                    <DismissButton
                      className="dismiss-button"
                      text={dismiss}
                      tx={dismissTx ?? (dismiss === undefined ? "base:dismiss" : undefined)}
                      txData={dismissData}
                      txComponents={dismissComponents}
                      icon={dismissIcon}
                      iconRight
                      autoFocus={!confirmAutoFocus && dismissAutoFocus}
                      isDisabled={isDismissDisabled}
                      onPress={onDismiss}
                    />
                  )}
                  {onConfirm && (
                    <ConfirmButton
                      className="confirm-button"
                      text={confirm}
                      tx={confirmTx ?? (confirm === undefined ? "base:confirm" : undefined)}
                      txData={confirmData}
                      txComponents={confirmComponents}
                      icon={confirmIcon}
                      iconRight
                      autoFocus={confirmAutoFocus}
                      isDisabled={isConfirmDisabled}
                      onPress={onConfirm}
                    />
                  )}
                </ButtonRow>
              </>
            )}
          </PopUpContainer>
        </PopUpBackdrop>
      </InvisiblePopUpBackdrop>
    );

    const node = isOpen === false ? null : popup;

    return modalRootRef.current ? ReactDOM.createPortal(node, modalRootRef.current) : node;
  },
);
