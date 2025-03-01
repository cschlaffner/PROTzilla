import { Modal } from "../modal";
import { StepSelectionProps } from "./step-selection.props.ts";
import { styled } from "styled-components";
import { useEffect, useState } from "react";

const TestBorder = styled.div`
  height: 50vh;
  width: 100%;
  border: #1a1d20;
  background: #1a1d20;
  position: relative;
`;

const WideModal = styled(Modal)`
  width: 90%;
  max-height: 100vh;
`;

const TestDiv = styled.div`
  height: 100%;
  overflow: hidden;
  overflow-y: auto;
`;

const StepList = styled.ul`
  overflow: hidden;
  overflow-y: scroll;
`;

export const StepSelection: React.FC<StepSelectionProps> = ({
  isOpen,
  onClose,
}) => {
  const [list, setList] = useState([]);

  useEffect(() => {
    const fetchList = async () => {
      try {
        const response = await fetch(
          "http://127.0.0.1:8000/api/step_name_list/",
        );
        if (!response.ok) {
          throw new Error("Network response was not ok");
        }
        const data = await response.json();
        setList(data);
      } catch (error) {
        console.error("Error fetching the list", error);
      }
    };

    fetchList();
  }, []);

  return (
    <TestBorder>
      <WideModal
        isOpen={isOpen}
        onClose={onClose}
        className={""}
        title={"Step Selection"}
      >
        <TestDiv>
          <StepList>
            {list.map((item, index) => (
              <li key={index}>{item}</li>
            ))}
          </StepList>
        </TestDiv>
      </WideModal>
    </TestBorder>
  );
};
