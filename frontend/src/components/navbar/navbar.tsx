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
  height: 75px;
  box-sizing: border-box;
  background: ${color("primary")};
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
  background-color: ${color("popUpBackdropLight")};
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
  font-size: ${fontSize("h2")};
  font-weight: ${fontWeight("bold")};
  align-self: center;
  padding: ${spacing("buttonPadding")};
`;

// TODO create this component and add here
const TempMenu = styled.div`
  width: 100px;
  height: 100px;
  background: #1a1d20;
  color: #fff;
  align-self: self-end;
  font-size: ${fontSize("small")};
`;

// TODO create this component and add here
const TempRunSettings = styled.div`
  width: 100px;
  height: 100px;
  background: #1a1d20;
  color: #fff;
  align-self: center;
  font-size: ${fontSize("small")};
`;

export const Navbar: React.FC<NavbarProps> = ({
  title,
  titleTx,
  titleData,
  titleComponents,
  onNavigateBack,
  isDetailsPage,

  ...rest
}) => {
  const [isMenuOpen, openMenu, closeMenu] = useToggleableState();
  const refMenu = useRef<HTMLDivElement>(null);
  useOutsidePress(refMenu, closeMenu, isMenuOpen, false);

  const [isRunSettingsOpen, openRunSettings, closeRunSettings] =
    useToggleableState();
  const refRunSettings = useRef<HTMLDivElement>(null);
  useOutsidePress(refRunSettings, closeRunSettings, isRunSettingsOpen, false);

  return (
    <FlexColumn {...rest}>
      <NavbarBody>
        <NavbarLeft>
          {isDetailsPage ? (
            <HomeButton
              icon={"protzilla"}
              text="Home"
              onPress={onNavigateBack}
            />
          ) : (
            <HomeIcon icon={"protzilla"} color={"onPrimary"} />
          )}
        </NavbarLeft>
        {isDetailsPage ? (
          <NavbarCenter>
            <NavbarCenterTitle
              text={title}
              tx={titleTx}
              txData={titleData}
              txComponents={titleComponents}
            />
            <Button icon={"edit"} onPress={openRunSettings} />
          </NavbarCenter>
        ) : (
          <NavbarCenter>
            <NavbarCenterTitle text={"PROTzilla"} tx={"PROTzilla"} />
          </NavbarCenter>
        )}
        <NavbarRight>
          <Button icon={"burgerMenu"} onPress={openMenu} />
        </NavbarRight>
      </NavbarBody>
      {isMenuOpen && (
        <TempMenu ref={refMenu}>
          {
            "TODO: Create component to show menu, go to settings, add github icon etc. "
          }
        </TempMenu>
      )}
      {isRunSettingsOpen && (
        <TempRunSettings ref={refRunSettings}>
          {
            "TODO: Create component to show current run's name, tags, other info."
          }
        </TempRunSettings>
      )}
    </FlexColumn>
  );
};
