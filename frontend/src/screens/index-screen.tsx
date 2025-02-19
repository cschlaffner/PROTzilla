import React, {  useEffect, useState } from "react";
import { Dropdown, Button, TextField } from "../components";
import "bootstrap/dist/css/bootstrap.min.css";
import { defaultPalette } from "../theme";
import { callApi, callApiWithParameters } from "../utils";
//import { useFetch } from "../hooks";



export const IndexScreen: React.FC = () => {
  const [newRunName, setNewRunName] = useState("");
  const [workflow, setWorkflow] = useState("standard");
  const [memoryMode, setMemoryMode] = useState("standard");
  const [existingRun, setExistingRun] = useState("nothing here yet");
  const [runs, setRuns] = useState<any>([]);
//  const [csrfToken, setCsrfToken] = useState("");

  useEffect(() => {
    fetch('http://127.0.0.1:8000/api/jannesjsontest/')
      .then((response) => response.json())
      .then((data: { value: string; label: string }[]) => setRuns(data))
      .catch((error) => console.error('Error fetching data:', error));
  }, []);

  
    // Fetch CSRF token on component mount
/*    useEffect(() => {
      fetch("http://127.0.0.1:8000/api/get-csrf-token/")
        .then((response) => response.json())
        .then((data) => setCsrfToken(data.csrfToken))
        .catch((error) => console.error("Error fetching CSRF token:", error));
    }, []); */
  

  const handleCreateRun = () => {
    if (runs.some((run: { value: string; }) => run.value === newRunName)) {
        alert("A run with this name already exists!");
        return;
    }
    setRuns([...runs, { value: newRunName, label: newRunName }]);
    setNewRunName("");
    console.log(runs);
  };

  const handleContinueRun = () => {
    console.log("Continue Run:", existingRun);
  };

  const handleDeleteRun = () => {
    setRuns(runs.filter((run: { value: string; }) => run.value !== existingRun));
    setExistingRun(runs[0]?.value || "");
    console.log(runs)
  };


  return (
    <div className="min-vh-100 w-100 bg-light">
      <header 
        style={{
          backgroundColor: defaultPalette.primary, // Verwendung der Theme-Farbe
          color: defaultPalette.onPrimary,
        }}
        className=" text-white py-3 px-4 d-flex justify-content-between align-items-center">
        <h1 className="h4 mb-0">PROTzilla</h1>
        <a href="https://github.com" className="text-white">GitHub</a>
      </header>
      <main className="container py-5 w-100">
        <div className="row w-100 g-4 justify-content-between align-items-center">
          {/* New Run Section */}
          <div className="col-md-4">
            <div className="card shadow-sm">
              <div className="card-body">
                <h5 className="card-title">Work on a new run:</h5>
                <TextField
                  label="Add run name:"
                  placeholder="Enter run name"
                  value={newRunName}
                  onChange={(e) => setNewRunName(e.target.value)}
                  className="mb-3"
                />
                <Dropdown
                  label="With workflow:"
                  options={[
                    { value: "standard", label: "Standard" },
                    { value: "example-workflow", label: "Example"}
                  ]}
                  value={workflow}
                  onChange={(value) => setWorkflow(value)}
                  className="mb-3"
                />
                <Dropdown
                  label="Memory mode:"
                  options={[
                    { value: "standard", label: "Standard" },
                    { value: "low-memory", label: "Low Memory" },
                  ]}
                  value={memoryMode}
                  onChange={(value) => setMemoryMode(value)}
                  className="mb-3"
                />
                <Button className="btn btn-primary w-100" onClick={handleCreateRun}>Create</Button>
              </div>
            </div>
          </div>

          {/* Continue Run Section */}
          <div className="col-md-4">
            <div className="card shadow-sm">
              <div className="card-body">
                <h5 className="card-title">Continue an existing run:</h5>
                <Dropdown
                  label="Select run:"
                  options={runs}
                  value={existingRun}
                  onChange={(value) => setExistingRun(value)}
                  className="mb-3"
                />
                <Button className="btn btn-primary w-100 mb-2" onClick={handleContinueRun}>Continue</Button>
                <Button className="btn btn-primary w-100 mb-2" onClick={() => callApiWithParameters("do_something_with_element_from_frontend/", { element: "das_richtige" })}>Do something</Button>
                <Button className="btn btn-secondary w-100">Manage databases</Button>
              </div>
            </div>
          </div>

          {/* Delete Run Section */}
          <div className="col-md-4">
            <div className="card shadow-sm">
              <div className="card-body">
                <h5 className="card-title">Delete an existing run:</h5>
                <Dropdown
                  label="Select run:"
                  options={runs}
                  value={existingRun}
                  onChange={(value) => setExistingRun(value)}
                  className="mb-3"
                />
                <Button className="btn btn-danger w-100" onClick={handleDeleteRun}>Delete</Button>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};