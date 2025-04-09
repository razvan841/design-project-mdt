import "./DiffResults.css"

// row that shows the value of each cell and potential errors 
export default function CardRow(props) {
    return (
        <div className="Card-Row">
            <span> Cell {props.id}: {props.value} </span>
            {props.error && <span> ERROR: {props.error}</span>}
        </div>
    );
}