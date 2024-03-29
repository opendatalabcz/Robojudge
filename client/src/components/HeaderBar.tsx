import React from "react";
import { Link } from "react-router-dom";
import { AppBar, Button, ButtonGroup, Typography } from "@mui/material";
import GavelIcon from "@mui/icons-material/Gavel";

export function HeaderBar() {
  return (
    <AppBar
      position="relative"
      style={{ justifyContent: "space-between", flexDirection: "row" }}
    >
      <Button component={Link} to="/" type="text" style={{ color: "white" }}>
        <Typography
          padding="0.5rem"
          noWrap
          variant="h4"
          component="div"
          style={{
            display: "flex",
            alignItems: "center",
            letterSpacing: "0.03REM",
          }}
        >
          <GavelIcon style={{ marginRight: "10px", fontSize: "30px" }} />
          RoboJudge
        </Typography>
      </Button>
      <ButtonGroup variant="text">
        <Button component={Link} to="/info" style={{ color: "white" }}>
          <Typography padding="0.5rem" variant="h6" noWrap component="div">
            Info
          </Typography>
        </Button>
        <Button component={Link} to="/docs" style={{ color: "white" }}>
          <Typography padding="0.5rem" variant="h6" noWrap component="div">
            API
          </Typography>
        </Button>
      </ButtonGroup>
    </AppBar>
  );
}
