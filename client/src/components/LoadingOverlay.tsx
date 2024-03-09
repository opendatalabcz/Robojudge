import React from 'react';
import { CircularProgress, Typography } from "@mui/material";

const styles = {
    loadingOverlay: {
        position: "fixed",
        width: "100%",
        height: "100%",
        zIndex: 1,
    },
    overlayInfo: {
        marginTop: '50vh',
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
    },
} as Record<string, React.CSSProperties>;

export const LoadingOverlay = () => {
    return <div style={styles.loadingOverlay}>
        <div style={styles.overlayInfo}>
            <CircularProgress />
            <Typography variant="body2" color="text.secondary">
                Hledám rozhodnutí a připravuji shrnutí...
            </Typography>
        </div>
    </div >
}