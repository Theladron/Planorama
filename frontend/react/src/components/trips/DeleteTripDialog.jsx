import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Button,
  CircularProgress,
} from "@mui/material";
import { useTranslation } from "react-i18next";

/**
 * Confirmation dialog for deleting a trip
 */
export const DeleteTripDialog = ({ open, onClose, onConfirm, loading }) => {
  const { t } = useTranslation();

  return (
    <Dialog
      open={open}
      onClose={onClose}
      aria-labelledby="delete-trip-dialog-title"
      aria-describedby="delete-trip-dialog-description"
    >
      <DialogTitle id="delete-trip-dialog-title">
        {t("trips.confirmDeleteTitle")}
      </DialogTitle>
      <DialogContent>
        <DialogContentText id="delete-trip-dialog-description">
          {t("trips.confirmDeleteText")}
        </DialogContentText>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} disabled={loading}>
          {t("trips.cancel")}
        </Button>
        <Button onClick={onConfirm} color="error" disabled={loading} autoFocus>
          {loading ? <CircularProgress size={20} /> : t("trips.delete")}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

