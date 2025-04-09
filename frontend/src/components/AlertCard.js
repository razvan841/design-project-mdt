import { Snackbar, Alert } from "@mui/material";

export default function AlertCard(props) {
    return (
        <Snackbar open={props.open} autoHideDuration={3000} onClose={props.handleClose} anchorOrigin={{ vertical: "bottom", horizontal: "right" }}>
            <Alert severity={props.severity} sx={{ width: "100%" }}>
                {props.message}
            </Alert>
        </Snackbar>
    );
}