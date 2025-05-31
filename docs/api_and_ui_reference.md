# Project Reference: Variables, IDs, Endpoints, and Payloads

This document catalogs all of the key identifiers, variables, DOM element IDs, JavaScript modules/functions, Flask API endpoints, and JSON payload fields used throughout the application.
*Whenever you propose code changes, consult this reference first to validate that any IDs, endpoints, and payload fields align exactly.*

---

## 1. Flask API Endpoints

### Labor & Equipment

| Method | URI                                                   | Description                              | Payload Keys                                                                             |
| ------ | ----------------------------------------------------- | ---------------------------------------- | ---------------------------------------------------------------------------------------- |
| POST   | `/labor-equipment/confirm-labor-equipment`            | Create or upsert labor/equipment entries | `project_id` (int), `date_of_report` (YYYY-MM-DD), `usage` (array of usage-line objects) |
| GET    | `/labor-equipment/by-project-date`                    | List pending entries for a project+date  | `project_id` (query), `date` (YYYY-MM-DD)                                                |
| PUT    | `/labor-equipment/update-entry/<entry_type>/<int:id>` | Update a single pending entry            | `{ hours: float, activity_code: string }`                                                |
| DELETE | `/labor-equipment/delete-entry/<entry_type>/<int:id>` | Delete a single pending entry            | n/a                                                                                      |

#### Required JSON Body for POST `/labor-equipment/confirm-labor-equipment`

```json
{
  "project_id": 24,
  "date_of_report": "2025-03-04",
  "usage": [
    {
      "employee_id": 7,
      "equipment_id": null,
      "hours": 8.0,
      "activity_code_id": 1313,
      "payment_item_id": 12,
      "cwp_id": "EXCAV",
      "is_manual": false,
      "manual_name": null
    },
    {
      "employee_id": null,
      "equipment_id": 5,
      "hours": 2.5,
      "activity_code_id": 1313,
      "payment_item_id": null,
      "cwp_id": null,
      "is_manual": false,
      "manual_name": null
    }
  ]
}
```

#### Usage‑Line Object for labor-equipment POST

```jsonc
{
  "employee_id":      int|null,       // if worker
  "equipment_id":     int|null,       // if equipment
  "hours":            number,         // required
  "activity_code_id": int,            // required, numeric PK of ActivityCode
  "payment_item_id":  int|null,
  "cwp_id":           string|null,
  "is_manual":        boolean,
  "manual_name":      string|null
}
```

---

### Materials

| Method | URI                                      | Description                                    | Payload Keys                                                             |
| ------ | ---------------------------------------- | ---------------------------------------------- | ------------------------------------------------------------------------ |
| POST   | `/materials/confirm-materials`           | Create material entries                        | `project_id`, `date_of_report`, `usage` (array of material-line objects) |
| GET    | `/materials/by-project-date`             | List pending material entries for project+date | `project_id` (query), `date`                                             |
| PUT    | `/materials/update-entry/<int:entry_id>` | Update quantity & activity for a material      | `{ quantity: float, activity_code: string }`                             |
| DELETE | `/materials/delete-entry/<int:entry_id>` | Delete a single material entry                 | n/a                                                                      |

#### Required JSON Body for POST `/materials/confirm-materials`

```json
{
  "project_id": 24,
  "date_of_report": "2025-03-04",
  "usage": [
    {
      "material_id": null,
      "manual_name": "Concrete Mix",
      "quantity": 20.5,
      "activity_code": "33000",
      "payment_item_id": 3,
      "cwp": "FOUND"
    },
    {
      "material_id": 12,
      "manual_name": null,
      "quantity": 100,
      "activity_code": "33000",
      "payment_item_id": null,
      "cwp": null
    }
  ]
}
```

#### Material‑Line Object for materials POST

```jsonc
{
  "material_id":      int|null,
  "manual_name":      string|null,
  "quantity":         number,           // required
  "activity_code":    string,           // required (code, not PK)
  "payment_item_id":  int|null,
  "cwp":              string|null
}
```

### Subcontractors

| Method | URI | Description | Payload Keys |
| ------ | --- | ----------- | ------------ |
| POST   | `/subcontractors/confirm-entries` | Create subcontractor entries | `project_number`, `date`, `usage` (array of entry objects) |
| GET    | `/subcontractors/by-project-date` | List pending subcontractor entries | `project_number` (query), `date`, `status` (query, optional) |
| PUT    | `/subcontractors/update-entry/<int:entry_id>` | Update a pending subcontractor entry | `{ hours: float, activity_code_id: int }` |
| DELETE | `/subcontractors/delete-entry/<int:entry_id>` | Delete a pending subcontractor entry | n/a |

#### Entry Object for subcontractor POST

```jsonc
{
  "subcontractor_id": int|null,
  "manual_name":      string|null,
  "num_employees":    int,
  "hours":            number,
  "activity_code_id": int
}
```


### Labor & Equipment

| Method | URI                                                   | Description                              | Payload Keys                                                                             |
| ------ | ----------------------------------------------------- | ---------------------------------------- | ---------------------------------------------------------------------------------------- |
| POST   | `/labor-equipment/confirm-labor-equipment`            | Create or upsert labor/equipment entries | `project_id` (int), `date_of_report` (YYYY-MM-DD), `usage` (array of usage-line objects) |
| GET    | `/labor-equipment/by-project-date`                    | List pending entries for a project+date  | `project_id` (query), `date` (YYYY-MM-DD)                                                |
| PUT    | `/labor-equipment/update-entry/<entry_type>/<int:id>` | Update a single pending entry            | `{ hours: float, activity_code: string }`                                                |
| DELETE | `/labor-equipment/delete-entry/<entry_type>/<int:id>` | Delete a single pending entry            | n/a                                                                                      |

#### Usage‑Line Object for labor-equipment POST

```jsonc
{
  "employee_id":      int|null,       // if worker
  "equipment_id":     int|null,       // if equipment
  "hours":            number,         // required
  "activity_code_id": int,            // required, numeric PK of ActivityCode
  "payment_item_id":  int|null,
  "cwp_id":           string|null,
  "is_manual":        boolean,
  "manual_name":      string|null
}
```

---

### Materials

| Method | URI                                      | Description                                    | Payload Keys                                                             |
| ------ | ---------------------------------------- | ---------------------------------------------- | ------------------------------------------------------------------------ |
| POST   | `/materials/confirm-materials`           | Create material entries                        | `project_id`, `date_of_report`, `usage` (array of material-line objects) |
| GET    | `/materials/by-project-date`             | List pending material entries for project+date | `project_id` (query), `date`                                             |
| PUT    | `/materials/update-entry/<int:entry_id>` | Update quantity & activity for a material      | `{ quantity: float, activity_code: string }`                             |
| DELETE | `/materials/delete-entry/<int:entry_id>` | Delete a single material entry                 | n/a                                                                      |

#### Material‑Line Object for materials POST

```jsonc
{
  "material_id":      int|null,
  "manual_name":      string|null,
  "quantity":         number,           // required
  "activity_code":    string,           // required (code, not PK)
  "payment_item_id":  int|null,
  "cwp":              string|null
}
```
### Documents

| Method | URI | Description | Payload Keys |
| ------ | --- | ----------- | ------------ |
| GET    | `/documents/list` | List documents for current project/date | n/a |
| GET    | `/documents/files/<filename>` | Serve uploaded file | n/a |
| POST   | `/documents/upload` | Upload files (FormData) | `files`, `document_type`, `project_id`, `work_date`, `doc_notes`, `activity_code_id`, `payment_item_id`, `cwp_code` |

#### Hover Preview

Include a container with ID `docPreview` (containing an `img#docPreviewImg`) on pages
that list document links. The preview box is shown on link hover for files ending
in `jpg`, `jpeg`, `png` or `gif`.

---

## 2. JavaScript Modules & Main Functions

* \`\`

  * `showToday()`                     → updates `#todayDate`
  * `highlightDates()`               → colors options in `#dateSelector` (if `<select>`)
  * `confirmDateSelection(date)`     → POST to `/data-entry/initialize-day`
  * `getTemperature()`               → GET `/weather`, updates `#weatherIcon` & `#currentTemperature`
  * `markTabComplete(tab)`           → POST `/update-progress`, updates UI badge & `#progress-bar`
  * `restoreProgress()`              → GET `/update-progress/get-progress`, reconstructs completed tabs

* \`\`

  * `populateDropdowns()`            ↦ parallel:

    * `populateWorkersAndEquipmentDropdown()` → GET `/workers-and-equipment/list`
    * `populateActivityDropdown()`            → GET `/activity-codes/get_activity_codes`
    * `populatePaymentItemDropdown()`        → GET `/payment-items/list`
    * `populateCwpDropdown()`                → GET `/cw-packages/list`

* \`\`

  * `initLaborEquipmentTab()`         → bootstrap form, buttons, load pending
  * `toggleManualEntry(mode)`         → show/hide manual inputs
  * `addUsageLine(event)`             → stage preview row in `confirmedUsageData`
  * `renderPreviewTable()`            → draw `tr.preview-row` in `#workersTable`
  * `confirmUsageLines(event)`        → POST to `/labor-equipment/confirm-labor-equipment`
  * `loadPendingEntries(pId,date)`    → GET `/labor-equipment/by-project-date`
  * `renderConfirmedTable(workers,equipment)` → draw `tr.confirmed-row`
  * `handleEdit()`, `saveEdit()`, `handleDelete()` → inline edit/delete

* \`\`

  * `initMaterialsTab()`              → bootstrap form, load pending
  * `addMaterialLine(event)`          → stage preview row
  * `renderPreviewTable()`            → draw `tr.preview-row` in `#materialsTable`
  * `confirmMaterialLines(event)`     → POST to `/materials/confirm-materials`
  * `loadPendingMaterials(pId,date)` → GET `/materials/by-project-date`
  * `renderConfirmedTableFromServer(materials)` → draw confirmed rows
  * `handleEditConfirmedRow()`, `handleDeleteConfirmedRow()` → edit/delete
  
  * \`\`

  * `initDocumentsTab()`            → bootstrap form & load list
  * `loadDocuments()`               → GET `/documents/list`, populate table
  * `showPreview(url, anchor)`      → show `#docPreview` for allowed images
  * `hidePreview()`                 → hide the preview bo
---

## 3. DOM Element IDs & Global JS Vars

### Globals (Header & Tabs)

```
#projectNumber        // selected project
#dateSelector         // active report date
#todayDate            // real “today” span
#currentTemperature   // weather °C
#weatherIcon          // weather icon img
#progress-bar         // progress bar fill element
```

### Labor/Equipment Form

```
#workerName           // dropdown “worker|id” or “equipment|id”
#manualWorkerName     // freeform worker name
#manualEquipmentName  // freeform equipment name
#laborHours           // hours input
#activityCode         // activity code select
#payment_item_id      // payment item select
#cwp_code             // CWP code select
#addEntryBtn          // add preview button
#confirmEntriesBtn    // confirm all staged
#workersTable         // combined preview + confirmed table
```

### Materials Form

```
#materialName
#materialQuantity
#materialActivityCode
#materialPaymentItem
#materialCwp
#addMaterialBtn
#confirmMaterialsBtn
#materialsTable
```
### Documents Tab

```
#documentFiles
#documentType
#uploadDocumentsBtn
#documentsTable
#docActivityCode
#docPaymentItem
#docCwp
#docTags
#docNote
#docNotes
#docPreview        // preview container
#docPreviewImg
```

### Notes Form

```
#noteDatetime
#noteAuthor
#noteCategory
#noteTags
#noteActivityCode
#notePaymentItem
#noteCwp
#noteContent
#saveNoteBtn
#dictateNoteBtn
#dailyNotesContainer
```
### Admin Section

```
#adminMenu
#menu-master
#menu-documents
#menu-users
#menu-importExport
#workerForm
#uploadMedia
#userAccountForm
#databaseBackup
```

---

## 4. JSON Payload Field Names

* **Common**: `project_id`, `date_of_report`
* **Labor/Equipment**: `employee_id`, `equipment_id`, `hours`, `activity_code_id`, `payment_item_id`, `cwp_id`, `is_manual`, `manual_name`
* **Materials**: `material_id`, `manual_name`, `quantity`, `activity_code`, `payment_item_id`, `cwp`
* **Documents**: `files`, `document_type`, `project_id`, `work_date`, `doc_notes`, `activity_code_id`, `payment_item_id`, `cwp_code`
* **Update (PUT)**: labor→ `{ hours, activity_code }`, materials→ `{ quantity, activity_code }`

---

## 5. Validation Checklist

Before writing or updating code:

1. **DOM IDs** – verify every `getElementById` or querySelector uses an ID listed in Section 3.
2. **Endpoints** – confirm the URI and HTTP method match exactly Section 1.
3. **Payload** – ensure JSON keys/types align with the schema in Section 1 or Section 4.
4. **Module Names & Functions** – import and call only the functions listed in Section 2.

*Keep this reference updated and consult it for every new feature or bug fix.*
