import { createContext, useEffect, useState, version } from "react";

export const SettingsContext = createContext();

const SettingsProvider = ({ children }) => {
    const [draftValues, setDraftValues] = useState(JSON.parse(sessionStorage.getItem("draftValues")) ||
    {
        cells:
            [
                { name: "", args: "", return: "", specs: "", run_as_is: false },
                { name: "", args: "", return: "", specs: "", run_as_is: false }
            ],
        input: "",
        output: "",
        raw_input: "",
        raw_output: "",
        timeout: "",
        generate_test_cases: false, 
        test_cases_signature: "",
        test_cases_count: ""
    });

    const [finalValues, setFinalValues] = useState(JSON.parse(sessionStorage.getItem("finalValues")) ||
    {
        cells:
            [
                { name: "", args: "", return: "", specs: "", run_as_is: false },
                { name: "", args: "", return: "", specs: "", run_as_is: false }
            ],
        input: "",
        output: "",
        raw_input: "",
        raw_output: "",
        timeout: "",
        generate_test_cases: false, 
        test_cases_signature: "",
        test_cases_count: ""
    });

    const initialCodeCells = [
        {
            codeText: sessionStorage.getItem("codecell-0") || "",
            language: sessionStorage.getItem("option-Language-0") || "",
            version: sessionStorage.getItem("option-Version-0") || "",
            compiler: sessionStorage.getItem("option-Compiler-0") || ""
        },
        {
            codeText: sessionStorage.getItem("codecell-1") || "",
            language: sessionStorage.getItem("option-Language-1") || "",
            version: sessionStorage.getItem("option-Version-1") || "",
            compiler: sessionStorage.getItem("option-Compiler-1") || ""
        }
    ]

    const [codeCells, setCodeCells] = useState(JSON.parse(sessionStorage.getItem("codeCells")) || initialCodeCells)

    useEffect(() => {
        sessionStorage.setItem("draftValues", JSON.stringify(draftValues));
    }, [draftValues]);

    useEffect(() => {
        sessionStorage.setItem("codeCells", JSON.stringify(codeCells))
    }, [codeCells]);

    const saveFinalValues = () => {
        setFinalValues(draftValues);
        sessionStorage.setItem("finalValues", JSON.stringify(draftValues))
    }

    const defaultJSON = {
        "cpp": {
            // default gcc compiler
            "compilers": ["gcc", "clang"],
            "versions": []
        },
        "java": {
            // default version 21 compiler amazoncorretto
            "compilers": ["amazoncorretto", "temurin"],
            "versions": ["21", "19", "17"]
        },
        "python": {
            // default version3.10
            "compilers": [],
            "versions": ["2.7", "3.5", "3.6", "3.7", "3.8", "3.9", "3.10", "3.11", "3.12"]
        },
        "javascript": {
            // default version node:19
            "compilers": [],
            "versions": ["node:current", "node:19", "node:18", "node:16", "node:14", "node:12"]
        },
        "php": {
            // default version php:8.3
            "compilers": [],
            "versions": ["php:8.3", "php:7.4", "php:5.6"]
        }
    };
    


    const [configOptions, setConfigOptions] = useState(JSON.parse(sessionStorage.getItem("configOptions")) || defaultJSON)

    const getConfigurations = () => {
        fetch("http://localhost:5000/api/v1/versions_compilers?language=all")
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`)
                }
                return response.json();
            })
            .then(data => {
                sessionStorage.setItem("configOptions", JSON.stringify(data))
                console.log("Response", JSON.stringify(data))
            })
            .catch(error => console.error("Error fetching data: ", error))
    }

    useEffect(() => {
        const options = getConfigurations()
        if (options !== undefined) {
            sessionStorage.setItem("configOptions", JSON.stringify(options))
        } else {
            sessionStorage.setItem("configOptions", JSON.stringify(defaultJSON))
        }
    }, [configOptions]);

    return (
        <SettingsContext.Provider value={{ draftValues, setDraftValues, finalValues, saveFinalValues, codeCells, setCodeCells, configOptions }}>
            {children}
        </SettingsContext.Provider>
    );
}

export default SettingsProvider;

