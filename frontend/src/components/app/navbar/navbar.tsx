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

import { API_ROOT } from "../../../constants";
import { ensureCSRFToken } from "../../../utils/api-call";

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

const ChatModal = styled(Modal)`
  width: min(960px, 95vw);
  max-width: 95vw;
`;

const ChatBody = styled.div`
  width: min(900px, 88vw);
  height: 75vh;
  max-height: 75vh;
  display: flex;
  flex-direction: column;
`;

const ChatMessages = styled.div`
  min-height: 420px;
  max-height: 56vh;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: ${spacing("small")};
  padding-bottom: ${spacing("small")};
  flex: 1;
`;

const ChatMessage = styled.div<{ $role: "user" | "assistant" }>`
  border: 1px solid ${(props) => (props.$role === "user" ? color("primary") : color("gray"))};
  border-radius: 8px;
  padding: ${spacing("small")};
  background: ${(props) => (props.$role === "user" ? color("primary") : "white")};
  color: ${(props) => (props.$role === "user" ? color("onPrimary") : color("primary"))};
  white-space: pre-line;
  max-width: 85%;
  align-self: ${(props) => (props.$role === "user" ? "flex-end" : "flex-start")};
`;

const ChatInput = styled.textarea`
  width: 100%;
  min-height: 120px;
  box-sizing: border-box;
  resize: vertical;
  border: 1px solid ${color("gray")};
  border-radius: 8px;
  padding: ${spacing("small")};
  font: inherit;
`;

const TraceDetails = styled.details`
  margin: ${spacing("small")} 0;
  padding: ${spacing("small")};
  background: ${color("backgroundOffset")};
  color: ${color("primary")};
  border-left: 4px solid ${color("primary")};
`;

const TraceSummary = styled.summary`
  cursor: pointer;
  font-weight: ${fontWeight("bold")};
`;

const TracePre = styled.pre`
  margin: ${spacing("verySmall")} 0 0 ${spacing("medium")};
  white-space: pre-wrap;
  word-break: break-word;
  font: inherit;
`;

const LoadingRow = styled.div`
  display: flex;
  justify-content: flex-start;
  padding: ${spacing("small")};
`;

const LoadingSpinner = styled(Icon)`
  width: 28px;
  height: 28px;

  @keyframes rotation {
    from {
      transform: rotate(0deg);
    }
    to {
      transform: rotate(359deg);
    }
  }

  animation: rotation 1.5s infinite linear;
`;

interface ChatToolTraceEntry {
  type: "trace";
  toolCallId?: string;
  tool: string;
  arguments: unknown;
  result: unknown;
}

interface ChatBubbleMessage {
  type: "message";
  role: "user" | "assistant";
  content: string;
}

type ChatEntry = ChatBubbleMessage | ChatToolTraceEntry;

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
  const [chatMessages, setChatMessages] = useState<ChatEntry[]>([]);
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

    const nextMessages = [
      ...chatMessages,
      { type: "message" as const, role: "user" as const, content: trimmedMessage },
    ];
    setChatMessages(nextMessages);
    setChatInput("");

    setIsSendingChatMessage(true);
    try {
      const csrfToken = await ensureCSRFToken();
      const response = await fetch(`${API_ROOT}send_chat_message`, {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },
        body: JSON.stringify({
          messages: nextMessages
            .filter((message) => message.type === "message")
            .map((message) => ({
              role: message.role,
              content: message.content,
            })),
        }),
      });

      if (!response.ok || !response.body) {
        throw new Error("The AI did not return an answer.");
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      for (;;) {
        const { value, done: isDone } = await reader.read();
        if (isDone) {
          break;
        }

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() ?? "";

        for (const line of lines) {
          if (!line.trim()) {
            continue;
          }

          const event = JSON.parse(line) as
            | {
                type: "tool_start";
                tool_call_id?: string;
                tool: string;
                arguments: unknown;
              }
            | { type: "tool_result"; tool_call_id?: string; result: unknown }
            | { type: "answer"; answer: string }
            | { type: "error"; message: string };

          if (event.type === "tool_start") {
            setChatMessages((messages) => [
              ...messages,
              {
                type: "trace",
                toolCallId: event.tool_call_id,
                tool: event.tool,
                arguments: event.arguments,
                result: null,
              },
            ]);
            continue;
          }

          if (event.type === "tool_result") {
            setChatMessages((messages) =>
              messages.map((message) =>
                message.type === "trace" && message.toolCallId === event.tool_call_id
                  ? { ...message, result: event.result }
                  : message,
              ),
            );
            continue;
          }

          if (event.type === "answer") {
            setChatMessages((messages) => [
              ...messages,
              { type: "message", role: "assistant", content: event.answer },
            ]);
            continue;
          }

          throw new Error(event.message);
        }
      }

      if (buffer.trim()) {
        const event = JSON.parse(buffer) as
          | { type: "answer"; answer: string }
          | { type: "error"; message: string };
        if (event.type === "error") {
          throw new Error(event.message);
        }
        setChatMessages((messages) => [
          ...messages,
          { type: "message", role: "assistant", content: event.answer },
        ]);
      }
    } catch (error) {
      notify({
        title: "Chat failed",
        message: error instanceof Error ? error.message : "The AI did not return an answer.",
        type: "error",
      });
    } finally {
      setIsSendingChatMessage(false);
    }
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
      <ChatModal
        title="Chat"
        isOpen={isChatOpen}
        onClose={() => {
          setIsChatOpen(false);
        }}
      >
        <ChatBody>
          <ChatMessages>
            {chatMessages.map((message, index) =>
              message.type === "trace" ? (
                <TraceDetails key={index.toString()}>
                  <TraceSummary>{message.tool}</TraceSummary>
                  <TracePre>
                    {JSON.stringify(
                      {
                        arguments: message.arguments,
                        result: message.result,
                      },
                      null,
                      2,
                    )}
                  </TracePre>
                </TraceDetails>
              ) : (
                <ChatMessage key={index.toString()} $role={message.role}>
                  <strong>{message.role === "user" ? "You" : "AI"}:</strong> {message.content}
                </ChatMessage>
              ),
            )}
            {isSendingChatMessage && (
              <LoadingRow>
                <LoadingSpinner icon="spinner" color="primary" />
              </LoadingRow>
            )}
          </ChatMessages>
          <ChatInput
            value={chatInput}
            placeholder="Type a message..."
            onChange={(event) => {
              setChatInput(event.target.value);
            }}
            onKeyDown={(event) => {
              if (event.key === "Enter" && !event.shiftKey) {
                event.preventDefault();
                if (!isSendingChatMessage && chatInput.trim()) {
                  void handleSendChatMessage();
                }
              }
            }}
          />
          <div style={{ display: "flex", justifyContent: "flex-end", marginTop: spacing("small") }}>
            <Button
              text={isSendingChatMessage ? "Sending..." : "Send"}
              onPress={() => void handleSendChatMessage()}
              isDisabled={isSendingChatMessage || !chatInput.trim()}
            />
          </div>
        </ChatBody>
      </ChatModal>
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
