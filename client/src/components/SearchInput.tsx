import React from "react";
import { Chip, IconButton, TextField, Typography } from "@mui/material";
import { Close } from "@mui/icons-material";
import Grid2 from "@mui/material/Unstable_Grid2/Grid2";

import { DEFAULT_HELPER_TEXT, queryExamples } from "../utils/consts";

type SearchInputProps = {
  isLoading: boolean;
  caseDescription: string;
  setCaseDescription: (arg: string) => void;
};

export function SearchInput({
  isLoading,
  caseDescription,
  setCaseDescription,
}: SearchInputProps) {
  return (
    <>
      <Grid2>
        <TextField
          fullWidth
          multiline
          style={{ margin: 0 }}
          disabled={isLoading}
          minRows={1}
          maxRows={5}
          value={caseDescription}
          onChange={(e) => setCaseDescription(e.target.value)}
          label="Popis případu"
          helperText={DEFAULT_HELPER_TEXT}
          FormHelperTextProps={{ style: { marginLeft: 0 } }}
          InputProps={{
            endAdornment: (
              <IconButton
                sx={{
                  visibility: caseDescription ? "visible" : "hidden",
                  padding: "0",
                }}
                onClick={() => {
                  setCaseDescription("");
                }}
              >
                <Close />
              </IconButton>
            ),
          }}
          sx={{
            m: 2,
            "& .Mui-focused .MuiIconButton-root": {
              color: "primary.main",
            },
          }}
        ></TextField>
      </Grid2>
      <Typography variant="subtitle1">Příklady dotazů</Typography>
      {queryExamples.map((example, index) => (
        <Chip
          style={{ margin: "0.25rem" }}
          disabled={isLoading}
          key={index}
          label={example.text}
          color="primary"
          clickable
          onClick={() => setCaseDescription(example.text)}
        />
      ))}
    </>
  );
}
