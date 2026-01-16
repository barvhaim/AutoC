import { DonutChart } from "@carbon/charts-react";
import { IOCType } from "../../utils/consts.ts";
import { IOCItem } from "../IOCsTable/IOCsTable.tsx";
import "@carbon/charts/styles.css";

interface IOCsTypeChartProps {
  iocs: IOCItem[];
}

const IOCsTypeChart: React.FC<IOCsTypeChartProps> = ({ iocs }) => {
  const IOCTypeCount = Object.fromEntries(
    Object.keys(IOCType).map((type) => [type, 0]),
  );
  iocs.forEach(({ type }) => {
    if (type in IOCType) {
      IOCTypeCount[type]++;
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
