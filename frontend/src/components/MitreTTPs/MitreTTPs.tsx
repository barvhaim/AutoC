import React from "react";
import { Tag } from "@carbon/react";
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
  return (
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
  );
};

export default MitreTTPs;
