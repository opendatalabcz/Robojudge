import React, { useRef } from "react";
import { Fade, Typography } from "@mui/material";

import { ArrowDropDown } from "@mui/icons-material";

type ExpandedSearchProps = {
  isButtonShowed: boolean;
  searchMoreCases: () => Promise<void>;
};

export function ShowMoreButton({
  isButtonShowed,
  searchMoreCases,
}: ExpandedSearchProps) {
  const bottomRef = useRef(null);

  return (
    <Fade in={isButtonShowed}>
      <div
        ref={bottomRef}
        style={{
          display: "flex",
          justifyContent: "center",
          flexDirection: "column",
          alignItems: "center",
          cursor: "pointer",
          margin: "auto",
          width: "48px",
          height: "48px",
          marginTop: "2rem",
        }}
        onClick={async () => {
          await searchMoreCases();
          // bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
        }}
      >
        <Typography variant="overline">Další</Typography>
        <ArrowDropDown
          style={{
            color: "#597081",
            fontSize: "8rem",
            marginTop: "-3.5rem",
          }}
        />
      </div>
    </Fade>
  );
}
