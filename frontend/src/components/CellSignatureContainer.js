import "../pages/SettingsPage.css"
import { useContext } from "react";
import InputField from "./InputField";
import { SettingsContext } from "./SettingsProvider";

// container for each cell's signature 
export default function CellSignatureContainer(props) {
    const { draftValues, setDraftValues } = useContext(SettingsContext)

    // handle user input 
    const handleChange = (e) => {
        const { name, value } = e.target;

        setDraftValues((prevValues) => {
            let newValues = { ...prevValues };

            if (name.includes(".")) {
                const keys = name.split(".");
                keys.reduce((acc, key, index) => {
                    if (index === keys.length - 1) {
                        if (key === "args" || key === "specs") {
                            acc[key] = value
                                .split(",")
                                .map((item) => item.trim());
                        } else {
                            acc[key] = value;
                        }
                    } else {
                        acc[key] = acc[key] || {};
                    }
                    return acc[key];
                }, newValues);
            } else {
                newValues[name] = value;
            }

            return newValues;
        });
    };

    const handleCheck = (e) => {
        const { checked } = e.target;

        setDraftValues((prevValues) => {

            let newValues = {
                ...prevValues,
                cells: prevValues.cells ? [...prevValues.cells] : [],
            };

            newValues.cells[props.index].run_as_is = checked;

            return newValues;
        });
    };



    return (
        <div className="cell-signature-container">
            <span className="cell-subtitle">Cell {props.index}</span>
            <label className="checkbox-container">
                <span> Run code as is </span>
                <input
                    type="checkbox"
                    name={`checkbox-cell-${props.index}`}
                    checked={draftValues.cells[props.index]?.run_as_is || false}
                    onChange={handleCheck} />
                <span class="checkbox" />
            </label>
            <div className="inputFields">
                <InputField fieldName={"Specs"} valueName={"specs"} placeholder={"numpy, pandas"} index={props.index} handleChange={handleChange} />
                {draftValues.cells[props.index].run_as_is === false ?
                    <>
                        <InputField fieldName={"Name"} valueName={"name"} placeholder={"sumNumber"} index={props.index} handleChange={handleChange} />
                    </>
                    :
                    <>
                    </>
                }
            </div>
        </div>
    );
}