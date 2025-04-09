import "../pages/CodePage.css"
import { useState, useContext } from "react";
import DropdownButton from "./DropdownButton.js";
import HeaderRow from "./HeaderRow.js";
import { SettingsContext } from "./SettingsProvider.js";
import Button from "./ConfirmButton.js";
import CodeFileReader from "./CodeFileReader.js";

export default function HeaderCell(props) {
    // close and open dropdown menu
    // const [open, setOpen] = useState(false)
    const open = props.headerOpen
    const setOpen = props.setHeaderOpen

    const toggle = () => {
        setOpen(!open)
    }

    const { configOptions, codeCells, setCodeCells, setDraftValues, saveFinalValues } = useContext(SettingsContext)

    // handle cell removal 
    const resetIndexes = (data, id) => {
        let filteredEntries = Object.entries(data)
            .filter(([key]) => key !== "expected_output" && key !== "differential" && key !== String(id));
    
        const updatedData = Object.fromEntries(
            filteredEntries.map(([key, value], newIndex) => [String(newIndex), value])
        );
    
        return updatedData;
    };

    const removeCodeCell = (id) => {
        sessionStorage.removeItem(`codecell-${id}`);
        sessionStorage.removeItem(`option-Language-${id}`);
        sessionStorage.removeItem(`option-Version-${id}`);
        sessionStorage.removeItem(`option-Compiler-${id}`);


        setCodeCells((prevValues) => {
            const newCells = prevValues.filter((_, index) => index !== id);
            sessionStorage.setItem("codeCells", JSON.stringify(newCells));

            // Clear session storage to avoid outdated keys
            for (let i = 0; i < prevValues.length; i++) {
                sessionStorage.removeItem(`codecell-${i}`);
                sessionStorage.removeItem(`option-Language-${i}`);
                sessionStorage.removeItem(`option-Version-${i}`);
                sessionStorage.removeItem(`option-Compiler-${i}`);
            }

            // Update session storage with new keys
            newCells.forEach((cell, i) => {
                sessionStorage.setItem(`codecell-${i}`, cell.codeText || []);
                sessionStorage.setItem(`option-Language-${i}`, cell.language || []);
                sessionStorage.setItem(`option-Version-${i}`, cell.version || []);
                sessionStorage.setItem(`option-Compiler-${i}`, cell.compiler || []);
            });

            return newCells;
        })

        setDraftValues((prevValues) => {
            const newValues = {
                ...prevValues,
                cells: prevValues.cells.filter((_, index) => index !== id)
            }
            sessionStorage.setItem("draftValues", JSON.stringify(newValues))
            return newValues;
        })

        saveFinalValues((prevValues) => {
            const newValues = {
                ...prevValues,
                cells: prevValues.cells.filter((_, index) => index !== id)
            }
            sessionStorage.setItem("finalValues", JSON.stringify(newValues))
            return newValues;
        })

        // handle index changes in data_response
        if (props.data) {
            const updatedData = resetIndexes(props.data, id);
            sessionStorage.setItem("data_response", JSON.stringify(updatedData));        }

        window.location.reload();
    };

    // handle file upload 
    const handleFileChange = (e) => {
        const file = e.target.files[0]
        const fileName = file.name
        let fileExtension = fileName.split(".").pop()

        if (fileExtension === "js") {
            fileExtension = "javascript"
        }

        if (fileExtension === "py") {
            fileExtension = "python"
        }

        if (file) {
            const reader = new FileReader()
            reader.onload = () => {
                const content = reader.result
                sessionStorage.setItem(`codecell-${props.id}`, content)
                sessionStorage.setItem(`option-Language-${props.id}`, fileExtension)

                setCodeCells((prevCells) => {
                    const updatedCells = [...prevCells];
                    updatedCells[props.id] = { ...updatedCells[props.id], codeText: content, language: fileExtension};
                    return updatedCells;
                })
                window.location.reload()
            }
            reader.readAsText(file)
        }


    }

    return (
        <div className="headerCodeCell">
            {/* header title  */}
            <div className="header" onClick={toggle}>
                <div className="title headerText"> Configuration - Cell {props.id} </div>
                <div className={`toggle ${open ? "isOpen" : ""}`}>
                    <DropdownButton dropdownToggle={toggle} />
                </div>
            </div>
            {/* header content - language, version, compiler */}
            <div className={`headerContent ${open ? "isOpen" : ""}`}>
                <HeaderRow id={props.id} title={"Language"} options={Object.keys(configOptions)} setOption={props.setLanguage} />
                <div className={`extraContent ${codeCells[props.id].language ? "isOpen" : ""}`}>
                    <HeaderRow id={props.id} title={"Version"} options={configOptions[codeCells[props.id].language]?.versions || []} setOption={props.setVersion} />
                    <HeaderRow id={props.id} title={"Compiler"} options={configOptions[codeCells[props.id].language]?.compilers || []} setOption={props.setCompiler} />
                </div>
                <div className="headerBottomButtons">
                    <CodeFileReader handleFileChange={handleFileChange} />
                    {codeCells.length > 2 &&
                        <button className="deleteButton" onClick={() => { removeCodeCell(props.id) }}>
                            <span> Delete
                            </span>
                        </button>}
                </div>
            </div>
        </div>
    );
}