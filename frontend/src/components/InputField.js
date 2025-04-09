import { useContext } from "react"
import { SettingsContext } from "./SettingsProvider"
import "../pages/SettingsPage.css"

// input field for cell signature!!
export default function InputField({fieldName, valueName, placeholder, index, handleChange}) {
    const {draftValues} = useContext(SettingsContext)

    const value = (valueName === "args" || valueName === "specs")
        ? Array.isArray(draftValues.cells[index][valueName]) 
        ? draftValues.cells[index][valueName].join(", ") 
        : ""
        : draftValues.cells[index][valueName];

    return (
        <div className="inputField">
        <span> {fieldName} </span>
            <input
                type="text"
                name= {`cells.${index}.${valueName}`}
                value={value}
                onChange= {handleChange}
                placeholder= {placeholder}
            />
        </div>
    );
}
