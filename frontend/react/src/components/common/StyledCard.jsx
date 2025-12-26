import { Card } from "@mui/material";

/**
 * Reusable styled card component with consistent styling
 */
export const StyledCard = ({ children, width = 350, sx = {}, ...props }) => {
  return (
    <Card
      sx={{
        position: "relative",
        zIndex: 1,
        width,
        backdropFilter: "blur(6px)",
        backgroundColor: "rgba(250, 201, 72, 0.15)",
        border: "1px solid rgba(250, 201, 72, 0.3)",
        borderRadius: "8px",
        boxShadow: "0 8px 32px 0 rgba(250, 201, 72, 0.2)",
        fontFamily: "'Pacifico', cursive",
        textShadow: "2px 2px 6px rgba(0,0,0,0.6)",
        color: "#fac948",
        p: 3,
        ...sx,
      }}
      {...props}
    >
      {children}
    </Card>
  );
};

