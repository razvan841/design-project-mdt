import CardRow from "./CardRow";
import "./DiffResults.css"

// content of differential results card 
export default function DRCard(props) {
    const listCards = props.failed_cells.map((cell, index) => (
        <CardRow id={index} value={cell.value} error={cell.error_msg}/>
    ));

    return (
        <div className="DR-Card">
            <div className="Card-Title">
                <span> {props.title} </span>
            </div>
            {props.expected_output &&
                <div className="Card-Title">
                    <span> Expected Output: {props.expected_output} </span>
                </div>
            }
            <div className="Card-Content">
                {listCards}
            </div>
        </div>
    );
}