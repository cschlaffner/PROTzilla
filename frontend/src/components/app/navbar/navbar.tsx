import { NavbarProps, RunEditMenu, Settings, useNotification } from "@protzilla/app";
import {
  Button,
  DiscardModal,
  FlexColumn,
  Form,
  Icon,
  InputValueType,
  Modal,
  Text,
} from "@protzilla/core";
import { useOutsidePress, useToggleableState } from "@protzilla/hooks";
import { color, fontSize, fontWeight, spacing } from "@protzilla/theme";
import { callApiWithParameters } from "@protzilla/utils";
import { useCallback, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { styled } from "styled-components";

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
  align-items: center;
`;

const NavbarCenterTitle = styled(Text)`
  color: ${color("onPrimary")};
  font-size: ${fontSize("h3")};
  font-weight: ${fontWeight("bold")};
  align-self: center;
  padding: ${spacing("buttonPadding")};
`;

const MemoryDiv = styled.div`
  display: flex;
  align-items: center;
`;

const MemoryUsageTitle = styled(Text)`
  color: ${color("onPrimary")};
  font-weight: ${fontWeight("bold")};
  font-size: ${fontSize("h5")};
  align-self: center;
  padding-left: ${spacing("verySmall")};
  padding-right: ${spacing("medium")};
`;

const ChatMessages = styled.div`
  min-height: 220px;
  max-height: 50vh;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: ${spacing("small")};
  padding-bottom: ${spacing("small")};
`;

const ChatMessage = styled.div`
  border: 1px solid ${color("gray")};
  border-radius: 8px;
  padding: ${spacing("small")};
  background: ${color("backgroundOffset")};
  white-space: pre-line;
`;

const ChatInput = styled.textarea`
  width: 100%;
  min-height: 90px;
  box-sizing: border-box;
  resize: vertical;
  border: 1px solid ${color("gray")};
  border-radius: 8px;
  padding: ${spacing("small")};
  font: inherit;
`;

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export const Navbar: React.FC<NavbarProps> = ({
  showRunInformation,
  memoryUsage,
  title,
  onNavigateHome,
  onOpenHelp,

  ...rest
}) => {
  const notify = useNotification();
  const navigate = useNavigate();
  const [runName, setRunName] = useState<string>(title ?? "");
  const [isWorkflowSaveOpen, setIsWorkflowSaveOpen] = useState(false);
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [chatInput, setChatInput] = useState("");
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [isSendingChatMessage, setIsSendingChatMessage] = useState(false);
  // <-- Modal for run properties and edit -->
  const [isRunSettingsOpen, openRunSettings, closeRunSettings] = useToggleableState();
  const refRunSettings = useRef<HTMLDivElement>(null);
  useOutsidePress(refRunSettings, closeRunSettings, isRunSettingsOpen, false);

  const onChangeRunName = (newRunName: string) => {
    setRunName(newRunName);
    void navigate("/", { state: { newRunName } });
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

  // <-- Modal for general settings -->
  const [isSettingsOpen, openSettings, closeSettings] = useToggleableState(false);
  const [hasChanges, setHasChanges] = useState(false);
  const [isDiscardModalOpen, openDiscardModal, closeDiscardModal] = useToggleableState(false);

  const handleDiscard = () => {
    closeSettings();
    closeDiscardModal();
  };
  const handleSettingsClose = (hasChanges = false) => {
    if (hasChanges) {
      openDiscardModal();
    } else {
      closeSettings();
    }
  };

  const handleSendChatMessage = async () => {
    const trimmedMessage = chatInput.trim();
    if (!trimmedMessage) {
      return;
    }

    const nextMessages = [...chatMessages, { role: "user" as const, content: trimmedMessage }];
    setChatMessages(nextMessages);
    setChatInput("");

    setIsSendingChatMessage(true);
    const response = await callApiWithParameters("send_chat_message", {
      messages: nextMessages,
    });
    setIsSendingChatMessage(false);

    if (response?.success && response.answer) {
      setChatMessages((messages) => [
        ...messages,
        { role: "assistant", content: response.answer as string },
      ]);
      return;
    }

    notify({
      title: "Chat failed",
      message: response?.message ? String(response.message) : "The AI did not return an answer.",
      type: "error",
    });
  };

  const handleWorkflowSave = useCallback(
    (data: Record<string, InputValueType>) => {
      const workflowname = data.workflowname;
      if (!workflowname) {
        notify({
          title: "Error",
          message: "Please enter a name for your workflow.",
          type: "error",
        });
        return;
      }
      void callApiWithParameters("save_workflow/", {
        run_name: runName,
        workflow_name: workflowname,
      }).then(() => {
        setIsWorkflowSaveOpen(false);
      });
    },
    [notify, runName],
  );

  // <-- render -->
  return (
    <FlexColumn {...rest}>
      <NavbarBody>
        <NavbarLeft>
          <Button icon={"home"} onPress={onNavigateHome} />
        </NavbarLeft>
        <NavbarCenter>
          <NavbarCenterTitle text={showRunInformation ? runName : "PROTzilla"} />
          {showRunInformation && (
            <div>
              <Button
                icon={"edit"}
                onPointerDown={isRunSettingsOpen ? undefined : openRunSettings}
              />
              <Button
                icon={"save"}
                onPress={() => {
                  setIsWorkflowSaveOpen(true);
                }}
              />
            </div>
          )}
        </NavbarCenter>

        <NavbarRight>
          {showRunInformation && memoryUsage !== undefined && (
            <MemoryDiv>
              <Icon icon={"memory"} color={"onPrimary"} />
              <MemoryUsageTitle>{memoryUsage}</MemoryUsageTitle>
            </MemoryDiv>
          )}
          <Button
            icon={"chat"}
            onPress={() => {
              setIsChatOpen(true);
            }}
          />
          <Button icon={"help"} onPress={onOpenHelp} />
          <Button icon={"settings"} onPress={openSettings} />
        </NavbarRight>
      </NavbarBody>
      <RunEditMenu
        runName={runName}
        onChangeRunName={onChangeRunName}
        handleAddTag={(tag: string) => {
          handleAddTag(tag);
        }}
        handleDeleteTag={(tagToDelete: string) => {
          handleDeleteTag(tagToDelete);
        }}
        handleToggleFavourite={() => {
          handleToggleFavourite();
        }}
        isOpen={isRunSettingsOpen}
        onClose={closeRunSettings}
        ref={refRunSettings}
      />
      <Settings
        isOpen={isSettingsOpen}
        onClose={handleSettingsClose}
        hasChanges={hasChanges}
        setHasChanges={setHasChanges}
      />
      <DiscardModal
        isOpen={isDiscardModalOpen}
        onDiscard={handleDiscard}
        onClose={closeDiscardModal}
      />
      <Modal
        title="Chat"
        isOpen={isChatOpen}
        onClose={() => {
          setIsChatOpen(false);
        }}
      >
        <ChatMessages>
          {chatMessages.map((message, index) => (
            <ChatMessage key={index.toString()}>
              <strong>{message.role === "user" ? "You" : "AI"}:</strong> {message.content}
            </ChatMessage>
          ))}
        </ChatMessages>
        <ChatInput
          value={chatInput}
          placeholder="Type a message..."
          onChange={(event) => {
            setChatInput(event.target.value);
          }}
        />
        <div style={{ display: "flex", justifyContent: "flex-end", marginTop: spacing("small") }}>
          <Button
            text={isSendingChatMessage ? "Sending..." : "Send"}
            onPress={() => void handleSendChatMessage()}
            isDisabled={isSendingChatMessage || !chatInput.trim()}
          />
        </div>
      </Modal>
      <Modal
        title="Save run as a custom workflow"
        isOpen={isWorkflowSaveOpen}
        onClose={() => {
          setIsWorkflowSaveOpen(false);
        }}
      >
        <Form
          formData={{
            label: "",
            labelSubmitButton: "Save workflow",
            isAutoSubmit: false,
            hasChangeIndicator: false,
            input_fields: [
              {
                type: "text",
                name: "workflowname",
                label: "With workflow name:",
                isVisible: true,
              },
            ],
          }}
          onChange={(data) => {
            handleWorkflowSave(data);
          }}
        ></Form>
      </Modal>
    </FlexColumn>
  );
};
