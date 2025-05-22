import { useNotification } from "@protzilla/app";
import { SecondaryButton, SectionTitle } from "@protzilla/core";
import { Icon, Text } from "@protzilla/core/shared";
import { size, spacing } from "@protzilla/theme";
import { styled } from "styled-components";

import { citation } from "./citation.ts";

const Logo = styled(Icon)`
  width: ${size("logoIconWidth")};
  height: ${size("logoIconHeight")};
  padding: ${spacing("medium")};
`;

const TitleDiv = styled.div`
  display: flex;
  flex-direction: column;
  align-items: self-start;
  gap: ${spacing("small")};
`;

const Header = styled.div`
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  gap: ${spacing("small")};
`;

const ContentDiv = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: ${spacing("large")};
`;

const InnerContentDiv = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: ${spacing("verySmall")};
`;

const CenteredText = styled(Text)`
  text-align: center;
`;

const CenteredDiv = styled.div`
  padding-right: 100px;
`;

export const GitHub = () => {
  const notify = useNotification();

  const onOpenGitHub = () => {
    window.open("https://github.com/cschlaffner/PROTzilla", "_blank");
  };

  const onOpenGitHubIssue = () => {
    window.open("https://github.com/cschlaffner/PROTzilla/issues/new/choose", "_blank");
  };

  const copyCitation = () => {
    void navigator.clipboard.writeText(citation);
    notify({
      title: "Success",
      message: "Citation copied to clipboard",
      type: "success",
    });
  };

  return (
    <CenteredDiv>
      <Header>
        <TitleDiv>
          <SectionTitle baseComponent={"h1"} title={"PROTzilla"} />
          <SectionTitle
            baseComponent={"h4"}
            description={"An open-source project at Hasso Plattner Institute"}
          />
        </TitleDiv>
        <Logo icon={"protzilla"} />
      </Header>
      <ContentDiv>
        <InnerContentDiv>
          <SecondaryButton onPress={onOpenGitHub} icon={"github"} text={"Github"} />
          <span>Version: 0.0.0.0</span>
          <span>Last Update: Apr-08-2025</span>
        </InnerContentDiv>
        <InnerContentDiv>
          <SectionTitle baseComponent={"h4"} title={"How to contribute"} />
          <CenteredText
            text={
              "As of now, we are not accepting contributions outside the current Bachelorproject at DACS' chair at HPI. However, if you have any suggestions, ideas or questions, feel free to reach out to us!"
            }
          />
          <SecondaryButton text={"Open an issue or report a bug"} onPress={onOpenGitHubIssue} />
        </InnerContentDiv>
        <InnerContentDiv>
          <SectionTitle baseComponent={"h4"} title={"How to cite"} />
          <CenteredText
            text={"If you use PROTzilla in your research, please cite the following paper:"}
          />
          <CenteredText text={"TODO: " + citation} />
          <SecondaryButton text={"Copy citation"} onPress={copyCitation} />
        </InnerContentDiv>
      </ContentDiv>
    </CenteredDiv>
  );
};
