import React, { useState } from "react";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import { Box, Collapse, Typography } from "@mui/material";
import Grid2 from "@mui/material/Unstable_Grid2/Grid2";
import { DatePicker } from "@mui/x-date-pickers";
import { Dayjs } from "dayjs";

type ExpandedSearchProps = {
  sentenceDateFrom: Dayjs;
  sentenceDateTo: Dayjs;
  publicationDateFrom: Dayjs;
  publicationDateTo: Dayjs;
  setSentenceDateFrom: (arg: Dayjs) => void;
  setSentenceDateTo: (arg: Dayjs) => void;
  setPublicationDateFrom: (arg: Dayjs) => void;
  setPublicationDateTo: (arg: Dayjs) => void;
};

export function ExpandedSearch(props: ExpandedSearchProps) {
  const [isCardExpanded, setIsCardExpanded] = useState(false);

  return (
    <>
      <Box
        display="flex"
        alignItems="center"
        onClick={() => setIsCardExpanded(!isCardExpanded)}
        style={{ cursor: "pointer", width: "200px" }}
      >
        <Typography variant="subtitle1">Rozšířené vyhledávání</Typography>
        <ExpandMoreIcon
          style={{
            transform: !isCardExpanded ? "rotate(0deg)" : "rotate(180deg)",
            marginLeft: "auto",
            float: "right",
          }}
        />
      </Box>
      <Collapse in={isCardExpanded} timeout="auto">
        <Grid2 spacing={2} container style={{ padding: "0.5rem" }}>
          <Grid2 spacing={2} container flexDirection="row" alignItems="center">
            <Grid2>
              <DatePicker
                sx={{ width: "260px" }}
                slotProps={{
                  field: {
                    clearable: true,
                    onClear: () => props.setSentenceDateFrom(null),
                  },
                }}
                label="Datum vydání (od)"
                format="DD.MM.YYYY"
                value={props.sentenceDateFrom}
                onChange={(newValue) => props.setSentenceDateFrom(newValue)}
              />
            </Grid2>
            <Grid2>-</Grid2>
            <Grid2>
              <DatePicker
                sx={{ width: "260px" }}
                slotProps={{
                  field: {
                    clearable: true,
                    onClear: () => props.setSentenceDateTo(null),
                  },
                }}
                label="Datum vydání (do)"
                format="DD.MM.YYYY"
                value={props.sentenceDateTo}
                onChange={(newValue) => props.setSentenceDateTo(newValue)}
              />
            </Grid2>
          </Grid2>
          <Grid2 spacing={2} container flexDirection="row" alignItems="center">
            <Grid2>
              <DatePicker
                sx={{ width: "260px" }}
                slotProps={{
                  field: {
                    clearable: true,
                    onClear: () => props.setPublicationDateFrom(null),
                  },
                }}
                label="Datum zveřejnění (od)"
                format="DD.MM.YYYY"
                value={props.publicationDateFrom}
                onChange={(newValue) => props.setPublicationDateFrom(newValue)}
              />
            </Grid2>
            <Grid2>-</Grid2>
            <Grid2>
              <DatePicker
                sx={{ width: "260px" }}
                slotProps={{
                  field: {
                    clearable: true,
                    onClear: () => props.setPublicationDateTo(null),
                  },
                }}
                label="Datum zveřejnění (do)"
                format="DD.MM.YYYY"
                value={props.publicationDateTo}
                onChange={(newValue) => props.setPublicationDateTo(newValue)}
              />
            </Grid2>
          </Grid2>
        </Grid2>
      </Collapse>
    </>
  );
}
