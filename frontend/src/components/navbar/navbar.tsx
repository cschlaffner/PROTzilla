import { styled } from "styled-components";

import {
    color,
    fontSize,
    fontWeight, spacing,
} from "../../theme";
import { FlexColumn } from "../box";
import { Text } from "../text";

import { NavbarProps } from "./navbar.props.ts";
import {Button} from "../button";


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
    background-color: ${color("popUpBackdropLight")};
    height: ${spacing("medium")};
    align-content: center;
`;

const NavbarCenterTitle = styled(Text)`
    color: ${color("onPrimary")};
    font-size: ${fontSize("h2")};
    font-weight: ${fontWeight("bold")};
    align-self: center;
    padding: ${spacing("buttonPadding")};
`;

export const Navbar: React.FC<NavbarProps> = ({
    title,
    titleTx,
    titleData,
    titleComponents,
    iconCenterRight,
    iconHome,
    iconBurgerMenu,

    ...rest

}) => {
  return <FlexColumn {...rest}>
    <NavbarBody>
        <NavbarLeft>
            <HomeButton
                icon={iconHome}
                text="Home"
                />
        </NavbarLeft>
        <NavbarCenter>
            <NavbarCenterTitle
                    text={title}
                tx={titleTx}
                txData={titleData}
                txComponents={titleComponents}
              />
            <Button
                icon={iconCenterRight}
                />

        </NavbarCenter>
        <NavbarRight>
            <Button
                icon={iconBurgerMenu}
                />
        </NavbarRight>


    </NavbarBody>
  </FlexColumn>;
}
