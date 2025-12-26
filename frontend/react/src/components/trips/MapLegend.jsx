import { useTranslation } from "react-i18next";

/**
 * Map legend component
 */
export const MapLegend = () => {
  const { t } = useTranslation();

  return (
    <div
      style={{
        position: "absolute",
        bottom: 20,
        left: 20,
        background: "white",
        padding: "8px 12px",
        border: "1px solid rgba(250, 201, 72, 0.25)",
        borderRadius: 6,
        boxShadow: "0 6px 20px rgba(250, 201, 72, 0.1)",
        zIndex: 1000,
        fontSize: 14,
        backgroundColor: "rgba(250, 201, 72, 0.2)",
        backdropFilter: "blur(3px)",
        textShadow: "1px 1px 4px rgba(0, 0, 0, 0.5)",
      }}
    >
      <div><strong>{t("tripsgeneration.legend", "Legend")}</strong></div>
      <div>{t("tripsgeneration.legend_info", "Click on a route or icon to see more information.")}</div>
      <div>
        <img
          src="https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-blue.png"
          alt="Blue marker"
          style={{ width: 13, height: 20, marginRight: 6 }}
        />
        Station
      </div>
      <div>
        <img
          src="https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png"
          alt="Red marker"
          style={{ width: 13, height: 20, marginRight: 6 }}
        />
        {t("tripsgeneration.overnight", "Overnight")}
      </div>
      <div>
        <img
          src="https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-green.png"
          alt="Green marker"
          style={{ width: 13, height: 20, marginRight: 6 }}
        />
        {t("tripsgeneration.activities", "Activity")}
      </div>
    </div>
  );
};

