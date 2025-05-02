import { useRef, useState } from "react";
import { styled } from "styled-components";

import { useOutsidePress, useToggleableState } from "../../hooks";
import { color, fontSize, fontWeight, spacing } from "../../theme";
import { callApiWithParameters } from "../../utils";
import { FlexColumn } from "../box";
import { Text } from "../text";
import { NavbarProps } from "./navbar.props.ts";
import { Button } from "../button";
import { RunEditMenu } from "../run-edit-menu/run-edit-menu.tsx";

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

const NavbarCenterTitle = styled(Text)`
  color: ${color("onPrimary")};
  font-size: ${fontSize("h3")};
  font-weight: ${fontWeight("bold")};
  align-self: center;
  padding: ${spacing("buttonPadding")};
`;

export const Navbar: React.FC<NavbarProps> = ({
  allowRunEdit,
  title,
  onNavigateHome,
  onOpenSettings,
  onOpenHelp,

  ...rest
}) => {
  const [runName, setRunName] = useState<string>(title as string);
  const [isRunSettingsOpen, openRunSettings, closeRunSettings] =
    useToggleableState();
  const refRunSettings = useRef<HTMLDivElement>(null);
  useOutsidePress(refRunSettings, closeRunSettings, isRunSettingsOpen, false);

  const onChangeRunName = (newRunName: string) => {
    setRunName(newRunName);
  };

  const handleAddTag = (tag: string) => {
    void callApiWithParameters("add_tag/", {
      run_name: runName,
      tag_name: tag,
    });
  };

  const handleDeleteTag = (tagToDelete: string) => {
    void callApiWithParameters("delete_tag/", {
      run_name: runName,
      tag_name: tagToDelete,
    });
  };

  const handleToggleFavourite = () => {
    void callApiWithParameters("toggle_favourite/", {
      run_name: runName,
    });
  };

  return (
    <FlexColumn {...rest}>
      <NavbarBody>
        <NavbarLeft>
          <Button icon={"home"} onPress={onNavigateHome} />
        </NavbarLeft>
        <NavbarCenter>
          <NavbarCenterTitle text={allowRunEdit ? runName : "PROTzilla"} />
          {allowRunEdit && (
            <Button
              icon={"edit"}
              onPointerDown={isRunSettingsOpen ? undefined : openRunSettings}
            />
          )}
        </NavbarCenter>

        <NavbarRight>
          <Button icon={"help"} onPress={onOpenHelp} />
          <Button icon={"settings"} onPress={onOpenSettings} />
        </NavbarRight>
      </NavbarBody>
      {isRunSettingsOpen && (
        <RunEditMenu
          runName={runName}
          onChangeRunName={onChangeRunName}
          handleAddTag={(tag: string) => { handleAddTag(tag); }}
          handleDeleteTag={(tagToDelete: string) =>
            { handleDeleteTag(tagToDelete); }
          }
          handleToggleFavourite={() => { handleToggleFavourite(); }}
          isOpen={isRunSettingsOpen}
          onClose={closeRunSettings}
          ref={refRunSettings}
        />
      )}
    </FlexColumn>
  );
};
