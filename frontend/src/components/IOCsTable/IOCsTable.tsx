import React, { useState } from "react";
import { useSelector } from "react-redux";
import {
  DataTable,
  Table,
  TableHead,
  TableRow,
  TableHeader,
  TableBody,
  TableCell,
  Tag,
  TableToolbar,
  TableToolbarContent,
  TableToolbarSearch,
  Button,
  TableContainer,
  OverflowMenu,
  OverflowMenuItem,
} from "@carbon/react";
import { Download } from "@carbon/icons-react";
import { cleanIocValue } from "../../utils/strings.ts";
import { getVirusTotalUrl } from "../../utils/virusTotal.ts";
import { postFeedback } from "../../service/feedback.ts";
import { exportToStix } from "../../utils/stixExport.ts";

export interface IOCItem {
  type: string;
  value: string;
}

interface IOCsTableProps {
  iocs: IOCItem[];
}

const IOCsTable: React.FC<IOCsTableProps> = ({ iocs }) => {
  const analyzedUrl = useSelector((state: any) => state.analysis.url);
  const [filterValue, setFilterValue] = useState("");

  const parsedIocs = iocs.map((ioc, index) => ({
    id: `${index}-${ioc.type}-${ioc.value}`,
    type: ioc.type,
    value: cleanIocValue(ioc.value),
  }));

  const exportToCSV = () => {
    // Create CSV content
    const headers = ["Type", "Value"];
    const csvContent = [
      headers.join(","),
      ...iocs.map((ioc) => `"${ioc.type}","${ioc.value}"`),
    ].join("\n");

    // Create blob and download link
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");

    // Set up and trigger download
    link.setAttribute("href", url);
    link.setAttribute("download", "iocs_export.csv");
    link.style.visibility = "hidden";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const exportToStixFormat = () => {
    exportToStix(iocs);
  };

  const handleSearch = (
    event: "" | React.ChangeEvent<HTMLInputElement>,
    value?: string,
  ) => {
    // Use the provided value if available, otherwise get it from the event
    const searchValue =
      typeof value === "string"
        ? value
        : event !== ""
          ? event.target.value
          : "";

    setFilterValue(searchValue);
  };

  // Filter rows based on search input
  const filteredRows =
    filterValue.trim() === ""
      ? parsedIocs
      : parsedIocs.filter(
          (ioc) =>
            ioc.type.toLowerCase().includes(filterValue.toLowerCase()) ||
            ioc.value.toLowerCase().includes(filterValue.toLowerCase()),
        );

  return (
    <DataTable
      rows={filteredRows}
      headers={[
        { key: "type", header: "Type" },
        { key: "value", header: "Value" },
      ]}
      experimentalAutoAlign={true}
    >
      {({ rows, headers, getHeaderProps, getTableProps }) => (
        <TableContainer>
          <TableToolbar size={"sm"}>
            <TableToolbarContent>
              <TableToolbarSearch onChange={handleSearch} size={"sm"} />
              <Button
                renderIcon={Download}
                onClick={exportToCSV}
                iconDescription="Export to CSV"
                kind="tertiary"
                size="sm"
              >
                Export CSV
              </Button>
              <Button
                renderIcon={Download}
                onClick={exportToStixFormat}
                iconDescription="Export to STIX"
                kind="tertiary"
                size="sm"
              >
                Export STIX
              </Button>
            </TableToolbarContent>
          </TableToolbar>
          <Table {...getTableProps()} size={"sm"}>
            <TableHead>
              <TableRow>
                {headers.map((header) => (
                  <TableHeader
                    {...getHeaderProps({ header, isSortable: true })}
                  >
                    {header.header}
                  </TableHeader>
                ))}
                <TableHeader className="cds--table-column-menu" />
              </TableRow>
            </TableHead>
            <TableBody>
              {rows.map((row) => {
                const url = getVirusTotalUrl(
                  row.cells[0].value,
                  row.cells[1].value,
                );
                return (
                  <TableRow key={row.id}>
                    <TableCell>
                      <Tag>{row.cells[0].value}</Tag>
                    </TableCell>
                    <TableCell style={{ fontFamily: "monospace" }}>
                      {row.cells[1].value}
                    </TableCell>
                    <TableCell className="cds--table-column-menu">
                      {url !== "" && (
                        <OverflowMenu
                          aria-label="overflow-menu"
                          align="left"
                          light={false}
                          size="sm"
                          flipped
                          className="cds--overflow-menu--primary"
                        >
                          <OverflowMenuItem
                            id={"view-in-virustotal"}
                            itemText={"🦠 Scan VirusTotal"}
                            onClick={() => {
                              window.open(url, "_blank");
                            }}
                            hasDivider={false}
                          />
                          <OverflowMenuItem
                            id={"copy-ioc-value"}
                            itemText={"🔗 Copy"}
                            hasDivider={true}
                            onClick={() => {
                              navigator.clipboard.writeText(row.cells[1].value);
                            }}
                          />
                          <OverflowMenuItem
                            id={"thumbs-up"}
                            itemText={"👍 Accurate!"}
                            hasDivider={true}
                            onClick={() => {
                              const feedback = {
                                url: analyzedUrl,
                                feedback_type: "ioc",
                                context: `${row.cells[0].value} | ${row.cells[1].value}`,
                                value: 1,
                              };
                              postFeedback(feedback)
                                .then(() => {
                                  console.debug("Feedback sent:", feedback);
                                })
                                .catch((err) => {
                                  console.error("Error sending feedback:", err);
                                });
                            }}
                          />
                          <OverflowMenuItem
                            id={"thumbs-down"}
                            itemText={"😵‍💫 Inaccurate"}
                            onClick={() => {
                              const feedback = {
                                url: analyzedUrl,
                                feedback_type: "ioc",
                                context: `${row.cells[0].value} | ${row.cells[1].value}`,
                                value: -1,
                              };
                              postFeedback(feedback)
                                .then(() => {
                                  console.debug("Feedback sent:", feedback);
                                })
                                .catch((err) => {
                                  console.error("Error sending feedback:", err);
                                });
                            }}
                          />
                        </OverflowMenu>
                      )}
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </DataTable>
  );
};

export default IOCsTable;
