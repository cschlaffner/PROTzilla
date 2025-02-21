import { forwardRef } from "react";
import { styled } from "styled-components";

import { SideMenuProps } from "./side-menu.props.ts";
import { color, fontSize, spacing } from "../../theme";
import { InvisibleButton } from "../button";

const SideMenuWrapper = styled.div<{ isMenuOpen: boolean }>`
  position: absolute;
  top: ${spacing("navbarHeight")};
  right: ${({ isMenuOpen }) => (isMenuOpen ? "0" : "-250px")}; /* Slide in */
  width: 250px;
  height: calc(100vh - ${spacing("navbarHeight")});
  background: ${color("protzillaLightGray")};
  box-shadow: -2px 0 10px rgba(0, 0, 0, 0.2);
  transition: right 0.3s ease-in-out;
  display: flex;
  flex-direction: column;
  padding: 20px;
  gap: 10px;
  justify-content: space-between;
`;

const SideMenuItem = styled(InvisibleButton)`
  display: flex;
  width: 100%;
  justify-content: left;
  font-size: ${fontSize("button")};
`;

const Footer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: ${spacing("large")};
  padding-bottom: ${spacing("medium")};
  font-size: ${fontSize("default")};
  color: ${color("protzillaDarkBlue")};
`;

export const SideMenu = forwardRef<HTMLDivElement, SideMenuProps>(
  function SideMenu({ isMenuOpen, ...rest }, ref) {
    const onNavigateToSettings = () => {
      console.log("open settings");
    };

    const onOpenGithub = () => {
      window.open("https://github.com/cschlaffner/PROTzilla", "_blank");
    };

    return (
      <SideMenuWrapper isMenuOpen={isMenuOpen} ref={ref} {...rest}>
        <div>
          <SideMenuItem onPress={onNavigateToSettings} icon={"settings"}>
            Settings
          </SideMenuItem>
          <SideMenuItem icon={"protzilla"}> More stuff </SideMenuItem>
        </div>

        <Footer>
          <InvisibleButton onPress={onOpenGithub} icon={"github"}>
            GitHub
          </InvisibleButton>
          <span>PROTzilla is an open-source project.</span>
          <span>Version: 0.0.0.0</span>
          <span>Hasso-Plattner-Institut Potsdam</span>
        </Footer>
      </SideMenuWrapper>
    );
  },
);
