import "./DiffResults.css"
import "../app.css"
import Close from "../assets/CloseTab.svg"
import Passed from "../assets/Check.svg"
import NotPassed from "../assets/NotPassed.svg"
import TestNo from "../assets/NumberIcon.svg"
import DRCard from "./DRCard"

// differential results overlay component 
export default function DiffResults(props) {
    const displayFailedTests = props.failed_tests.map((test, _) => (
        <DRCard title={`Input: ${test.input}`} 
        failed_cells={Object.values(
            Object.fromEntries(
                Object.entries(test.cells).filter(([key, _]) => key !== "expected_output")
            )
        )} 
        expected_output={test.cells.expected_output?.value} />
    ));

    return (
        <div className="DR-MainContainer">
            <div className="DR-Box">
                <div className="DR-Title" onClick={props.closeDiff}>
                    <span> Differential Results </span>
                    <img src={Close} />
                </div>
                <div className="DR-Content">
                    <div className="DR-Row">
                        <div className="DR-Icon">
                            <img src={TestNo} />
                        </div>
                        <span> Number of tests: {props.total_tests}</span>
                    </div>
                    <div className="DR-Row">
                        <div className="DR-Icon">
                            <img src={Passed} />
                        </div>
                        <span> Matched tests: {props.matched_tests}</span>
                    </div>
                    <div className="DR-Row failed">
                        <div className="DR-Icon">
                            <img src={NotPassed} />
                        </div>
                        <span> Failed tests: {props.unmatched_tests} </span>
                    </div>
                    <div className="DR-FailedContainer">
                        {displayFailedTests}
                    </div>
                </div>
            </div>
        </div>
    );
}