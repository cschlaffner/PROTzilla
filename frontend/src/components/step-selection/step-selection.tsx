import { Modal } from "../modal";
import { StepSelectionProps } from "./step-selection.props.ts";
import { styled } from "styled-components";
import { useEffect, useState } from "react";

const WideModal = styled(Modal)`
  width: 100%;
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
    <WideModal
      isOpen={isOpen}
      onClose={onClose}
      className={""}
      title={"Step Selection"}
    >
      <div>
        <h1>List from Backend</h1>
        <p>check if list is empty: {list.length}</p>

        <ul>
          {list.map((item, index) => (
            <li key={index}>{item}</li>
          ))}
        </ul>
      </div>
    </WideModal>
  );
};
