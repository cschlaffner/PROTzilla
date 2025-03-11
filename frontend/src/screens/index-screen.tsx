import React, { useEffect, useState } from "react";
import { Col, Container, Row } from "react-grid-system";
import { useNavigate } from "react-router-dom";

import { Button, Card, Dropdown, TextField } from "../components";
import "bootstrap/dist/css/bootstrap.min.css";
import { defaultPalette } from "../theme";

export const IndexScreen: React.FC = () => {
  const [newRunName, setNewRunName] = useState("");
  const [workflow, setWorkflow] = useState("standard");
  const [memoryMode, setMemoryMode] = useState("standard");
  const [existingRun, setExistingRun] = useState("nothing here yet");
  const [runs, setRuns] = useState<{ value: string; label: string }[]>([]);
  const navigate = useNavigate();

  useEffect(() => {
    fetch("http://127.0.0.1:8000/api/jannesjsontest/")
      .then((response) => response.json())
      .then((data: { value: string; label: string }[]) => {
        setRuns(data);
      })
      .catch((error: unknown) => {
        console.error("Error fetching data:", error);
      });
  }, []);

  const handleCreateRun = () => {
    if (runs.some((run) => run.value === newRunName)) {
      alert("A run with this name already exists!");
      return;
    }
    setRuns([...runs, { value: newRunName, label: newRunName }]);
    setNewRunName("");
    console.log(runs);
  };

  const handleContinueRun = () => {
    console.log("Continue Run:", existingRun);
    void navigate("/run");
  };

  const handleDeleteRun = () => {
    setRuns(runs.filter((run) => run.value !== existingRun));
    setExistingRun(runs[0]?.value || "");
    console.log(runs);
  };

  return (
    <div className="min-vh-100 w-100 bg-light">
      <header
        style={{
          backgroundColor: defaultPalette.primary, // Verwendung der Theme-Farbe
          color: defaultPalette.onPrimary,
        }}
        className=" text-white py-3 px-4 d-flex justify-content-between align-items-center"
      >
        <h1 className="h4 mb-0">PROTzilla</h1>
        <a href="https://github.com" className="text-white">
          GitHub
        </a>
      </header>
      <Container>
        <Row gutterWidth={16} justify="between" align="center" style={{ height: "80vh" }}>
          <Col md={4}>
            <Card title="Work on a new run:">
              <TextField
                label="Add run name:"
                placeholder="Enter run name"
                value={newRunName}
                onChange={(e) => {setNewRunName(e.target.value)}}
                className="mb-3"
              />
              <Dropdown
                label="With workflow:"
                options={[
                  { value: "standard", label: "Standard" },
                  { value: "example-workflow", label: "Example"}
                ]}
                value={workflow}
                onChange={(value) => {setWorkflow(value)}}
                className="mb-3"
              />
              <Dropdown
                label="Memory mode:"
                options={[
                  { value: "standard", label: "Standard" },
                  { value: "low-memory", label: "Low Memory" },
                ]}
                value={memoryMode}
                onChange={(value) => {setMemoryMode(value)}}
                className="mb-3"
              />
              <Button className="btn btn-primary w-100" onClick={handleCreateRun}>Create</Button>
            </Card>
          </Col>
          {/* Continue Run Section */}
          <Col md={4}>
            <Card title="Continue an existing run:">
              <Dropdown
                label="Select run:"
                options={runs}
                value={existingRun}
                onChange={(value) => {setExistingRun(value)}}
                className="mb-3"
              />
              <Button className="btn btn-primary w-100 mb-2" onClick={handleContinueRun}>Continue</Button>
              <Button className="btn btn-secondary w-100">Manage databases</Button>
            </Card>
          </Col>

          {/* Delete Run Section */}
          <Col md={4}>
            <Card title="Delete an existing run:">
              <Dropdown
                label="Select run:"
                options={runs}
                value={existingRun}
                onChange={(value) => {setExistingRun(value)}}
                className="mb-3"
              />
              <Button className="btn btn-danger w-100" onClick={handleDeleteRun}>Delete</Button>
            </Card>
          </Col>
        </Row>
      </Container>

    </div>
  );
};
