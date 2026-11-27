import { useNotification } from "@protzilla/app";
import { Button, DropdownInputField, SectionTitle, TextInputField } from "@protzilla/core";
import { spacing } from "@protzilla/theme";
import { callApi, callApiWithParameters } from "@protzilla/utils";
import { useEffect, useState } from "react";
import { styled } from "styled-components";

const SettingsSection = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${spacing("small")};
  max-width: 520px;
`;

const ButtonRow = styled.div`
  display: flex;
  justify-content: flex-end;
  padding-top: ${spacing("small")};
`;

const toOptions = (values: string[]) => values.map((value) => ({ label: value, value }));

export const AISettings = () => {
  const notify = useNotification();
  const [providers, setProviders] = useState<{ label: string; value: string }[]>([]);
  const [models, setModels] = useState<{ label: string; value: string }[]>([]);
  const [provider, setProvider] = useState("");
  const [model, setModel] = useState("");
  const [apiKey, setApiKey] = useState("");

  useEffect(() => {
    void (async () => {
      const availableProviders = await callApi("get_ai_providers");
      if (availableProviders) {
        setProviders(toOptions(availableProviders as string[]));
      }

      const savedSettings = await callApi("load_ai_settings");
      if (!savedSettings) {
        return;
      }

      setProvider(savedSettings.provider as string);
      setModel(savedSettings.model as string);
      setApiKey(savedSettings.api_key as string);
    })();
  }, []);

  useEffect(() => {
    void (async () => {
      if (!provider) {
        setModels([]);
        setModel("");
        return;
      }

      const availableModels = await callApiWithParameters("get_ai_models", { provider });
      if (!availableModels) {
        setModels([]);
        setModel("");
        return;
      }

      const nextModels = toOptions(availableModels as string[]);
      setModels(nextModels);
      if (nextModels.length === 0) {
        setModel("");
      }
    })();
  }, [provider]);

  const handleSave = async () => {
    const response = await callApiWithParameters("save_ai_settings", {
      provider,
      model,
      api_key: apiKey,
    });

    if (response?.success) {
      notify({
        title: "Saved successfully",
        message: "Your AI settings have been saved.",
        type: "success",
      });
      return;
    }

    notify({
      title: "Saving failed",
      message: response?.message ?? "An unexpected error occurred.",
      type: "error",
    });
  };

  return (
    <SettingsSection>
      <SectionTitle
        baseComponent={"h2"}
        title={"AI Settings"}
        description={"Select a LiteLLM provider, one of its models, and your API key."}
      />
      <DropdownInputField
        label="Provider"
        options={providers}
        value={provider}
        onChange={(value) => {
          setProvider(value);
        }}
      />
      <DropdownInputField
        label="Model"
        options={models}
        value={model}
        onChange={(value) => {
          setModel(value);
        }}
      />
      <TextInputField
        label="API Key"
        value={apiKey}
        onChange={setApiKey}
        placeholder="Enter API key"
      />
      <ButtonRow>
        <Button text="Save" onPress={() => void handleSave()} />
      </ButtonRow>
    </SettingsSection>
  );
};
