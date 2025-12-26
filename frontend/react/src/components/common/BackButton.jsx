import { Box, Button } from "@mui/material";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";

/**
 * Reusable back button component
 */
export const BackButton = ({ to = "/trips", label, ...props }) => {
  const navigate = useNavigate();
  const { t } = useTranslation();

  return (
    <Box
      sx={{
        position: "fixed",
        bottom: 24,
        left: 0,
        right: 0,
        display: "flex",
        justifyContent: "center",
        zIndex: 10,
      }}
    >
      <Button
        variant="outlined"
        color="warning"
        onClick={() => navigate(to)}
        sx={{
          fontWeight: "bold",
          borderColor: "#fac948",
          color: "#fac948",
          "&:hover": {
            backgroundColor: "rgba(250, 201, 72, 0.15)",
            borderColor: "#fac948",
          },
        }}
        {...props}
      >
        {label || t("common.back")}
      </Button>
    </Box>
  );
};

