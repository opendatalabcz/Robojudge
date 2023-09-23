import React from 'react';
import { CircularProgress, Typography } from "@mui/material";

const styles = {
    loadingOverlay: {
        position: "absolute",
        display: "flex",
        justifyContent: "center",
        flexDirection: "column",
        alignItems: "center",
        width: "100%",
        height: "100%",
        zIndex: 1,
    } as React.CSSProperties
};

export const LoadingOverlay = () => {
    return <div style={styles.loadingOverlay}>
        <CircularProgress />
        <Typography variant="body2" color="text.secondary">
            Hledám rozhodnutí a připravuji shrnutí...
        </Typography>
    </div >
}