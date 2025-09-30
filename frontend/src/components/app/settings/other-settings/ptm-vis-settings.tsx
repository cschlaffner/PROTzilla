import { useNotification } from "@protzilla/app";
import { Form, SectionTitle, Text } from "@protzilla/core";
import { spacing } from "@protzilla/theme";
import { callApiWithParameters } from "@protzilla/utils";
import { useEffect, useState } from "react";
import { styled } from "styled-components";

const SettingsTitle = styled(SectionTitle)`
  padding-top: ${spacing("large")};
  padding-bottom: ${spacing("small")};
`;

const SettingsList = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${spacing("verySmall")};
`;

interface PTMSettingsProps {
  label_angle: number;
  vertical_orientation: boolean;
  ptm_settings_file: string;
  handleDelete?: () => void;
}

const SettingsEntry = styled.div`
  display: flex;
  justify-content: space-between;
  align-content: center;
  flex-direction: column;
  width: 90%;
`;

const PTMSettings = ({ label_angle, vertical_orientation }: PTMSettingsProps) => {
  return (
    // TODO: probably replace div
    <div>
      <SettingsEntry>
        <Text text={"Angle of modification labels: " + label_angle.toString()} />
      </SettingsEntry>
      <SettingsEntry>
        <Text
          text={
            "Orientation of protein sequence: " + (vertical_orientation ? "Vertical" : "Horizontal")
          }
        />
      </SettingsEntry>
    </div>
  );
};

// ###################################
// TODO: probably have to redo some of the stuff here, since we will have to different settings
//   1. The element which contains stuff that is sent to the backend
//   2. The element which contains stuff that is only for visualization (preprocessed by backend,
//      e.g. the parsed CSVs)

export const PTMVisSettings = () => {
  const notify = useNotification();
  const [ptmSettings, setPTMSettings] = useState<PTMSettingsProps>({
    label_angle: 0,
    vertical_orientation: false,
  });

  const fetchPTMSettings = async (templateName: string) => {
    const response = await callApiWithParameters("load_ptm_settings", {
      templateName: templateName,
    });
    if (response) {
      const ptmSettings: PTMSettingsProps = {
        label_angle: response.label_angle,
        vertical_orientation: response.vertical_orientation,
      };
      setPTMSettings(ptmSettings);
    }
  };

  useEffect(() => {
    void fetchPTMSettings("ptm_settings");
  }, []);

  const handlePTMSettingsUpdate = async (
    labelAngle: number,
    verticalOrientation: boolean,
    ptmSettingsFile: string,
  ) => {
    const response = await callApiWithParameters("save_ptm_settings", {
      label_angle: labelAngle,
      vertical_orientation: verticalOrientation,
      ptm_settings_file: ptmSettingsFile,
    });
    if (response?.success) {
      notify({
        title: "PTM Settings updated",
        message: response.message as string,
        type: "success",
        isClosingAutomatically: true,
      });
    } else {
      notify({
        title: "PTM settings update failed",
        message: response.message ?? "Unknown error",
        type: "error",
        isClosingAutomatically: true,
      });
    }

    void fetchPTMSettings("ptm_settings");
  };

  /** TODO
   - [ ] verfügbare Modifications (in Kurzform als dict key)
     - [ ] Mapping auf Farben
     - [ ] Lang-Namen
     - [ ] Sites
   - colors
     - [ ] Cleavage und PTM colors (see e.g. CLEAVAGE_LABEL_COLOR) - TODO: mainly for details
     - [ ] Sequence Region colors (A und B)
   - [ ] Legend titles TODO: maybe integrate in file above
   - [X] Angle of labels
   - [X] Figure Orientation
   - [-] Inversion of AXIS group (A/B) -- seems redundant if user can specifiy where to plot
   - [ ] Maybe multi-select to arrange PTMs into above/below (- or also steer via file)
   **/

  return (
    <div>
      <SectionTitle
        baseComponent={"h2"}
        title={"PTM Visualizations"}
        style={{ paddingBottom: "4px" }}
      />
      <SectionTitle
        baseComponent={"h6"}
        description={"Select which PTMs should be visualized and adapt the corresponding plots."}
        style={{ paddingBottom: "8px" }}
      />
      <Form
        formData={{
          label: "",
          labelSubmitButton: "Update settings",
          isAutoSubmit: false,
          hasChangeIndicator: false,
          input_fields: [
            {
              // TODO: some kind of specification would be nice
              // TODO: optional colors
              type: "file",
              name: "ptm_settings_file",
              label: "Upload custom PTM settings (CSV file):",
              isVisible: true,
            },
            {
              // TODO: some kind of specification would be nice
              type: "file",
              name: "colors_file",
              label: "Upload custom colors (CSV file):",
              isVisible: true,
            },
            {
              type: "single-checkbox",
              name: "vertical_orientation",
              label: "Figure orientation",
              text: "Plot protein sequences vertically",
              isVisible: true,
            },
            {
              type: "number",
              name: "label_angle",
              label: "Angle of modification labels (in degrees)",
              value: 0,
              min: 0,
              max: 359,
              isVisible: true,
            },
          ],
        }}
        onChange={(data) => {
          void handlePTMSettingsUpdate(
            data.label_angle as number,
            data.vertical_orientation as boolean,
            data.ptm_settings_file as string,
          );
        }}
      />
      <SettingsTitle baseComponent={"h2"} title={"Current Settings"} />
      <SettingsList>
        {
          <PTMSettings
            label_angle={ptmSettings.label_angle}
            vertical_orientation={ptmSettings.vertical_orientation}
          />
        }
      </SettingsList>
    </div>
  );
};
