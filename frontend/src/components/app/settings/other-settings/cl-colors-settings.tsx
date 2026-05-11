import { useNotification } from "@protzilla/app";
import { DeleteModal, Form, SecondaryButton, SectionTitle, Text } from "@protzilla/core";
import { useToggleableState } from "@protzilla/hooks";
import { spacing } from "@protzilla/theme";
import { callApi, callApiWithParameters } from "@protzilla/utils";
import { useEffect, useState } from "react";
import { styled } from "styled-components";

import { CrosslinkerType } from "../../../core/shared/molstar-viewer/crosslinker-processing";
import { CROSSLINK_DEFAULT_COLORS } from "../../../core/shared/molstar-viewer/molstar-viewer.config";

const CurrentColorsTitle = styled(SectionTitle)`
  padding-top: ${spacing("large")};
  padding-bottom: ${spacing("small")};

  margin: 0;
`;

const CurrentColorsList = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${spacing("verySmall")};
`;

const CurrentColorsHeader = styled.div`
  display: flex;
  flex-direction: row;
  align-items: flex-end;
  justify-content: space-between;
`;

const ColorEntryContainer = styled.div`
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;

  padding-left: ${spacing("listIndentation")};
  padding-top: ${spacing("verySmall")};
  padding-bottom: ${spacing("verySmall")};
`;

const ColorInfo = styled.div`
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: ${spacing("small")};
`;

const ColorPreview = styled.div<{ color: string }>`
  width: 24px;
  height: 24px;
  border-radius: 4px;
  border: 1px solid black;

  background-color: ${({ color }) => color};
`;

interface ColorEntryProps {
  label: string;
  color: number;
}

const toHexColor = (color: number) => `#${color.toString(16).padStart(6, "0")}`;

const ColorEntry = ({ label, color }: ColorEntryProps) => {
  return (
    <ColorEntryContainer>
      <ColorInfo>
        <ColorPreview color={toHexColor(color)} />

        <Text text={`${label}: ${toHexColor(color)}`} />
      </ColorInfo>
    </ColorEntryContainer>
  );
};

const entries = [
  { label: "Valid intra-crosslinks", key: CrosslinkerType.ValidIntra },
  { label: "Invalid intra-crosslinks", key: CrosslinkerType.InvalidIntra },
  { label: "Valid inter-crosslinks", key: CrosslinkerType.ValidInter },
  { label: "Invalid inter-crosslinks", key: CrosslinkerType.InvalidInter },
];

export const CrosslinkColors = () => {
  const notify = useNotification();
  const [colors, setColors] = useState(CROSSLINK_DEFAULT_COLORS);
  const [isDeleteModalOpen, openDeleteModal, closeDeleteModal] = useToggleableState(false);
  const [formKey, setFormKey] = useState(0);

  useEffect(() => {
    const loadColors = async () => {
      const result = await callApi("get_cl_colors");

      if (result && Object.keys(result).length > 0) {
        setColors(result);
      }
    };

    void loadColors();
  }, []);

  const parseColor = (value: unknown): number => {
    const str = String(value).trim();

    if (/^-?\d+$/.test(str)) return Number(str);

    if (str.startsWith("0x")) {
      const parsed = parseInt(str, 16);
      if (!Number.isNaN(parsed)) return parsed;
    }

    if (str.startsWith("#")) {
      const parsed = parseInt(str.slice(1), 16);
      if (!Number.isNaN(parsed)) return parsed;
    }

    if (/^[0-9a-fA-F]{6}$/.test(str)) {
      return parseInt(str, 16);
    }

    throw new Error("Invalid colour format");
  };

  const updateColors = (prev: typeof CROSSLINK_DEFAULT_COLORS, data: Record<string, unknown>) => {
    const update = (key: CrosslinkerType) => {
      const input = data[key];

      // if the field was left empty, we keep the old color
      if (input == null || (typeof input === "string" && input.trim() === "")) {
        return prev[key];
      }

      // non-empty fields are validated
      try {
        return parseColor(input);
      } catch {
        notify({
          title: "Invalid colour input",
          message:
            `Invalid value for ${key}.` +
            "Please enter a valid colour-code" +
            "(e.g. #FF00AA or 0xFF00AA or 6-digit hex code).",
          type: "error",
          isClosingAutomatically: true,
        });

        throw new Error("Abort update");
      }
    };

    return {
      [CrosslinkerType.ValidIntra]: update(CrosslinkerType.ValidIntra),
      [CrosslinkerType.InvalidIntra]: update(CrosslinkerType.InvalidIntra),
      [CrosslinkerType.ValidInter]: update(CrosslinkerType.ValidInter),
      [CrosslinkerType.InvalidInter]: update(CrosslinkerType.InvalidInter),
    };
  };

  const handleChangeColors = async (data: Record<string, unknown>) => {
    try {
      const updated = updateColors(colors, data);
      setColors(updated);

      const response = await callApiWithParameters("update_cl_colors", updated);
      if (response?.success) {
        notify({
          title: "Crosslink colour update",
          message: response.message as string,
          type: "success",
          isClosingAutomatically: true,
        });
      } else {
        notify({
          title: "Crosslink colour update failed",
          message: response.message ?? "Unknown error",
          type: "error",
          isClosingAutomatically: true,
        });
      }
      setFormKey((prev) => prev + 1);
    } catch {
      return;
    }
  };

  const handleResetToDefaults = async () => {
    const updated = CROSSLINK_DEFAULT_COLORS;
    setColors(updated);

    const response = await callApiWithParameters("update_cl_colors", updated);
    if (response?.success) {
      notify({
        title: "Crosslink colour reset",
        message: response.message as string,
        type: "success",
        isClosingAutomatically: true,
      });
    } else {
      notify({
        title: "Crosslink colour reset failed",
        message: response.message ?? "Unknown error",
        type: "error",
        isClosingAutomatically: true,
      });
    }
    closeDeleteModal();
  };

  const handleDelete = () => {
    openDeleteModal();
  };

  return (
    <div>
      <SectionTitle
        baseComponent={"h2"}
        title={"Select colors for the different variants of crosslinks"}
        style={{ paddingBottom: "4px" }}
      />
      <SectionTitle
        baseComponent={"h6"}
        description={
          "Select custom colors for selected or all variants of crosslinks" +
          "or revert back to the default here."
        }
        style={{ paddingBottom: "8px" }}
      />

      <Form
        key={formKey}
        formData={{
          label: "",
          labelSubmitButton: "Change colour scheme",
          isAutoSubmit: false,
          hasChangeIndicator: false,
          input_fields: [
            {
              type: "text",
              name: CrosslinkerType.ValidIntra,
              label: "Color of valid intra-crosslinks:",
              isVisible: true,
            },
            {
              type: "text",
              name: CrosslinkerType.InvalidIntra,
              label: "Color of invalid intra-crosslinks:",
              isVisible: true,
            },
            {
              type: "text",
              name: CrosslinkerType.ValidInter,
              label: "Color of valid inter-crosslinks:",
              isVisible: true,
            },
            {
              type: "text",
              name: CrosslinkerType.InvalidInter,
              label: "Color of invalid inter-crosslinks:",
              isVisible: true,
            },
          ],
        }}
        onChange={(data) => {
          handleChangeColors(data).catch(console.error);
        }}
      />

      <CurrentColorsHeader>
        <CurrentColorsTitle baseComponent={"h2"} title={"Currently selected crosslink colours"} />

        <SecondaryButton icon={"trash"} isCautious={true} onPress={handleDelete} />
      </CurrentColorsHeader>

      <CurrentColorsList>
        {entries.map((entry) => (
          <ColorEntry key={entry.key} label={entry.label} color={colors[entry.key]} />
        ))}
      </CurrentColorsList>

      <DeleteModal
        isOpen={isDeleteModalOpen}
        onClose={closeDeleteModal}
        onConfirm={() => {
          void handleResetToDefaults();
        }}
        title={
          `All crosslink colours will be reset to the developer defaults.` +
          `Your currently selected colours will be permanently deleted. Would you like to proceed?`
        }
      />
    </div>
  );
};
