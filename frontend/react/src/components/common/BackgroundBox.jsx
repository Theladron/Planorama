import { Box } from "@mui/material";

/**
 * Reusable background box component with overlay
 */
export const BackgroundBox = ({ children, sx = {}, ...props }) => {
  return (
    <Box
      sx={{
        minHeight: "100vh",
        backgroundImage: "url('/images/home_background.jpg')",
        backgroundSize: "cover",
        backgroundPosition: "center",
        position: "relative",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        p: 3,
        color: "#fff",
        "&::before": {
          content: '""',
          position: "absolute",
          top: 0,
          left: 0,
          width: "100%",
          height: "100%",
          backgroundColor: "rgba(0, 0, 0, 0.4)",
          zIndex: 0,
        },
        ...sx,
      }}
      {...props}
    >
      {children}
    </Box>
  );
};

