import { useNotification } from "@protzilla/app";
import { Form, Link, SectionTitle, Text } from "@protzilla/core";
import { spacing } from "@protzilla/theme";
import { callApi, callApiWithParameters } from "@protzilla/utils";
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

const ContentDiv = styled.div`
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: ${spacing("small")};
`;

const saveFile = (url: string, filename: string) => {
  const a = document.createElement("a");
  a.href = url;
  a.download = filename || "file-name";
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
};

const downloadYAML = () => {
  void (async () => {
    // so that the linter shuts up
    const response = await callApi("load_default_ptm_settings_yaml");
    if (response) {
      const file = new Blob([response.example_settings], { type: "text/plain" });
      const url = window.URL.createObjectURL(file);
      saveFile(url, "example_ptm_settings.yaml");
      window.URL.revokeObjectURL(url);
    }
  })();
};

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
  sites: string[];
  above_below: string;
}

const PTM = ({ name, color, sites, above_below }: PTMProps) => {
  return (
    <div>
      <Text text={name + ":"} style={{ fontWeight: "bold" }} />
      <Text text=" Color: " />
      <ColorText text={color} />
      <Text text={", Sites: " + sites.join(", ")} />
      <Text text={", Above/below sequence: " + (above_below == "A" ? "above" : "below")} />
    </div>
  );
};

interface ColorSettingsProps {
  sequence_region_colors: Record<string, string>;
  group_label_colors: Record<string, string>;
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
  group_label_colors,
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
        <div key={"sequence_region_" + index.toString()}>
          <Text text={region + ": "} style={{ paddingLeft: "12px" }} />
          <ColorText text={color} />
        </div>
      ))}
      <Text text="Group Label Colors:" />
      {Object.entries(group_label_colors).map(([group, color], index) => (
        <div key={"group_label_" + index.toString()}>
          <Text text={group + ": "} style={{ paddingLeft: "12px" }} />
          <ColorText text={color} />
        </div>
      ))}
    </div>
  );
};

interface OtherSettingsProps {
  label_angle: number;
  vertical_orientation: boolean;
}

const OtherSettings = ({ label_angle, vertical_orientation }: OtherSettingsProps) => {
  return (
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

interface PTMSettingsProps {
  modifications: PTMProps[];
  color_settings: ColorSettingsProps;
  other_settings: OtherSettingsProps;
  handleDelete?: () => void;
}

const PTMSettings = ({ modifications, color_settings, other_settings }: PTMSettingsProps) => {
  return (
    <div>
      <SettingsSectionTitle baseComponent="h5" title="Custom PTM Settings" />
      {modifications.map((modification, index) => (
        <SettingsEntry key={index}>
          <PTM
            name={modification.name}
            color={modification.color}
            sites={modification.sites}
            above_below={modification.above_below}
          />
        </SettingsEntry>
      ))}
      <SettingsSectionTitle baseComponent="h5" title="Custom Color Settings" />
      <ColorSettings
        sequence_region_colors={color_settings.sequence_region_colors}
        group_label_colors={color_settings.group_label_colors}
        cleavage_label_color={color_settings.cleavage_label_color}
        cleavage_scale_color_low={color_settings.cleavage_scale_color_low}
        cleavage_scale_color_mid={color_settings.cleavage_scale_color_mid}
        cleavage_scale_color_high={color_settings.cleavage_scale_color_high}
        ptm_scale_color_low={color_settings.ptm_scale_color_low}
        ptm_scale_color_mid={color_settings.ptm_scale_color_mid}
        ptm_scale_color_high={color_settings.ptm_scale_color_high}
      />
      <SettingsSectionTitle baseComponent="h5" title="Other Settings" />
      <OtherSettings
        label_angle={other_settings.label_angle}
        vertical_orientation={other_settings.vertical_orientation}
      />
    </div>
  );
};

export const PTMVisSettings = () => {
  const notify = useNotification();
  const [ptmSettings, setPTMSettings] = useState<PTMSettingsProps>({
    modifications: [],
    color_settings: {
      sequence_region_colors: { A: "#1f77b4" },
      group_label_colors: { A: "#2ca02c" },
      cleavage_label_color: "#ff7f0e",
      cleavage_scale_color_low: "#d62728",
      cleavage_scale_color_mid: "#ffbb78",
      cleavage_scale_color_high: "#98df8a",
      ptm_scale_color_low: "#9467bd",
      ptm_scale_color_mid: "#c5b0d5",
      ptm_scale_color_high: "#8c564b",
    },
    other_settings: {
      label_angle: 0,
      vertical_orientation: false,
    },
  });

  const fetchPTMSettings = async (templateName: string) => {
    const response = await callApiWithParameters("load_ptm_settings", {
      templateName: templateName,
    });
    if (response) {
      const ptmSettings: PTMSettingsProps = {
        modifications: Object.values(response.modifications),
        color_settings: response.color_settings,
        other_settings: response.other_settings,
      };
      setPTMSettings(ptmSettings);
    }
  };

  useEffect(() => {
    void fetchPTMSettings("ptm_settings");
  }, []);

  const handlePTMSettingsUpdate = async (ptmSettingsFile: string) => {
    const response = await callApiWithParameters("save_ptm_settings", {
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
              type: "file",
              name: "ptm_settings_file",
              label: "Upload custom PTM settings (YAML file):",
              isVisible: true,
            },
          ],
        }}
        onChange={(data) => {
          void handlePTMSettingsUpdate(data.ptm_settings_file as string);
        }}
      />
      <ContentDiv>
        <Link
          text={"Click here to download an example for a settings YAML file"}
          onClick={downloadYAML}
        />
      </ContentDiv>
      <SettingsTitle baseComponent={"h2"} title={"Current Settings"} />
      <SettingsList>
        {
          <PTMSettings
            modifications={ptmSettings.modifications}
            color_settings={ptmSettings.color_settings}
            other_settings={ptmSettings.other_settings}
          />
        }
      </SettingsList>
    </div>
  );
};
