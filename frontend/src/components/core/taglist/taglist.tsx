import { Icon } from "@protzilla/core/shared";
import { color, fontSize, radius, spacing } from "@protzilla/theme";
import { styled } from "styled-components";

import { TagListProps } from "./taglist.props";

const StyledList = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: ${spacing("superSmall")};
`;

const Tag = styled.span`
  background-color: ${color("protzillaDarkBlue")};
  color: ${color("onPrimary")};
  padding: ${spacing("tagPadding")};
  border-radius: ${radius("tag")};
  font-size: ${fontSize("default")};
  white-space: nowrap;
  display: flex;
  align-items: center;
  gap: ${spacing("verySmall")};
`;

export const TagList: React.FC<TagListProps> = ({ runName, tags, icon, handleTag }) => {
  return (
    <StyledList>
      {tags.map((tag, i) => (
        <Tag key={i}>
          {tag}
          <Icon
            icon={icon}
            color="gray"
            onClick={() => {
              handleTag(tag, runName);
            }}
            aria-label={`Remove tag ${tag}`}
            style={{
              height: "15px",
            }}
          />
        </Tag>
      ))}
    </StyledList>
  );
};
