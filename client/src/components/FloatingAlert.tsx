import React from 'react';
import { Alert, Snackbar } from "@mui/material";


export type FloatingAlertProps = {
    isShown: boolean;
    setShown: (value: boolean) => void;
    text: string;
    type?: 'error' | 'info' | 'warning'
}

export const FloatingAlert = ({ isShown, text, type = 'error', setShown }: FloatingAlertProps) => {
    return <Snackbar
        open={isShown}
        autoHideDuration={6000}
        onClose={() => setShown(false)}
    >
        <Alert
            onClose={() => setShown(false)}
            severity={type}
            sx={{ width: "100%" }}
        >
            {text}
        </Alert>
    </Snackbar>
}