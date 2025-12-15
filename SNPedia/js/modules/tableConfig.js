/**
 * Table Configuration Module
 * Handles Tabulator table initialization and column definitions
 */

export class TableConfig {
  static getColumnDefinitions() {
    return [
      {
        title: "Name",
        field: "Name",
        visible: true,
        headerFilter: "input",
        width: 120
      },
      {
        title: "Short Description",
        field: "Description",
        headerFilter: "input",
        widthGrow: 2,
        formatter: "html"
      },
      {
        title: "Stabilized Orientation",
        field: "StabilizedOrientation",
        visible: false,
        headerFilter: "input"
      },
      {
        title: "Individual Genotype",
        field: "Genotype",
        visible: false,
        headerFilter: "input",
        formatter: "html"
      },
      {
        title: "Genotype variations",
        field: "Variations",
        headerFilter: "input",
        widthGrow: 1,
        formatter: "html"
      },
      {
        title: "Interesting genotype",
        field: "IsInteresting",
        visible: false,
        headerFilter: "list",
        headerFilterParams: {
          values: {
            "": "All",
            "Yes": "Yes",
            "No": "No"
          },
          clearable: true,
          placeholder: "Filter..."
        }
      },
      {
        title: "Uncommon genotype",
        field: "IsUncommon",
        visible: false,
        headerFilter: "list",
        headerFilterParams: {
          values: {
            "": "All",
            "Yes": "Yes",
            "No": "No"
          },
          clearable: true,
          placeholder: "Filter..."
        }
      }
    ];
  }

  static getTableOptions() {
    return {
      layout: "fitColumns",
      layoutColumnsOnNewData: true,
      height: "100%",
      pagination: true,
      paginationSize: 50,
      paginationSizeSelector: [25, 50, 100, 250],
      movableColumns: true,
      resizableColumnFit: true,
      selectable: true,
      selectableRollingSelection: false,
      columns: this.getColumnDefinitions(),
      initialSort: [
        { column: "IsUncommon", dir: "desc" }
      ]
    };
  }
}