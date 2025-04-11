import { useState, useEffect, useContext } from "react";
import '../app.css';
import { SettingsContext } from "../components/SettingsProvider.js";
import Sidebar from "../components/SideBar.js";
import MockUp from "../json_files/mock_up_output.json";
import "./SettingsPage.css";
import "../components/OverlayContent.css"
import Box from "../components/BasicOutputBox.js"
import BlackBox from "../components/BlackOutputBox.js"
import { useNavigate } from "react-router-dom";
import CellSignatureContainer from "../components/CellSignatureContainer.js";
import TestFileReader from "../components/TestFileReader.js";
import GlobalSignatureCell from "../components/GlobalSignatureCell.js";
import AlertCard from "../components/AlertCard.js";
import { Snackbar, Alert, Button } from "@mui/material";

export default function SettingsPage() {
  // Configuration settings
  const defaultOverlayConfig = {
    showTimeMetric: true,
    showStorageMetric: true,
    showBlackBox: true,
  };

  const [config, setConfig] = useState(defaultOverlayConfig);
  const [activeTab, setActiveTab] = useState('overlay');

  useEffect(() => {
    const storedConfig = localStorage.getItem('overlayConfig');
    if (storedConfig) {
      setConfig(JSON.parse(storedConfig));
    }
  }, []);

  const handleToggle = (e) => {
    const { name, type, checked } = e.target;
    setConfig((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : e.target.value,
    }));
  };

  const handleSave = () => {
    saveFinalValues();
    localStorage.setItem('overlayConfig', JSON.stringify(config));
    setAlertVisibleConfig(true)
  };

  // Handling code cells signatures
  const { codeCells } = useContext(SettingsContext)

  const listSignatureContainers = codeCells.map((_, index) => (
    <CellSignatureContainer index={index} />
  ))

  // Handling Input and Output field values for testing
  const { draftValues, setDraftValues, saveFinalValues } = useContext(SettingsContext)
  const handleChange = (e) => {
    const { name, value } = e.target;

    setDraftValues((prevValues) => {
      let newValues = { ...prevValues };

      if (name.includes(".")) {
        const keys = name.split(".");
        keys.reduce((acc, key, index) => {
          if (index === keys.length - 1) {
            acc[key] = value;
          } else {
            acc[key] = acc[key] || {};
          }
          return acc[key];
        }, newValues);
      } else if (name === "input") {
        newValues.raw_input = value;
      } else if (name === "output") {
        newValues.raw_output = value;
      } else if (name === "timeout") {
        if (/^\d*$/.test(value) && value != "" && value[0] != "0") {
          newValues.timeout = parseInt(value, 10)
        } else {
          newValues.timeout = ""
        }
      } else if (name === "test_cases_count") {
        if (/^\d*$/.test(value) && value != "" && value[0] != "0") {
          newValues.test_cases_count = parseInt(value, 10)
        } else {
          newValues.test_cases_count = ""
        }
      } else {
        newValues[name] = value;
      }
      return newValues;
    });
  };

  const parseArg = (arg) => {
    if (isString(arg)) {
        return "\"" + arg + "\"";
    }
    if (Array.isArray(arg)) {
      arg = arg.map(parseArg).join(", ");
      arg = "[" + arg + "]";
    }
    return String(arg);
  }

  const parseArguments = (input) => {
    input = "[" + input + "]";
    let json_input = JSON.parse(input);
    console.log("Object input: ", json_input);
    let output = json_input.map(parseArg);
    console.log("Parsed input: ", output);
    return output;
  };

  const parseField = (input) => {
    let rows = input.split("\n");
    let rows_parsed = rows.map((row) => parseArguments(row));
    let rows_filtered = rows_parsed.filter((row) => row.length > 0);
    return rows_filtered;
  }

  const isString = (value) => typeof value === 'string' || value instanceof String;

  const saveSignature = () => {
    draftValues.input = parseField(draftValues.raw_input);
    draftValues.output = parseField(draftValues.raw_output);
    saveFinalValues();
    setAlertVisibleCellSignature(true);
    // alert("Changes saved!", draftValues);
    // console.log(codeCells)
  }

  // handle test file imports
  const parseTestFile = (file) => {
    let inputSection = []
    let outputSection = []
    let currentSection = ""

    const lines = file.split("\n").map(line => line.trim())
    lines.forEach(line => {
      if (line.toLowerCase() === "input" || line.toLowerCase() === "output") {
        currentSection = line.toLowerCase()
      } else {
        const values = parseArguments(line)
        if (currentSection === "input") {
          inputSection.push(values)
        } else {
          outputSection.push(values)
        }
      }
    })

    return { input: inputSection, output: outputSection }

  }

  const handleFileChange = (e) => {
    const file = e.target.files[0];

    if (file) {
      const reader = new FileReader();
      reader.onload = () => {
        const content = reader.result;
        const parsedData = parseTestFile(content);

        setDraftValues(prevValues => ({
          ...prevValues,
          input: parsedData.input,
          output: parsedData.output
        }));

        saveFinalValues(prevValues => ({
          ...prevValues,
          input: parsedData.input,
          output: parsedData.output
        }))
      };
      reader.readAsText(file);
    }
  };

  // saving project
  const exportFullSession = () => {
    const sessionData = {};

    for (let i = 0; i < sessionStorage.length; i++) {
      const key = sessionStorage.key(i);

      if (
        key.startsWith("option-") ||
        key.startsWith("codecell-") ||
        key === "configOptions" ||
        key === "draftValues"
      ) {
        continue;
      }

      const value = sessionStorage.getItem(key);
      try {
        sessionData[key] = JSON.parse(value);
      } catch (e) {
        sessionData[key] = value;
      }
    }

    const blob = new Blob([JSON.stringify(sessionData, null, 2)], {
      type: "application/json"
    });

    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = "full_session.json";
    anchor.click();
    URL.revokeObjectURL(url);
  };


  // Navigation
  const navigate = useNavigate();
  const closeSettings = () => {
    navigate("/CodeCells");
  };

  const toCodePage = () => {
    navigate("/CodePage");
  };

  // Generate Test Cases
  const handleCheck = (e) => {
    const { checked } = e.target;
    setAlertManualTesting(checked)

    setDraftValues((prevValues) => ({
      ...prevValues,
      generate_test_cases: checked
    }));
  };

  // Render content for each tab 
  const renderTabContent = () => {
    switch (activeTab) {
      case 'overlay':
        return (
          <div className="tab-content-overlay">
            <div className="settingsContainer">
              <div className="category-container">
                <div className="title">
                  <span>Metric Settings</span>
                </div>
                <div className="full-width-line"></div>
                <div className="settings-container-col">
                  <div className="checkbox-setting-container">
                    <div className="subtitle">
                      <span>Execution Time</span>
                    </div>
                    <label className="checkbox-container">
                      <input
                        type="checkbox"
                        name="showTimeMetric"
                        checked={config.showTimeMetric}
                        onChange={handleToggle}
                      />
                      <span class="checkbox" />
                    </label>
                  </div>
                  <div className="checkbox-setting-container">
                    <div className="subtitle">
                      <span>Memory Usage</span>
                    </div>
                    <label className="checkbox-container">
                      <input
                        type="checkbox"
                        name="showStorageMetric"
                        checked={config.showStorageMetric}
                        onChange={handleToggle}
                      />
                      <span class="checkbox" />
                    </label>
                  </div>
                </div>
              </div>
              <div className="category-container">
                <div className="title">
                  <span>Terminal Settings</span>
                </div>
                <div className="full-width-line"></div>
                <div className="settings-container-col">
                  <div className="checkbox-setting-container">
                    <div className="subtitle">
                      <span>Show Terminal</span>
                    </div>
                    <label className="checkbox-container">
                      <input
                        type="checkbox"
                        name="showBlackBox"
                        checked={config.showBlackBox}
                        onChange={handleToggle}
                      />
                      <span class="checkbox" />
                    </label>
                  </div>
                </div>
              </div>
              <div className="category-container">
                <div className="title">
                  <span>System Settings</span>
                </div>
                <div className="full-width-line"></div>
                <div className="settings-container-col">
                  <div className="checkbox-setting-container">
                    <div className="subtitle">
                      <span>Timeout Period (seconds)</span>
                    </div>
                    <div className="inputField timeout">
                      <input
                        type="text"
                        name="timeout"
                        placeholder="60"
                        value={draftValues.timeout}
                        onChange={handleChange}
                      />
                    </div>
                  </div>
                </div>
              </div>
              <button className="settingsButton" onClick={handleSave}>
                <span> Save </span>
              </button>
            </div>
            <div className="outputContainer">
              <div className="overlay">
                <div className="overlay-background">
                  <div className="overlay-container">
                    <div class="rows-container">
                      {(config.showTimeMetric || config.showStorageMetric) && (<div className="output-row-first">
                        {config.showTimeMetric && (<Box title="Execution Time">{MockUp.defaultMetrics.executionTime}</Box>)}
                        {config.showStorageMetric && (<Box title="Memory Usage">{MockUp.defaultMetrics.memoryUsage}</Box>)}
                      </div>)}
                      {config.showBlackBox && (<div className="output-row">
                        <BlackBox>{MockUp.value}</BlackBox>
                      </div>)}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        );
      case 'signature':
        return (
          <div className="tab-content-overlay">
            <div className="settingsContainer">
              {/* Cell signatures container*/}
              <div className="category-container">
                <div className="settings-title">
                  <span>Function Signatures</span>
                </div>
                <div className="full-width-line"></div>
                <div className="SettingsFields">
                  <GlobalSignatureCell />
                  {listSignatureContainers}
                </div>
              </div>
              {/* Testing values container */}
              <div className="category-container">
                <div className="settings-title">
                  <span> Testing Values </span>
                </div>
                <div className="full-width-line"></div>
                <div className="testing-content">
                  <div className="test-container">
                    <div className="cell-subtitle" >
                      <span> Automatic Testing </span>
                    </div>
                    <div className="test-container-content">
                      <label className="checkbox-container">
                        <span> Generate Test Cases </span>
                        <input
                          type="checkbox"
                          name={`checkbox-generate-test-cases`}
                          checked={draftValues?.generate_test_cases || false}
                          onChange={handleCheck} />
                        <span class="checkbox" />
                      </label>
                      <div className="inputField">
                        <span>Number of Test Cases</span>
                        <div className="inputField timeout">
                          <input
                            type="text"
                            name="test_cases_count"
                            placeholder="25"
                            value={draftValues.test_cases_count}
                            onChange={handleChange}
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                  <div className={`test-container ${draftValues.generate_test_cases ? "isUnavailable" : ""}`}>
                    <div className="cell-subtitle" >
                      <span> Manual Testing </span>
                    </div>
                    <div className="test-container-content">
                      <div className="inputField testing">
                        <span> Input Values </span>
                        <textarea
                          name="input"
                        onChange={handleChange}
                        value={draftValues.raw_input}
                          rows={5}
                          cols={15}
                          placeholder={`1, 2 \n3, 6`}
                        />
                      </div>
                      <div className="inputField testing">
                        <span> Output Values </span>
                        <textarea
                          name="output"
                        value={draftValues.raw_output}
                          onChange={handleChange}
                          rows={5}
                          cols={15}
                          placeholder={`1, 2 \n3, 6`}
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div className="bottomButtons">
                <TestFileReader handleFileChange={handleFileChange} />
                <button onClick={saveSignature}>
                  <span> Save </span>
                </button>
              </div>
            </div>
          </div>
        );
      default:
        return 'overlay';
    }
  };

  // alerts
  const [alertVisibleConfig, setAlertVisibleConfig] = useState(false)
  const [alertVisibleCellSignature, setAlertVisibleCellSignature] = useState(false)
  const [alertManualTesting, setAlertManualTesting] = useState(draftValues?.generate_test_cases || false)
  const [warningMessage, setWarningMessage] = useState(false)

  const handleClose = (event, reason) => {
    if (reason === "clickaway") return;
    setAlertVisibleConfig(false);
    setAlertVisibleCellSignature(false);
    setAlertManualTesting(false);
    setWarningMessage(false)
  };

  return (
    <div className="big-container">
      {/* alerts */}
      <Snackbar
        open={warningMessage}
        autoHideDuration={6000}
        onClose={handleClose}
        anchorOrigin={{ vertical: "bottom", horizontal: "right" }}
      >
        <Alert
          severity="warning"
          sx={{
            width: "100%",
            "& .MuiButton-root": {
              all: "unset",
              fontFamily: "Roboto, sans-serif",
              padding: "6px 16px",
              borderRadius: "4px",
              cursor: "pointer",
              transition: "background-color 0.3s ease, box-shadow 0.2s ease",
              userSelect: "none",
              fontSize: "0.875rem",
              fontWeight: 500,
              textTransform: "uppercase",
              backgroundColor: "#e0ccbc", // darker beige
              color: "#2c2c2c",
              textAlign: "center",

              "&:hover": {
                backgroundColor: "#d5c0b1",
              },
              "&:active": {
                backgroundColor: "#c8b3a4",
                boxShadow: "inset 0 3px 5px rgba(0,0,0,0.2)",
              },

              "&.outlined": {
                backgroundColor: "transparent",
                color: "#8d6e5c",
                border: "1px solid #8d6e5c",
                "&:hover": {
                  backgroundColor: "rgba(141, 110, 92, 0.08)",
                },
                "&:active": {
                  backgroundColor: "rgba(141, 110, 92, 0.15)",
                  boxShadow: "inset 0 2px 4px rgba(0,0,0,0.15)",
                },
              },
            },
          }}
          onClose={handleClose}
          action={
            <>
              <Button color="inherit" size="small" onClick={() => {
                exportFullSession();
                setWarningMessage(false);
              }}>
                Save
              </Button>
              <Button color="inherit" size="small" onClick={() => {
                console.log("Closed without saving");
                setWarningMessage(false);
                sessionStorage.clear()
                navigate("/")
              }}>
                Close Anyway
              </Button>
            </>
          }
        >
          Make sure you save before closing the project!
        </Alert>
      </Snackbar>
      <AlertCard open={alertVisibleConfig} handleClose={handleClose} severity="success" message="Overlay configuration saved successfully!" />
      <AlertCard open={alertVisibleCellSignature} handleClose={handleClose} severity="success" message="Changes saved!" />
      <AlertCard open={alertManualTesting} handleClose={handleClose} severity="info" message="Manual testing is no longer available!" />

      <Sidebar
        runCodeCells={toCodePage}
        pressSettings={toCodePage}
        pressLogo={() => setWarningMessage(true)}
      />
      <div className="tab-container">
        <div className="tab-menu">
          <button
            onClick={() => setActiveTab('overlay')}
            className={activeTab === 'overlay' ? 'active' : ''}
          >
            Overlay
          </button>
          <button
            onClick={() => setActiveTab('signature')}
            className={activeTab === 'signature' ? 'active' : ''}
          >
            Signature
          </button>
        </div>
        {renderTabContent()}
      </div>

    </div>

  );
}
