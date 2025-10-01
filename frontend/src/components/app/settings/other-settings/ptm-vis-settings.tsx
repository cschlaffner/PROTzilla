import { useNotification } from "@protzilla/app";
import { Form, SectionTitle, Text } from "@protzilla/core";
import { spacing } from "@protzilla/theme";
import { callApiWithParameters } from "@protzilla/utils";
import { useEffect, useState } from "react";
import { styled } from "styled-components";

const isColorLight = (hex_color_string: string): boolean => {
  // Taken from https://stackoverflow.com/a/12043228
  const color = hex_color_string.substring(1); // strip #
  const rgb = parseInt(color, 16); // convert rrggbb to decimal
  const r = (rgb >> 16) & 0xff; // extract red
  const g = (rgb >> 8) & 0xff; // extract green
  const b = (rgb >> 0) & 0xff; // extract blue

  const luma = 0.2126 * r + 0.7152 * g + 0.0722 * b; // per ITU-R BT.709
  return luma > 128;
};

const ColorText = styled(Text)`
  color: ${(props) => props.text ?? "#000000"};
  background-color: ${(props) => {
    return isColorLight(props.text ?? "#ffffff") ? "#000000" : "#ffffff";
  }};
  font-weight: bold;
`;

const SettingsTitle = styled(SectionTitle)`
  padding-top: ${spacing("large")};
  padding-bottom: ${spacing("small")};
`;

const SettingsSectionTitle = styled(SectionTitle)`
  padding-top: ${spacing("small")};
  padding-bottom: ${spacing("small")};
`;

const SettingsList = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${spacing("verySmall")};
`;

const SettingsEntry = styled.div`
  display: flex;
  justify-content: space-between;
  align-content: center;
  flex-direction: column;
  width: 90%;
`;

interface PTMProps {
  name: string;
  color: string;
  sites: string;
}

const PTM = ({ name, color, sites }: PTMProps) => {
  return (
    <div>
      <Text text={name + ":"} style={{ fontWeight: "bold" }} />
      <Text text=" Color: " />
      <ColorText text={color} />
      <Text text={", Sites: " + sites.split("").join(", ")} />
    </div>
  );
};

interface ColorSettingsProps {
  sequence_region_colors: Record<string, string>;
  cleavage_label_color: string;
  cleavage_scale_color_low: string;
  cleavage_scale_color_mid: string;
  cleavage_scale_color_high: string;
  ptm_scale_color_low: string;
  ptm_scale_color_mid: string;
  ptm_scale_color_high: string;
}

const ColorSettings = ({
  sequence_region_colors,
  cleavage_label_color,
  cleavage_scale_color_low,
  cleavage_scale_color_mid,
  cleavage_scale_color_high,
  ptm_scale_color_low,
  ptm_scale_color_mid,
  ptm_scale_color_high,
}: ColorSettingsProps) => {
  return (
    <div>
      <div>
        <Text text={"Cleavage label color: "} />
        <ColorText text={cleavage_label_color} />
      </div>
      <div>
        <Text text={"Cleavage scale colors: Low: "} />
        <ColorText text={cleavage_scale_color_low} />
        <Text text={", Mid: "} />
        <ColorText text={cleavage_scale_color_mid} />
        <Text text={", High: "} />
        <ColorText text={cleavage_scale_color_high} />
      </div>
      <div>
        <Text text={"PTM scale colors: Low: "} />
        <ColorText text={ptm_scale_color_low} />
        <Text text={", Mid: "} />
        <ColorText text={ptm_scale_color_mid} />
        <Text text={", High: "} />
        <ColorText text={ptm_scale_color_high} />
      </div>
      <Text text="Sequence Region Colors:" />
      {Object.entries(sequence_region_colors).map(([region, color], index) => (
        <div key={index}>
          <Text text={region + ": "} style={{ paddingLeft: "12px" }} />
          <ColorText text={color} />
        </div>
      ))}
    </div>
  );
};

interface PTMSettingsProps {
  modifications: PTMProps[];
  color_settings: ColorSettingsProps;
  label_angle: number;
  vertical_orientation: boolean;
  handleDelete?: () => void;
}

const PTMSettings = ({
  modifications,
  color_settings,
  label_angle,
  vertical_orientation,
}: PTMSettingsProps) => {
  return (
    <div>
      <SettingsSectionTitle baseComponent="h5" title="Custom PTM Settings" />
      {modifications.map((modification, index) => (
        <SettingsEntry key={index}>
          <PTM name={modification.name} color={modification.color} sites={modification.sites} />
        </SettingsEntry>
      ))}
      <SettingsSectionTitle baseComponent="h5" title="Custom Color Settings" />
      <ColorSettings
        sequence_region_colors={color_settings.sequence_region_colors}
        cleavage_label_color={color_settings.cleavage_label_color}
        cleavage_scale_color_low={color_settings.cleavage_scale_color_low}
        cleavage_scale_color_mid={color_settings.cleavage_scale_color_mid}
        cleavage_scale_color_high={color_settings.cleavage_scale_color_high}
        ptm_scale_color_low={color_settings.ptm_scale_color_low}
        ptm_scale_color_mid={color_settings.ptm_scale_color_mid}
        ptm_scale_color_high={color_settings.ptm_scale_color_high}
      />
      <SettingsSectionTitle baseComponent="h5" title="Other Settings" />
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

export const PTMVisSettings = () => {
  const notify = useNotification();
  // TODO: not ideal to initialize all of this here  - maybe at least move to variable
  const [ptmSettings, setPTMSettings] = useState<PTMSettingsProps>({
    modifications: [],
    color_settings: {
      sequence_region_colors: {
        A: "#1f77b4",
      },
      cleavage_label_color: "#ff7f0e",
      cleavage_scale_color_low: "#d62728",
      cleavage_scale_color_mid: "#ffbb78",
      cleavage_scale_color_high: "#98df8a",
      ptm_scale_color_low: "#9467bd",
      ptm_scale_color_mid: "#c5b0d5",
      ptm_scale_color_high: "#8c564b",
    },
    label_angle: 0,
    vertical_orientation: false,
  });

  const fetchPTMSettings = async (templateName: string) => {
    const response = await callApiWithParameters("load_ptm_settings", {
      templateName: templateName,
    });
    if (response) {
      const ptmSettings: PTMSettingsProps = {
        modifications: Object.values(response.modifications),
        color_settings: response.color_settings,
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
    ptmSettingsFile: string,
    colorSettingsFile: string,
    labelAngle: number,
    verticalOrientation: boolean,
  ) => {
    const response = await callApiWithParameters("save_ptm_settings", {
      ptm_settings_file: ptmSettingsFile,
      color_settings_file: colorSettingsFile,
      label_angle: labelAngle,
      vertical_orientation: verticalOrientation,
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
              name: "color_settings_file",
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
            data.ptm_settings_file as string,
            data.color_settings_file as string,
            data.label_angle as number,
            data.vertical_orientation as boolean,
          );
        }}
      />
      <SettingsTitle baseComponent={"h2"} title={"Current Settings"} />
      <SettingsList>
        {
          <PTMSettings
            modifications={ptmSettings.modifications}
            color_settings={ptmSettings.color_settings}
            label_angle={ptmSettings.label_angle}
            vertical_orientation={ptmSettings.vertical_orientation}
          />
        }
      </SettingsList>
    </div>
  );
};
