import React from 'react';
import { Alert, Snackbar } from "@mui/material";


export type FloatingAlertProps = {
    isShown: boolean;
    setShown: (value: boolean) => void;
    positionVertical: 'bottom' | 'top';
    positionHorizontal: 'left' | 'center' | 'right';
    text: string;
    type?: 'error' | 'info' | 'warning'
}

export const FloatingAlert = ({ isShown, text, type = 'error', setShown, positionVertical = 'bottom', positionHorizontal = 'left' }: FloatingAlertProps) => {
    return <Snackbar
        open={isShown}
        autoHideDuration={6000}
        onClose={() => setShown(false)}
        anchorOrigin={{ vertical: positionVertical, horizontal: positionHorizontal }}
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