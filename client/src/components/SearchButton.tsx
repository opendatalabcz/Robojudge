import React from "react";
import { Button, Tooltip } from "@mui/material";

type SearchButtonProps = {
  tooltipText: string;
  isButtonDisabled: boolean;
  searchCases: () => Promise<void>;
};

export function SearchButton({
  tooltipText,
  isButtonDisabled,
  searchCases,
}: SearchButtonProps) {
  return (
    <Tooltip title={tooltipText} placement="bottom">
      {/* The tooltip will not display on disabled elements otherwise */}
      <div style={{ float: "right" }}>
        <Button
          onClick={searchCases}
          disabled={isButtonDisabled}
          variant="outlined"
        >
          Hledat
        </Button>
      </div>
    </Tooltip>
  );
}
