import styled from "styled-components";

import { Icon } from "../icon";
import { TagListProps } from "./taglist.props";
import { color } from "../../theme";

const StyledList = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
`

const Tag = styled.span`
  background-color: ${color("protzillaDarkBlue")};
  color: white;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  white-space: nowrap;
  display: flex;
  align-items: center;
  gap: 6px;
`

export const TagList: React.FC<TagListProps> = ({
  runName,
  tags,
  icon,
  handleTag,
}) => {
  return (
    <StyledList>
        {tags.map((tag, i) => (
        <Tag key={i}>
            {tag}
            <Icon 
                icon={icon}
                color="gray"
                onClick={() => { handleTag(tag, runName); }}
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
