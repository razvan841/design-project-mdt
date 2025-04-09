import "./CodePage.css";
import "../app.css";
import { useContext, useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import CodeCell from "../components/CodeCell.js";
import SideBar from "../components/SideBar.js";
import { saveAs } from "file-saver";
import { SettingsContext } from "../components/SettingsProvider.js";
import DiffResults from "../components/DiffResults.js";
import FileReaderComponent from "../components/CodeFileReader.js";
import { Snackbar, Alert, Button, keyframes } from "@mui/material";
import AlertCard from "../components/AlertCard.js";

export default function CodePage() {
	// data response from backend
	const [data, setData] = useState(
		JSON.parse(sessionStorage.getItem("data_response")) || null
	);

	// diff results open
	const [diffOpen, setDiffOpen] = useState(false);

	// code cells
	// set the two initial code cells that the user will have at the start
	const { codeCells, setCodeCells } = useContext(SettingsContext);
	const [loading, setLoading] = useState(false);
	const [status, setStatus] = useState(0);

	// handle change in any code cell based on cell id
	const handleCodeChange = (id, key, value) => {
		setCodeCells((prev) => {
			const updatedCells = [...prev];
			updatedCells[id] = { ...updatedCells[id], [key]: value };
			return updatedCells;
		});
	};

	// render the list of code cells
	const listCells = codeCells.map((_, index) => (
		<CodeCell
			className="code-cell"
			data={data}
			isLoading={loading}
			status={status}
			id={index}
			setCodeText={(code) => handleCodeChange(index, "codeText", code)}
			setLanguage={(language) =>
				handleCodeChange(index, "language", language)
			}
			setVersion={(version) =>
				handleCodeChange(index, "version", version)
			}
			setCompiler={(compiler) =>
				handleCodeChange(index, "compiler", compiler)
			}
		/>
	));

	// get final values entered in the settings page
	const { finalValues, saveFinalValues, setDraftValues } =
		useContext(SettingsContext);

	// create configuartion file to send to backend
	const createOptions = () => {
		if (!finalValues || !finalValues.cells) {
			return []; // Prevents undefined errors
		}

		return codeCells
			.map((cell, index) => {
				if (!finalValues.cells[index]) {
					return null; // Skip if finalValues.cells[index] is undefined
				}

				return {
					cell_id: index,
					code: cell.codeText,
					signature: {
						name: finalValues.cells[index].name || "",
						args: finalValues.cells[0].args || "",
						return: finalValues.cells[0].return || "",
					},
					language: cell.language || "",
					version: cell.version || "",
					compiler: cell.compiler || "",
					specs: finalValues.cells[index].specs || "",
					run_as_is: finalValues.cells[index].run_as_is || false,
				};
			})
			.filter(Boolean); // Removes any `null` values
	};

	const configFile = {
		message: {
			options: createOptions(),
			input: finalValues.input,
			output: finalValues.output,
			timeout: finalValues.timeout ? finalValues.timeout : 60,
			generate_test_cases: finalValues.generate_test_cases,
			test_cases_signature: finalValues.cells[0].args,
			test_cases_count: finalValues.test_cases_count
				? finalValues.test_cases_count
				: 25,
		},
	};

	// button functionalities
	const saveJSON = () => {
		const document = JSON.stringify(configFile, null, 2);
		const blob = new Blob([document], {
			type: "application/json",
		});
		saveAs(blob, "../testfiles/testJSON.json");
	};

	const JSONblob = new Blob([JSON.stringify(configFile, null, 2)], {
		type: "application/json",
	});

	const runCode = () => {
    setLoading(true);
    fetch("http://localhost:5000/api/v1/execute_code", {
      method: "POST",
      body: JSONblob,
      headers: {
        "Content-type": "application/json",
      },
    })
      .then(async (response) => {
        setLoading(false);
        const body = await response.json(); 
  
        if (!response.ok) {
          // Show backend error message if available
          const errorMessage = body?.message.error_message || 'Unknown error';
          setAlertError(true);
          setAlertMessage(errorMessage);
          throw new Error(`HTTP ${response.status}: ${errorMessage}`);
        }
  
        // Success case
        setData(body);
        sessionStorage.setItem("data_response", JSON.stringify(body));
        console.log("Response:", body);
      })
      .catch((error) => {
        setAlertError(true);
        setAlertMessage(error.message);
        console.log("error", error);
        console.error("Error fetching data:", error);
      });
  };

	const fetchStatus = () => {
		fetch("http://localhost:5000/api/v1/status_execution", {
			method: "GET",
			headers: {
				"Content-Type": "application/json",
			},
		})
			.then((response) => {
				if (!response.ok) {
					setAlertError(true);
					alert(`HTTP error! Status: ${response.status}`);
          setLoading(false);
					throw new Error(`HTTP error! Status: ${response.status}`);
				}
				return response.json();
			})
			.then((jsonData) => {
				setStatus(jsonData.status);
				console.log("Fetched status:", jsonData.status);
			})
			.catch((error) => {
        setLoading(false);
				console.error("Error fetching status:", error);
			});
	};

	useEffect(() => {
		let intervalId;
		if (loading) {
			// Optionally call fetchStatus() immediately, then at an interval.
			fetchStatus();
			intervalId = setInterval(fetchStatus, 200);
		}
		return () => {
			if (intervalId) clearInterval(intervalId);
		};
	}, [loading]);

	const addCodeCell = () => {
		setCodeCells((prevCells) => {
			const newCells = [
				...prevCells,
				{
					id: prevCells.length.toString(),
					codeText: "",
					language: "",
					version: "",
					compiler: "",
				},
			];
			sessionStorage.setItem("codeCells", JSON.stringify(newCells));
			return newCells;
		});

		setDraftValues((prevValues) => {
			const newValues = {
				...prevValues,
				cells: prevValues.cells
					? [
							...prevValues.cells,
							{
								name: "",
								args: "",
								return: "",
								specs: "",
								run_as_is: false,
							},
					  ]
					: [
							{
								name: "",
								args: "",
								return: "",
								specs: "",
								run_as_is: false,
							},
					  ],
			};
			sessionStorage.setItem("draftValues", JSON.stringify(newValues));
			return newValues;
		});

		saveFinalValues((prevValues) => {
			const newValues = {
				...prevValues,
				cells: prevValues.cells
					? [
							...prevValues.cells,
							{
								name: "",
								args: "",
								return: "",
								specs: "",
								run_as_is: false,
							},
					  ]
					: [
							{
								name: "",
								args: "",
								return: "",
								specs: "",
								run_as_is: false,
							},
					  ],
			};
			sessionStorage.setItem("finalValues", JSON.stringify(newValues));
			return newValues;
		});

		setAlertAddCodeCell(true);
	};

	// navigation
	const navigate = useNavigate();

	const openSettings = () => {
		navigate("/Settings");
	};

	// locally save
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
			type: "application/json",
		});

		const url = URL.createObjectURL(blob);
		const anchor = document.createElement("a");
		anchor.href = url;
		anchor.download = "full_session.json";
		anchor.click();
		URL.revokeObjectURL(url);

		setAlertSaveProject(true);
	};

	const inputRef = useRef(null);

	const handleImportClick = () => {
		inputRef.current.click();
	};

	const importFullSession = (event) => {
		const file = event.target.files?.[0];
		if (!file) return;

		const reader = new FileReader();
		reader.onload = (e) => {
			try {
				const sessionData = JSON.parse(e.target.result);
				sessionStorage.clear();
				for (const [key, value] of Object.entries(sessionData)) {
					sessionStorage.setItem(key, value);

                    if (key === "data_response") {
                        console.log(value);
                        sessionStorage.setItem(key, JSON.stringify(value));
                    }

					if (key === "finalValues") {
						sessionStorage.setItem(
							"finalValues",
							JSON.stringify(value)
						);
						sessionStorage.setItem(
							"draftValues",
							JSON.stringify(value)
						);
					}

					if (key === "codeCells") {
						sessionStorage.setItem(
							"codeCells",
							JSON.stringify(value)
						);

						for (let i = 0; i < value.length; i++) {
							const cell = value[i];
							sessionStorage.setItem(
								`codecell-${i}`,
								cell.codeText
							);
							sessionStorage.setItem(
								`option-Language-${i}`,
								cell.language
							);
							sessionStorage.setItem(
								`option-Version-${i}`,
								cell.version
							);
							sessionStorage.setItem(
								`option-Compiler-${i}`,
								cell.compiler
							);
						}
					}
				}
				window.location.reload(); // Optional
			} catch (err) {
				setAlertFailedImportProject(true);
				console.error("Failed to load full session:", err);
			}
		};
		reader.readAsText(file);

		setAlertImportProject(true);
	};

  // alerts
  const [alertAddCodeCell, setAlertAddCodeCell] = useState(false)
  const [alertSaveProject, setAlertSaveProject] = useState(false)
  const [alertImportProject, setAlertImportProject] = useState(false)
  const [alertFailedImportProject, setAlertFailedImportProject] = useState(false)
  const [alertError, setAlertError] = useState(false)
  const [alertMessage, setAlertMessage] = useState("404 - NOT FOUND")
  const [warningMessage, setWarningMessage] = useState(false)


  const handleClose = (event, reason) => {
    if (reason === "clickaway") return;
    setAlertAddCodeCell(false)
    setAlertSaveProject(false)
    setAlertImportProject(false)
    setAlertFailedImportProject(false)
    setAlertError(false)
    setWarningMessage(false)
  };

  return (
    <div className="big-container" >
      {/* alerts */}
      {/* alert for warning when you want to go back */}
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
      <AlertCard open={alertFailedImportProject} handleClose={handleClose} severity="error" message="Failed to import project!" />
      <AlertCard open={alertAddCodeCell} handleClose={handleClose} severity="success" message="Code cell added successfully!" />
      <AlertCard open={alertError} handleClose={handleClose} severity="error" message={alertMessage} />

      <SideBar
        runCodeCells={runCode}
        pressSettings={openSettings}
        addCodeCell={addCodeCell}
        setDiff={() => setDiffOpen(!diffOpen)}
        data={data}
        pressSave={exportFullSession}
        pressImport={importFullSession}
        inputRef={inputRef}
        handleImportClick={handleImportClick}
        pressLogo={() => setWarningMessage(true)}
      />
      <div className={`cells-container ${diffOpen ? "diffIsOpen" : ""}`}>
        {listCells}
        {data?.differential && diffOpen && <DiffResults
          total_tests={data.differential.test_count}
          matched_tests={data.differential.matched}
          unmatched_tests={data.differential.no_match}
          failed_tests={data.differential.failed}
          closeDiff={() => setDiffOpen(!diffOpen)}
        />}
      </div>
    </div >
  );
}
