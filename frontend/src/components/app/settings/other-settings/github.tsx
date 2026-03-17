import { useNotification } from "@protzilla/app";
import { Icon, SecondaryButton, SectionTitle, Text } from "@protzilla/core";
import { size, spacing } from "@protzilla/theme";
import { styled } from "styled-components";

// import { citation } from "./citation.ts";
import { licenseInfo } from "./license.ts";
import { PROTZILLA_LASTUPDATE, PROTZILLA_VERSION } from "../../../../constants.ts";

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

  const openLicence = () => {
    window.open("https://github.com/cschlaffner/PROTzilla/blob/main/LICENSE");
  };

  // TODO: Readd once citation is ready
  // const copyCitation = () => {
  //   void navigator.clipboard.writeText(citation);
  //   notify({
  //     title: "Success",
  //     message: "Citation copied to clipboard",
  //     type: "success",
  //   });
  // };

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
          <span>Version: {PROTZILLA_VERSION}</span>
          <span>Last Update: {PROTZILLA_LASTUPDATE}</span>
        </InnerContentDiv>
        <InnerContentDiv>
          <SectionTitle baseComponent={"h4"} title={"How to contribute"} />
          <CenteredText
            text={
              "PROTzilla is mainly developed internally at HPI. If you have any issues or suggestions, feel free to reach out to us!"
            }
          />
          <SecondaryButton text={"Open an issue or report a bug"} onPress={onOpenGitHubIssue} />
        </InnerContentDiv>
        <InnerContentDiv>
          <SectionTitle baseComponent={"h4"} title={"Disclaimer and License"} />
          <CenteredText text={licenseInfo} />
          <SecondaryButton onPress={openLicence} text={"Open License"} />
        </InnerContentDiv>
      </ContentDiv>
    </CenteredDiv>
  );
};
