import { Box, CircularProgress } from "@mui/material";

/**
 * Reusable loading spinner component
 */
export const LoadingSpinner = ({ fullHeight = true, sx = {}, ...props }) => {
  return (
    <Box
      sx={{
        display: "flex",
        height: fullHeight ? "100vh" : "auto",
        justifyContent: "center",
        alignItems: "center",
        ...sx,
      }}
      {...props}
    >
      <CircularProgress color="inherit" />
    </Box>
  );
};

