import React, { useState } from "react";
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
  TextInput,
} from "@carbon/react";
import { Download } from "@carbon/icons-react";

export interface IOCItem {
  type: string;
  value: string;
}

interface IOCsTableProps {
  iocs: IOCItem[];
}

const IOCsTable: React.FC<IOCsTableProps> = ({ iocs }) => {
  const [filterValue, setFilterValue] = useState("");

  const parsedIocs = iocs.map((ioc, index) => ({
    id: `${index}-${ioc.type}-${ioc.value}`,
    type: ioc.type,
    value: ioc.value,
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

  const [feedbacks, setFeedbacks] = useState<{ [key: string]: string }>({});

  return (
    <TableContainer>
      <TableToolbar>
        <TableToolbarContent>
          <TableToolbarSearch onChange={handleSearch} />
          <Button
            renderIcon={Download}
            onClick={exportToCSV}
            iconDescription="Export to CSV"
            kind="primary"
            size="lg"
          >
            Export CSV
          </Button>
        </TableToolbarContent>
      </TableToolbar>
      <DataTable
        rows={filteredRows}
        headers={[
          { key: "type", header: "Type" },
          { key: "value", header: "Value" },
          { key: "feedback", header: "Feedback" },
        ]}
      >
        {({ rows, headers, getHeaderProps, getTableProps }) => (
          <Table {...getTableProps()}>
            <TableHead>
              <TableRow>
                {headers.map((header) => (
                  <TableHeader
                    {...getHeaderProps({ header, isSortable: true })}
                  >
                    {header.header}
                  </TableHeader>
                ))}
              </TableRow>
            </TableHead>
            <TableBody>
              {rows.map((row) => (
                <TableRow key={row.id}>
                  <TableCell>
                    <Tag>{row.cells[0].value}</Tag>
                  </TableCell>
                  <TableCell style={{ fontFamily: "monospace" }}>
                    {row.cells[1].value}
                  </TableCell>
                  <TableCell style={{ minWidth: "200px" }}>
                    <TextInput
                      id={`feedback-${row.cells[1].value}`}
                      labelText=""
                      placeholder="Write feedback here..."
                      size="sm"
                      value={feedbacks[row.cells[1].value] || ""} // if there is a saved feedback (at feedbacks[...]) present it. else show nothing
                      onChange={(e) =>
                        setFeedbacks((prev) => ({
                          ...prev,
                          [row.cells[1].value]: e.target.value,
                        }))
                      }
                    />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </DataTable>
    </TableContainer>
  );
};

export default IOCsTable;
