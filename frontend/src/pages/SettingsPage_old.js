import { useContext } from "react";
import { SettingsContext } from "../components/SettingsProvider.js"
import Sidebar from "../components/SideBar.js";
import MockUp from "../json_files/mock_up_output.json"
import Output from "../components/OverlayContent.js"
import "./SettingsPage.css"
import { useNavigate } from "react-router-dom"

export default function SettingsPage() {
    const {draftValues, setDraftValues, saveFinalValues} = useContext(SettingsContext)

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
                newValues.input = value
                    .split("\n") 
                    .map(row => row.split(",").map(num => num.trim())); 
            } else {
                newValues[name] = value;
            }
    
            return newValues;
        });
    };

    const navigate = useNavigate();

    const closeSettings = () => {
        navigate("/CodeCells")
    }

    return (
        <div className="mainSPContainer">
            <Sidebar runCodeCells={() => alert("Go to main page!")} pressSettings={closeSettings}/>
            <div className="contentContainer">
            <div className="settingsContainer">
                <div className="functionSignatureContainer">
                    <div className="settingsTitle">
                        <span> Function Signatures</span>
                    </div>
                    <div className="SettingsFields">
                    <div className="settingsSubTitle">
                        <span> Cell 1 </span>
                        <div className="inputFields"> 
                        <div className="inputField">
                            <span > Name </span>
                            <input
                                type="text"
                                name= "cell1.name" // name field of cell1
                                value= {draftValues.cell1.name}
                                onChange= {handleChange}
                            />
                        </div>
                        <div className="inputField">
                            <span > Arg 1 </span>
                                <input
                                    type="text"
                                    name= "cell1.arg1.name" // name field of cell1
                                    value= {draftValues.cell1.arg1.name}
                                    onChange= {handleChange}
                                />
                                <input
                                    type="text"
                                    name= "cell1.arg1.type" // name field of cell1
                                    value= {draftValues.cell1.arg1.type}
                                    onChange= {handleChange}
                                />
                        </div>
                        <div className="inputField">
                        <span > Arg 2 </span>
                            <input
                                type="text"
                                name= "cell1.arg2.name" // name field of cell1
                                value= {draftValues.cell1.arg2.name}
                                onChange= {handleChange}
                            />
                            <input                                    
                                type="text"
                                name= "cell1.arg2.type" // name field of cell1
                                value= {draftValues.cell1.arg2.type}
                                onChange= {handleChange}
                            />
                        </div>
                        <div className="inputField">
                        <span > Return </span>
                            <input
                                type="text"
                                name= "cell1.return" // name field of cell1
                                value= {draftValues.cell1.return}
                                onChange= {handleChange}
                            />
                        </div>
                    </div>
                    </div>
                    <div className="settingsSubTitle">
                        <span> Cell 2 </span>
                        <div className="inputFields"> 
                        <div className="inputField">
                            <span > Name </span>
                            <input
                                type="text"
                                name= "cell2.name" // name field of cell1
                                value= {draftValues.cell2.name}
                                onChange= {handleChange}
                            />
                        </div>
                        <div className="inputField">
                            <span > Arg 1 </span>
                                <input
                                    type="text"
                                    name= "cell2.arg1.name" // name field of cell1
                                    value= {draftValues.cell2.arg1.name}
                                    onChange= {handleChange}
                                />
                                <input
                                    type="text"
                                    name= "cell2.arg1.type" // name field of cell1
                                    value= {draftValues.cell2.arg1.type}
                                    onChange= {handleChange}
                                />
                        </div>
                        <div className="inputField">
                        <span > Arg 2 </span>
                            <input
                                type="text"
                                name= "cell2.arg2.name" // name field of cell1
                                value= {draftValues.cell2.arg2.name}
                                onChange= {handleChange}
                            />
                            <input                                    
                                type="text"
                                name= "cell2.arg2.type" // name field of cell1
                                value= {draftValues.cell2.arg2.type}
                                onChange= {handleChange}
                            />
                        </div>
                        <div className="inputField">
                        <span > Return </span>
                            <input
                                type="text"
                                name= "cell2.return" // name field of cell1
                                value= {draftValues.cell2.return}
                                onChange= {handleChange}
                            />
                        </div>
                    </div>
                    </div>
                    </div>
                    <div className="settingsTitle">
                        <span> Testing Values</span>
                        <div className="SettingsFieldsTesting">
                            <div className="settingsSubTitle input">
                                <span> Input Values </span>
                                <textarea
                                    name="input"
                                    value={Array.isArray(draftValues.input) 
                                        ? draftValues.input.map(row => row.join(",")).join("\n") 
                                        : ""} // Convert input array back to string for textarea
                                    onChange={handleChange}
                                    rows={1} 
                                />

                            </div>
                            <div className="settingsSubTitle">
                                <span> Output Values </span>
                                <input
                                type="text"
                                name= "output" // name field of cell1
                                value= {draftValues.output}
                                onChange= {handleChange}
                            />
                            </div>
                        </div>
                    </div>
                    <div className="settingsButton" onClick={() => {saveFinalValues(); alert("Changes saved!", draftValues)}}> 
                    <span> Save </span>
                </div>
                </div>
                <div className="metricsContainer"></div>
            </div>
            <div className="outputContainer">
                <div className="overlay">
                    <div className="overlay-background">
                        <div className="overlay-container">
                            <Output data={MockUp}/>
                        </div>
                    </div>
                </div>
            </div>
            </div>
        </div>
    );
}