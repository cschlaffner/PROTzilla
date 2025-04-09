import { styled } from "styled-components";

import { size, spacing } from "../../../theme";
import { InvisibleButton, SecondaryButton } from "../../button";
import { Icon } from "../../icon";
import { SectionTitle } from "../../section-title";
import { Text } from "../../text";
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

export const Github = () => {
  const onOpenGithub = () => {
    window.open("https://github.com/cschlaffner/PROTzilla", "_blank");
  };

  const onOpenGithubIssue = () => {
    window.open(
      "https://github.com/cschlaffner/PROTzilla/issues/new/choose",
      "_blank",
    );
  };

  const copyCitation = () => {
    void navigator.clipboard.writeText(citation);
    // TODO add message
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
          <InvisibleButton
            onPress={onOpenGithub}
            icon={"github"}
            text={"Github"}
          />
          <span>Version: 0.0.0.0</span>
          <span>Last Update: Apr-08-2025</span>
        </InnerContentDiv>
        <InnerContentDiv>
          <SectionTitle baseComponent={"h4"} title={"How to contribute"} />
          <CenteredText
            text={
              "As of now, we are not accepting contributions outside the current Bachelorproject at Prof. Renard's chair at HPI. However, if you have any suggestions, ideas or questions, feel free to reach out to us!"
            }
          />
          <SecondaryButton
            text={"Open an issue or report a bug"}
            onPress={onOpenGithubIssue}
          />
        </InnerContentDiv>
        <InnerContentDiv>
          <SectionTitle baseComponent={"h4"} title={"How to cite"} />
          <CenteredText
            text={
              "If you use PROTzilla in your research, please cite the following paper:"
            }
          />
          <CenteredText text={"TODO: " + citation} />
          <SecondaryButton text={"Copy citation"} onPress={copyCitation} />
        </InnerContentDiv>
      </ContentDiv>
    </CenteredDiv>
  );
};
