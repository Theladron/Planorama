import { TextField } from "@mui/material";

/**
 * Reusable styled text field with consistent styling
 */
export const StyledTextField = ({ sx = {}, ...props }) => {
  return (
    <TextField
      variant="standard"
      InputLabelProps={{ shrink: true }}
      sx={{
        mb: 3,
        input: { color: "#f0e6cc" },
        "& .MuiInputLabel-root": { color: "#fac948" },
        "& .MuiInput-underline:before": { borderBottomColor: "#fac948" },
        ...sx,
      }}
      {...props}
    />
  );
};

