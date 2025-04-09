import "../pages/SettingsPage.css"
import { useContext } from "react";
import InputField from "./InputField";
import { SettingsContext } from "./SettingsProvider";

// global signature container for args and return 
export default function CellSignatureContainer() {
    const { setDraftValues } = useContext(SettingsContext)

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

    return (
        <div className="cell-signature-container">
            <span className="cell-subtitle">Global</span>
            <div className="inputFields">
                <InputField fieldName={"Args"} valueName={"args"} placeholder={"int, int, float"} index={0} handleChange={handleChange} />
                <InputField fieldName={"Return"} valueName={"return"} placeholder={"int"} index={0} handleChange={handleChange} />
            </div>
        </div>
    );
}