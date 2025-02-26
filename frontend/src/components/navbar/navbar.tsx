import { useRef } from "react";
import { styled } from "styled-components";

import { useOutsidePress, useToggleableState } from "../../hooks";
import { color, fontSize, fontWeight, spacing } from "../../theme";
import { FlexColumn } from "../box";
import { Text } from "../text";
import { NavbarProps } from "./navbar.props.ts";
import { Button } from "../button";
import { Icon } from "../icon";

const NavbarBody = styled.div`
  align-items: center;
  width: 100vw;
  height: ${spacing("navbarHeight")};
  box-sizing: border-box;
  background: ${color("primary")};
  position: relative;
  display: flex;
  flex-direction: row;
  justify-content: space-between;
`;

const NavbarLeft = styled.div`
  display: flex;
  flex-direction: row;
  justify-content: left;
  padding-left: ${spacing("medium")};
`;

const NavbarCenter = styled.div`
  display: flex;
  flex-direction: row;
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  justify-content: center;
  align-content: center;
  align-items: center;
  height: 100%;
`;

const NavbarRight = styled.div`
  display: flex;
  flex-direction: row;
  justify-content: right;
  padding-right: ${spacing("medium")};
`;

const HomeButton = styled(Button)`
  padding-top: 0;
  padding-left: ${spacing("smallButtonIconPadding")};
  padding-bottom: 0;
  padding-right: ${spacing("buttonPadding")};
  height: ${spacing("large")};
  align-content: center;

  .icon {
    width: 100%;
    height: 100%;
  }
`;

const HomeIcon = styled(Icon)`
  height: ${spacing("large")};
  width: fit-content;
  color: ${color("onPrimary")};
  padding-left: ${spacing("smallButtonIconPadding")};
  padding-right: ${spacing("buttonPadding")};
`;

const NavbarCenterTitle = styled(Text)`
  color: ${color("onPrimary")};
  font-size: ${fontSize("h3")};
  font-weight: ${fontWeight("bold")};
  align-self: center;
  padding: ${spacing("buttonPadding")};
`;

// TODO create this component and add here
const TempRunSettings = styled.div`
  width: 100px;
  height: 100px;
  background: #1a1d20;
  position: absolute;
  top: ${spacing("navbarHeight")};
  color: #fff;
  align-self: center;
  font-size: ${fontSize("small")};
`;

export const Navbar: React.FC<NavbarProps> = ({
  allowRunEdit,
  title,
  titleTx,
  titleData,
  titleComponents,
  onNavigateHome,
  onOpenSettings,
  showHomeButton,

  ...rest
}) => {
  const [isRunSettingsOpen, openRunSettings, closeRunSettings] =
    useToggleableState();
  const refRunSettings = useRef<HTMLDivElement>(null);
  useOutsidePress(refRunSettings, closeRunSettings, isRunSettingsOpen, false);

  return (
    <FlexColumn {...rest}>
      <NavbarBody>
        <NavbarLeft>
          {showHomeButton ? (
            <HomeButton
              icon={"protzilla"}
              text="Home"
              onPress={onNavigateHome}
            />
          ) : (
            <HomeIcon icon={"protzilla"} color={"onPrimary"} />
          )}
        </NavbarLeft>
        <NavbarCenter>
          <NavbarCenterTitle
            text={allowRunEdit ? title : "PROTzilla"}
            tx={allowRunEdit ? titleTx : "PROTzilla"}
            txData={allowRunEdit ? titleData : undefined}
            txComponents={allowRunEdit ? titleComponents : undefined}
          />
          {allowRunEdit && (
            <Button
              icon={"edit"}
              onPointerDown={isRunSettingsOpen ? undefined : openRunSettings}
            />
          )}
          {isRunSettingsOpen && (
            <TempRunSettings ref={refRunSettings}>
              {
                "TODO: Create component to show current run's name, tags, other info."
              }
            </TempRunSettings>
          )}
        </NavbarCenter>

        <NavbarRight>
          <Button icon={"settings"} onPress={onOpenSettings} />
        </NavbarRight>
      </NavbarBody>
    </FlexColumn>
  );
};
