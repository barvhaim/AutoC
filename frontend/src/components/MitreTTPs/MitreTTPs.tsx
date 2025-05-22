import React from "react";
import { IconButton, Tag } from "@carbon/react";
import { Download } from "@carbon/icons-react";
import styles from "./MitreTTPs.module.scss";

interface MitreTTPsProps {
  mitreTTPs: {
    id: string;
    name: string;
    confidence: number;
    url: string;
  }[];
}

const MitreTTPs: React.FC<MitreTTPsProps> = ({ mitreTTPs }) => {
  const exportToCSV = () => {
    // Create CSV content
    const headers = ["ID", "Name", "Confidence", "URL"];
    const csvContent = [
      headers.join(","),
      ...mitreTTPs.map(
        (ttp) => `"${ttp.id}","${ttp.name}","${ttp.confidence}","${ttp.url}"`,
      ),
    ].join("\n");

    // Create blob and download link
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");

    // Set up and trigger download
    link.setAttribute("href", url);
    link.setAttribute("download", "mitre_ttps_export.csv");
    link.style.visibility = "hidden";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };
  return (
    <div>
      <div className={styles.mitre_ttps_container}>
        {mitreTTPs.map((ttp) => (
          <Tag
            type="warm-gray"
            className={styles.ttp_tag}
            onClick={(e: React.MouseEvent<HTMLDivElement, MouseEvent>) => {
              e.preventDefault();
              window.open(ttp.url, "_blank");
            }}
            key={ttp.id}
          >
            {`${ttp.id}: ${ttp.name}`}
          </Tag>
        ))}
      </div>
      {mitreTTPs.length > 0 && (
        <div className={styles.export_button_container}>
          <IconButton
            onClick={exportToCSV}
            kind="ghost"
            label="Export to CSV"
            title="Export TTPs to CSV"
          >
            <Download />
          </IconButton>
        </div>
      )}
    </div>
  );
};

export default MitreTTPs;
