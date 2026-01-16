import { DonutChart } from "@carbon/charts-react";
import { IOCType } from "../../utils/consts.ts";
import { IOCItem } from "../IOCsTable/IOCsTable.tsx";
import "@carbon/charts/styles.css";

interface IOCsTypeChartProps {
  iocs: IOCItem[];
}

const IOCsTypeChart: React.FC<IOCsTypeChartProps> = ({ iocs }) => {
  // Count IOCs by their short display name
  const IOCTypeCount: Record<string, number> = Object.fromEntries(
    Object.values(IOCType).map((displayName) => [displayName, 0]),
  );
  iocs.forEach(({ type }) => {
    // Map backend type (e.g., "SHA256 Hash") to display name (e.g., "SHA256")
    const displayName = IOCType[type];
    if (displayName) {
      IOCTypeCount[displayName]++;
    }
  });
  const data = Object.entries(IOCTypeCount).map(([group, value]) => ({
    group,
    value,
  }));

  return (
    <DonutChart
      data={data}
      options={{
        height: "340px",
        theme: "g100",
        resizable: true,
        title: "Found IOCs by type",
        donut: {
          alignment: "center",
          center: {
            label: "IOCs",
          },
        },
      }}
    />
  );
};

export default IOCsTypeChart;
