BEGIN TRANSACTION;
CREATE TABLE "activity_codes" (
	id INTEGER NOT NULL, 
	code VARCHAR(50) NOT NULL, 
	project_id INTEGER, 
	cwp VARCHAR(50), 
	description VARCHAR(255) NOT NULL, 
	unit VARCHAR(50), 
	std_man_hours_per_unit FLOAT, 
	created_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(project_id) REFERENCES projects (id) ON DELETE CASCADE
);
INSERT INTO "activity_codes" VALUES(1,'',NULL,NULL,'',NULL,NULL,NULL);
INSERT INTO "activity_codes" VALUES(2,'1313',NULL,NULL,'Gestion de projet','hrs',1.0,'2025-01-07');
INSERT INTO "activity_codes" VALUES(3,'1521',NULL,NULL,'Bureaux de chantier/sanitaire',NULL,NULL,'2025-01-07');
INSERT INTO "activity_codes" VALUES(4,'31000',NULL,NULL,'Excavations','m3',0.03,'2025-01-07');
INSERT INTO "activity_codes" VALUES(5,'32111',NULL,NULL,'Clotures et barrieres','ml',NULL,'2025-01-07');
INSERT INTO "activity_codes" VALUES(6,'33000',NULL,NULL,'Egouts et aqueducs','ml',1.0,'2024-01-07');
INSERT INTO "activity_codes" VALUES(7,'33011',NULL,NULL,'Aqueduc','ml',0.8,'2024-01-07');
INSERT INTO "activity_codes" VALUES(8,'80001',NULL,NULL,'deplacement des roulottes de chantier',NULL,NULL,NULL);
CREATE TABLE alembic_version (
	version_num VARCHAR(32) NOT NULL, 
	CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);
INSERT INTO "alembic_version" VALUES('a87f3c0b5e8c');
CREATE TABLE entries_daily_notes (
	id INTEGER NOT NULL, 
	project_id INTEGER NOT NULL, 
	note TEXT NOT NULL, 
	created_by VARCHAR(255), 
	created_at DATETIME, 
	category VARCHAR(50), 
	priority VARCHAR(6), 
	linked_activity_code INTEGER, 
	attachment_url VARCHAR(2083), 
	editable_by VARCHAR(255), 
	PRIMARY KEY (id), 
	FOREIGN KEY(linked_activity_code) REFERENCES activity_codes (id), 
	FOREIGN KEY(project_id) REFERENCES projects (id)
);
INSERT INTO "entries_daily_notes" VALUES(1,3,'cecci est un test de note','1','2025-01-06','extras','hogh',4,'"C:\Users\patri\OneDrive\Bureau\TCC_V2.0\20241024_134840.jpg"',NULL);
INSERT INTO "entries_daily_notes" VALUES(2,4,'ceci est aussi un test de notes','pascal patrice','2025-01-06','general','low',2,'"C:\Users\patri\OneDrive\Bureau\TCC_V2.0\20241024_134840.jpg"',NULL);
CREATE TABLE daily_pictures (
	id INTEGER NOT NULL, 
	project_id INTEGER NOT NULL, 
	file_name VARCHAR(255) NOT NULL, 
	file_url VARCHAR(2083) NOT NULL, 
	description TEXT, 
	taken_at DATETIME, 
	uploaded_at DATETIME, 
	activity_code VARCHAR(50), 
	work_order_id INTEGER, 
	daily_note_id INTEGER, 
	coordinates JSON, 
	position VARCHAR(255), 
	size FLOAT, 
	tags JSON, 
	captured_by VARCHAR(255), 
	PRIMARY KEY (id), 
	FOREIGN KEY(activity_code) REFERENCES activity_codes (id), 
	FOREIGN KEY(daily_note_id) REFERENCES entries_daily_notes (id), 
	FOREIGN KEY(project_id) REFERENCES projects (id), 
	FOREIGN KEY(work_order_id) REFERENCES work_orders (id)
);
INSERT INTO "daily_pictures" VALUES(1,3,'test image','"C:\Users\patri\OneDrive\Bureau\TCC_V2.0\data\20240805_082846.jpg"','avancement batiment','2024-08-01',NULL,'2',NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "daily_pictures" VALUES(2,4,'test image','"C:\Users\patri\OneDrive\Bureau\TCC_V2.0\data\20240805_082846.jpg"','avancement batiment 2','2024-08-01',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
CREATE TABLE daily_report_statuses (
	id INTEGER NOT NULL, 
	project_id INTEGER NOT NULL, 
	report_date DATE NOT NULL, 
	workers_tab VARCHAR(11), 
	materials_tab VARCHAR(11), 
	equipment_tab VARCHAR(11), 
	notes_tab VARCHAR(11), 
	pictures_tab VARCHAR(11), 
	subcontractors_tab VARCHAR(11), 
	workorders_tab VARCHAR(11), 
	report_status VARCHAR(11), 
	created_at DATETIME, 
	updated_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(project_id) REFERENCES projects (id)
);
INSERT INTO "daily_report_statuses" VALUES(1,2,'2025-01-07','in_progress',NULL,NULL,NULL,NULL,NULL,NULL,'completed','2025-01-07',NULL);
INSERT INTO "daily_report_statuses" VALUES(2,3,'2025-01-30','completed',NULL,NULL,NULL,NULL,NULL,NULL,'in_progress','2025-01-07',NULL);
INSERT INTO "daily_report_statuses" VALUES(3,4,'2025-02-02','completed','completed','completed',NULL,NULL,NULL,NULL,'completed','2025-01-07',NULL);
INSERT INTO "daily_report_statuses" VALUES(4,3,'2025-02-03','in_progress','completed','completed',NULL,NULL,NULL,NULL,'in_progress','2025-01-07',NULL);
CREATE TABLE documents (
	id INTEGER NOT NULL, 
	project_id INTEGER NOT NULL, 
	file_name VARCHAR(255) NOT NULL, 
	file_url VARCHAR(2083) NOT NULL, 
	uploaded_at DATETIME, 
	document_type VARCHAR(16) NOT NULL, 
	category VARCHAR(50), 
	daily_note_id INTEGER, 
	picture_repository_url VARCHAR(2083), 
	is_approved BOOLEAN, 
	approved_by VARCHAR(255), 
	approval_date DATETIME, 
	tags JSON, 
	created_at DATETIME, 
	last_modified_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(daily_note_id) REFERENCES entries_daily_notes (id), 
	FOREIGN KEY(project_id) REFERENCES projects (id)
);
INSERT INTO "documents" VALUES(1,3,'project_tree','"C:\Users\patri\OneDrive\Bureau\TCC_V2.0\project_tree.docx"',NULL,'.docx','General',NULL,NULL,NULL,NULL,NULL,'project tree','2025-01-07',NULL);
CREATE TABLE "entries_equipment" (
	id INTEGER NOT NULL, 
	date_of_report DATE NOT NULL, 
	project_id INTEGER NOT NULL, 
	equipment_id INTEGER NOT NULL, 
	hours_used FLOAT NOT NULL, 
	activity_id INTEGER, 
	cwp VARCHAR(50), 
	phase VARCHAR(50), 
	usage_description TEXT, 
	created_at DATETIME, 
	updated_at DATETIME, 
	status VARCHAR(11), 
	PRIMARY KEY (id), 
	FOREIGN KEY(activity_id) REFERENCES activity_codes (id), 
	FOREIGN KEY(equipment_id) REFERENCES equipment (id), 
	FOREIGN KEY(project_id) REFERENCES projects (id)
);
INSERT INTO "entries_equipment" VALUES(1,'2025-01-06',3,4,8.0,NULL,NULL,NULL,NULL,'2025-01-06',NULL,NULL);
INSERT INTO "entries_equipment" VALUES(2,'2025-01-06',4,3,8.0,NULL,NULL,NULL,NULL,'2025-01-06',NULL,NULL);
INSERT INTO "entries_equipment" VALUES(3,'2025-01-06',3,3,8.0,NULL,NULL,NULL,NULL,'2025-01-06',NULL,NULL);
INSERT INTO "entries_equipment" VALUES(4,'2025-01-06',4,2,8.0,NULL,NULL,NULL,NULL,'2025-01-06',NULL,NULL);
CREATE TABLE "entries_material" (
	id INTEGER NOT NULL, 
	material_id INTEGER NOT NULL, 
	project_id INTEGER NOT NULL, 
	purchase_order_id INTEGER, 
	activity_code_id INTEGER, 
	task_id INTEGER, 
	work_order_id INTEGER, 
	material_name VARCHAR(255), 
	unit VARCHAR(50), 
	unit_price FLOAT, 
	quantity_used FLOAT, 
	supplier_name VARCHAR(255), 
	cost FLOAT, 
	procurement_status VARCHAR(50), 
	created_at DATETIME, 
	updated_at DATETIME, 
	status VARCHAR(11), 
	PRIMARY KEY (id), 
	FOREIGN KEY(material_id) REFERENCES materials (id), 
	FOREIGN KEY(project_id) REFERENCES projects (id), 
	FOREIGN KEY(activity_code_id) REFERENCES activity_codes (id), 
	FOREIGN KEY(purchase_order_id) REFERENCES purchase_orders (id), 
	FOREIGN KEY(task_id) REFERENCES project_tasks (id), 
	FOREIGN KEY(work_order_id) REFERENCES work_orders (id)
);
INSERT INTO "entries_material" VALUES(1,2,3,2,NULL,NULL,NULL,NULL,NULL,NULL,1000.0,NULL,NULL,NULL,'2025-01-06',NULL,NULL);
INSERT INTO "entries_material" VALUES(2,3,4,3,NULL,NULL,NULL,NULL,NULL,NULL,25.0,NULL,NULL,NULL,NULL,NULL,NULL);
CREATE TABLE "entries_workers" (
	"id"	INTEGER NOT NULL,
	"date_of_report"	DATE NOT NULL,
	"project_id"	INTEGER NOT NULL,
	"worker_id"	INTEGER NOT NULL,
	"hours_worked"	FLOAT NOT NULL,
	"activity_id"	INTEGER,
	"cwp"	VARCHAR(50),
	"phase"	VARCHAR(50),
	"created_at"	DATETIME,
	"updated_at"	DATETIME,
	"status"	VARCHAR(11),
	PRIMARY KEY("id"),
	FOREIGN KEY("activity_id") REFERENCES "activity_codes"("id"),
	FOREIGN KEY("project_id") REFERENCES "projects"("id"),
	FOREIGN KEY("worker_id") REFERENCES "workers"("id")
);
INSERT INTO "entries_workers" VALUES(1,'2025-01-06',3,2,8.0,NULL,NULL,NULL,'2025-01-06',NULL,NULL);
INSERT INTO "entries_workers" VALUES(2,'2025-01-06',4,3,8.0,NULL,NULL,NULL,'2025-01-07',NULL,NULL);
INSERT INTO "entries_workers" VALUES(3,'2025-01-06',3,3,8.0,NULL,NULL,NULL,'2025-01-06',NULL,NULL);
CREATE TABLE "equipment" (
	id INTEGER NOT NULL, 
	equipment_id VARCHAR(100), 
	name VARCHAR(255) NOT NULL, 
	serial_number VARCHAR(100), 
	assigned_to VARCHAR(100), 
	assigned_project_id INTEGER, 
	maintenance_status VARCHAR(17), 
	hourly_rate FLOAT, 
	last_maintenance_date DATETIME, 
	next_maintenance_date DATETIME, 
	latitude FLOAT, 
	longitude FLOAT, 
	device_id VARCHAR(100), 
	telemetry_data JSON, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME, 
	PRIMARY KEY (id), 
	UNIQUE (equipment_id), 
	UNIQUE (serial_number), 
	FOREIGN KEY(assigned_project_id) REFERENCES projects (id), 
	UNIQUE (device_id)
);
INSERT INTO "equipment" VALUES(1,NULL,'',NULL,NULL,NULL,'',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'',NULL);
INSERT INTO "equipment" VALUES(2,'BU-06','BU-06_Bouteur Moyen (750, D6, D61 )_KOMATSU D61PX
','12341324f523r3q',NULL,NULL,'operational',120.0,'2024-12-01','2025-03-01',NULL,NULL,NULL,NULL,'2025-01-06',NULL);
INSERT INTO "equipment" VALUES(3,'L-25','L-25_Chargeur sur roues_TAKEUCHI TW95C
','67h63f6u457g6766',NULL,NULL,'operational',125.0,'2024-12-01','2025-03-01',NULL,NULL,NULL,NULL,'2025-01-07',NULL);
INSERT INTO "equipment" VALUES(4,'PE-45','PE-45_Excavatrice 35 Tonnes_KOMATSU PC360
','654654we5tvfdg541654',NULL,NULL,'operational',200.0,'2024-12-01','2025-03-01',NULL,NULL,NULL,NULL,'2025-01-07',NULL);
CREATE TABLE equipment_assignments (
	worker_id INTEGER NOT NULL, 
	equipment_id INTEGER NOT NULL, 
	project_id INTEGER NOT NULL, 
	start_date DATE, 
	end_date DATE, 
	role VARCHAR(50), 
	notes VARCHAR(255), 
	PRIMARY KEY (worker_id, equipment_id), 
	FOREIGN KEY(equipment_id) REFERENCES equipment (id), 
	FOREIGN KEY(project_id) REFERENCES projects (id), 
	FOREIGN KEY(worker_id) REFERENCES workers (id)
);
INSERT INTO "equipment_assignments" VALUES(2,4,3,'2025-01-06','2025-01-30','operateur de pelle','rempalce M.chose qui est malade');
INSERT INTO "equipment_assignments" VALUES(3,3,3,'2025-01-06','2025-01-15','operateur mach lourde',NULL);
CREATE TABLE "materials" (
	id INTEGER NOT NULL, 
	material_id VARCHAR(100), 
	name VARCHAR(255) NOT NULL, 
	unit VARCHAR(50), 
	cost_per_unit FLOAT, 
	description TEXT, 
	project_id INTEGER, 
	purchase_order_id INTEGER, 
	created_at DATETIME, 
	updated_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(purchase_order_id) REFERENCES purchase_orders (id), 
	FOREIGN KEY(project_id) REFERENCES projects (id) ON DELETE CASCADE, 
	UNIQUE (material_id)
);
INSERT INTO "materials" VALUES(1,NULL,'',NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "materials" VALUES(2,'1234','Pierre Mg-20 DB','tm',15.0,'Pierre MG-20 DB',NULL,NULL,'2025-01-07',NULL);
INSERT INTO "materials" VALUES(3,'4567','Tuyaux pvc sdr-35 250mm diam','ml',35.0,'Tuyaux pvc sdr-35 250mm diam',NULL,NULL,'2025-01-07',NULL);
CREATE TABLE "payment_items" (
	"id"	INTEGER NOT NULL,
	"project_id"	INTEGER NOT NULL,
	"payment_code"	VARCHAR(50) NOT NULL,
	"activity_code_id"	INTEGER NOT NULL,
	"task_id"	INTEGER,
	"item_name"	VARCHAR(255) NOT NULL,
	"unit"	VARCHAR(50),
	"rate_per_unit"	FLOAT,
	"created_at"	DATETIME,
	PRIMARY KEY("id"),
	FOREIGN KEY("activity_code_id") REFERENCES "activity_codes"("id"),
	CONSTRAINT "fk_payment_items_project_id" FOREIGN KEY("project_id") REFERENCES "projects"("id"),
	FOREIGN KEY("task_id") REFERENCES "project_tasks"("id")
);
INSERT INTO "payment_items" VALUES(1,3,'1.01',2,2,'Mobilisation et gestion du projet','glob',25000.0,'2025-01-06');
INSERT INTO "payment_items" VALUES(2,3,'2.01',4,3,'Excavation et remblayage','m3',35.0,'2025-01-07');
INSERT INTO "payment_items" VALUES(3,3,'3.01',6,3,'Egouts et aqueducs','ml',225.0,'2025-01-06');
INSERT INTO "payment_items" VALUES(4,4,'1,01',2,2,'Mobilisation de chantier','glob',25000.0,'2025-01-06');
INSERT INTO "payment_items" VALUES(5,4,'2,01',7,3,'conduites eqgouts et aqueducs','ml',325.0,'2025-01-06');
CREATE TABLE "project_tasks" (
	id INTEGER NOT NULL, 
	project_id INTEGER NOT NULL, 
	name VARCHAR(255) NOT NULL, 
	activity_code_id INTEGER NOT NULL, 
	start_date DATE, 
	end_date DATE, 
	status VARCHAR(11), 
	progress FLOAT, 
	man_hour_budget FLOAT, 
	man_hours FLOAT, 
	unit VARCHAR(50), 
	qte FLOAT, 
	"PV" FLOAT, 
	"EV" FLOAT, 
	"AC" FLOAT, 
	"CV" FLOAT, 
	"SV" FLOAT, 
	"VAC" FLOAT, 
	"CPI" FLOAT, 
	"SPI" FLOAT, 
	"EAC" FLOAT, 
	"ETC" FLOAT, 
	"TCPI" FLOAT, 
	"CWP" VARCHAR(100), 
	specialty VARCHAR(100), 
	created_at DATETIME, 
	updated_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(project_id) REFERENCES projects (id), 
	FOREIGN KEY(activity_code_id) REFERENCES activity_codes (id)
);
INSERT INTO "project_tasks" VALUES(1,3,'excavation de masse',6,'2025-01-07','2025-01-30',NULL,0.0,1000.0,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-01-06',NULL);
INSERT INTO "project_tasks" VALUES(2,3,'mobilisation du chantie',2,'2025-01-06','2025-01-07',NULL,0.0,200.0,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,' ','2025-01-06',NULL);
INSERT INTO "project_tasks" VALUES(3,4,'Mobilisation de chantier',2,NULL,NULL,NULL,0.0,200.0,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-01-06',NULL);
CREATE TABLE projects (
	id INTEGER NOT NULL, 
	name VARCHAR(255) NOT NULL, 
	description VARCHAR(500), 
	project_number VARCHAR(50) NOT NULL, 
	category VARCHAR(100) NOT NULL, 
	status VARCHAR(11), 
	client_name VARCHAR(255), 
	project_manager VARCHAR(255), 
	address VARCHAR(255), 
	budget FLOAT, 
	original_budget FLOAT, 
	revised_budget FLOAT, 
	contingency_fund FLOAT, 
	risk_level VARCHAR(6), 
	risk_notes TEXT, 
	map_url VARCHAR(2083), 
	latitude FLOAT, 
	longitude FLOAT, 
	picture_url VARCHAR(2083), 
	video_capture_url VARCHAR(2083), 
	start_date DATE, 
	end_date DATE, 
	notes TEXT, 
	plan_repository_url VARCHAR(2083), 
	sustainability_rating VARCHAR(8), 
	sustainability_goals TEXT, 
	collaboration_url VARCHAR(2083), 
	integration_status BOOLEAN, 
	audit_due_date DATE, 
	compliance_status VARCHAR(13), 
	local_hires INTEGER, 
	community_engagement_notes TEXT, 
	previous_project_id INTEGER, 
	benchmark_cost_per_unit FLOAT, 
	tags JSON, 
	critical_path_duration INTEGER, 
	key_milestones JSON, 
	safety_incidents INTEGER, 
	incident_notes TEXT, 
	bim_file_url VARCHAR(2083), 
	bim_model_id VARCHAR(255), 
	created_at DATETIME, 
	updated_at DATETIME, 
	updated_by VARCHAR(255), 
	PRIMARY KEY (id), 
	FOREIGN KEY(previous_project_id) REFERENCES projects (id), 
	UNIQUE (name)
);
INSERT INTO "projects" VALUES(1,'',NULL,'','',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "projects" VALUES(2,'Saint_constant','Projet Test de la base de donne','25-101','Civil','in_progress','PP','PP',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-01-06','2025-01-30',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "projects" VALUES(3,'Nemaska Lithium','CC004','24-408','Industrial','in_progress','Nemaska Lithium','Pascal P','5600 rue Louis Riel, Becancour',3500000.0,3500000.0,3200000.0,100000.0,'low','Transport en degel a verifier','https://www.google.com/maps/place/5600+Chem.+Louis+Riel,+Champlain,+QC+G0X+1C0/@46.3630582,-72.394569,750m/data=!3m2!1e3!4b1!4m5!3m4!1s0x4cc7c0e7d302276f:0x563a21cc7283cf0b!8m2!3d46.3630545!4d-72.3919941?authuser=0&entry=ttu&g_ep=EgoyMDI1MDEwMi4wIKXMDSoASAFQAw%3D%3D',46.36315,-72.39198,NULL,NULL,'2024-08-01','2025-08-01',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2024-08-01','2025-01-07','Pascal Patrice');
INSERT INTO "projects" VALUES(4,'Bureau Montreal','Test avec adresse bureau de Montreal','24-410','commercial','in_progress',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "projects" VALUES(5,'Air-Liquide','Terrassements air Liquide','24-413','Industriel','in_progress','Talvi','Pascal P','7000 Rue Yvon Trudeau, Bécancour, QC G9H 2V9',1100000.0,1100000.0,1000000.0,50000.0,'low','paiement issues','https://www.google.com/maps/place/Metallurgistes+D''Amerique/@46.3623124,-72.4030052,909m/data=!3m1!1e3!4m6!3m5!1s0x4cc7c0dca62a823d:0x135b227d3710e799!8m2!3d46.363948!4d-72.400882!16s%2Fg%2F11b5wmjjj8?authuser=0&entry=ttu&g_ep=EgoyMDI1MDEyOS4xIKXMDSoASAFQAw%3D%3D',46.36408,-72.40047,NULL,NULL,'2025-01-06','2025-06-30',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,120,NULL,NULL,NULL,NULL,NULL,NULL,'2025-02-03','Pascal P');
CREATE TABLE purchase_order_attachments (
	id INTEGER NOT NULL, 
	po_id INTEGER NOT NULL, 
	file_name VARCHAR(255) NOT NULL, 
	file_url VARCHAR(2083) NOT NULL, 
	uploaded_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(po_id) REFERENCES purchase_orders (id)
);
CREATE TABLE "purchase_orders" (
	id INTEGER NOT NULL, 
	po_id INTEGER, 
	order_number VARCHAR(50) NOT NULL, 
	vendor VARCHAR(255) NOT NULL, 
	vendor_address VARCHAR(255), 
	vendor_phone VARCHAR(50), 
	vendor_general_email VARCHAR(255), 
	vendor_accounting_email VARCHAR(255), 
	vendor_contact_name VARCHAR(255), 
	vendor_contact_phone VARCHAR(50), 
	vendor_contact_email VARCHAR(255), 
	project_id INTEGER, 
	equipment_id VARCHAR(100), 
	worker_id INTEGER, 
	subcontractor_id INTEGER, 
	service_name VARCHAR(255), 
	activity_code_id INTEGER, 
	task_id INTEGER, 
	quantity_purchased FLOAT, 
	unit_price FLOAT, 
	total_cost FLOAT, 
	procurement_group VARCHAR(6), 
	procurement_type VARCHAR(13), 
	delivery_date DATE, 
	delivery_location VARCHAR(255), 
	link_to_supplier_quote VARCHAR(2083), 
	quantity_consumed FLOAT, 
	delivery_compliance VARCHAR(13), 
	attachments JSON, 
	is_change_order BOOLEAN, 
	linked_po_id INTEGER, 
	on_site_status VARCHAR(9), 
	created_at DATETIME, 
	updated_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(worker_id) REFERENCES workers (id), 
	FOREIGN KEY(subcontractor_id) REFERENCES subcontractors (id), 
	FOREIGN KEY(linked_po_id) REFERENCES purchase_orders (id), 
	UNIQUE (order_number), 
	FOREIGN KEY(po_id) REFERENCES purchase_orders (id), 
	FOREIGN KEY(equipment_id) REFERENCES equipment (equipment_id), 
	FOREIGN KEY(task_id) REFERENCES project_tasks (id), 
	FOREIGN KEY(activity_code_id) REFERENCES activity_codes (id), 
	FOREIGN KEY(project_id) REFERENCES projects (id)
);
INSERT INTO "purchase_orders" VALUES(1,NULL,'','',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "purchase_orders" VALUES(2,NULL,'24401001','PCM',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,10000.0,15.0,150000.0,'Materials','Units',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-01-07',NULL);
INSERT INTO "purchase_orders" VALUES(3,NULL,'24401002','Emco',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,100.0,35.0,3500.0,'Materials','unit',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
CREATE TABLE "subcontractor_entries" (
	id INTEGER NOT NULL, 
	subcontractor_id INTEGER NOT NULL, 
	project_id INTEGER NOT NULL, 
	task_id INTEGER, 
	work_order_id INTEGER, 
	date DATE, 
	description TEXT, 
	equipment_hours FLOAT, 
	material_cost FLOAT, 
	labor_hours FLOAT, 
	total_cost FLOAT, 
	progress_percentage FLOAT, 
	created_at DATETIME, 
	updated_at DATETIME, 
	status VARCHAR(11), 
	activity_code_id INTEGER, 
	PRIMARY KEY (id), 
	CONSTRAINT fk_subcontractor_entries_activity_code FOREIGN KEY(activity_code_id) REFERENCES activity_codes (id), 
	FOREIGN KEY(project_id) REFERENCES projects (id), 
	FOREIGN KEY(subcontractor_id) REFERENCES subcontractors (id), 
	FOREIGN KEY(task_id) REFERENCES project_tasks (id), 
	FOREIGN KEY(work_order_id) REFERENCES work_orders (id)
);
INSERT INTO "subcontractor_entries" VALUES(1,2,3,3,NULL,NULL,'installation cable chauffant',NULL,NULL,10.0,NULL,NULL,NULL,NULL,NULL,2);
CREATE TABLE "subcontractors" (
	id INTEGER NOT NULL, 
	project_id INTEGER, 
	name VARCHAR(255) NOT NULL, 
	task VARCHAR(255), 
	contract_type VARCHAR(18), 
	total_contract_value FLOAT, 
	progress_percentage FLOAT, 
	payment_status VARCHAR(7), 
	payment_terms VARCHAR(255), 
	last_payment_date DATE, 
	cost_plus_total FLOAT, 
	created_at DATETIME, 
	updated_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(project_id) REFERENCES projects (id)
);
INSERT INTO "subcontractors" VALUES(1,NULL,'',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "subcontractors" VALUES(2,NULL,'Lemteck electrique',NULL,NULL,50000.0,NULL,NULL,NULL,NULL,NULL,'2025-01-07',NULL);
INSERT INTO "subcontractors" VALUES(3,NULL,'Signalitik',NULL,'forf',15000.0,NULL,NULL,NULL,NULL,NULL,'2025-01-07',NULL);
CREATE TABLE sustainability_metrics (
	id INTEGER NOT NULL, 
	project_id INTEGER, 
	task_id INTEGER, 
	metric_name VARCHAR(255) NOT NULL, 
	category VARCHAR(9), 
	value FLOAT NOT NULL, 
	unit VARCHAR(50) NOT NULL, 
	threshold FLOAT, 
	target_value FLOAT, 
	deviation FLOAT, 
	triggered_alert BOOLEAN, 
	recorded_at DATETIME, 
	recorded_by VARCHAR(255), 
	notes TEXT, 
	PRIMARY KEY (id), 
	FOREIGN KEY(project_id) REFERENCES projects (id), 
	FOREIGN KEY(task_id) REFERENCES project_tasks (id)
);
CREATE TABLE tab_progress (
	id INTEGER NOT NULL, 
	project_id INTEGER NOT NULL, 
	date DATE NOT NULL, 
	tab_name VARCHAR(50) NOT NULL, 
	status VARCHAR(10), 
	progress_percentage FLOAT, 
	is_locked BOOLEAN, 
	status_history JSON, 
	tab_notes TEXT, 
	last_updated_by VARCHAR(255), 
	reviewed_by VARCHAR(255), 
	created_at DATETIME, 
	last_updated_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(project_id) REFERENCES projects (id)
);
INSERT INTO "tab_progress" VALUES(1,3,'2025-01-06','workers','completed',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "tab_progress" VALUES(2,2,'2025-01-06','workers','completed',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "tab_progress" VALUES(3,4,'2025-01-06','workers','in_progress',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
CREATE TABLE weather_logs (
	id INTEGER NOT NULL, 
	project_id INTEGER NOT NULL, 
	date DATE NOT NULL, 
	temperature FLOAT, 
	humidity FLOAT, 
	wind_speed FLOAT, 
	description VARCHAR(255), 
	severity VARCHAR(6), 
	work_impact VARCHAR(13), 
	delay_reason TEXT, 
	hours_lost FLOAT, 
	impacted_activity_codes JSON, 
	api_data JSON, 
	trend VARCHAR(50), 
	predicted_hours_lost FLOAT, 
	PRIMARY KEY (id), 
	FOREIGN KEY(project_id) REFERENCES projects (id)
);
INSERT INTO "weather_logs" VALUES(1,3,'2025-01-07',-15.0,35.0,15.0,'nuageux et averses de neige','low','deneigement',NULL,2.0,31000,NULL,NULL,2.0);
CREATE TABLE "work_order_entries" (
	id INTEGER NOT NULL, 
	work_order_id INTEGER NOT NULL, 
	worker_id INTEGER, 
	task_id INTEGER, 
	activity_code_id INTEGER NOT NULL, 
	hours_worked FLOAT, 
	date DATE, 
	description TEXT, 
	labor_cost FLOAT, 
	equipement_cost FLOAT, 
	subcontractor_cost FLOAT, 
	service_cost FLOAT, 
	total_cost FLOAT, 
	progress_percentage FLOAT, 
	created_at DATETIME, 
	updated_at DATETIME, 
	updated_by VARCHAR(50), 
	status VARCHAR(11), 
	PRIMARY KEY (id), 
	FOREIGN KEY(worker_id) REFERENCES workers (id), 
	FOREIGN KEY(task_id) REFERENCES project_tasks (id), 
	FOREIGN KEY(activity_code_id) REFERENCES activity_codes (id), 
	FOREIGN KEY(work_order_id) REFERENCES work_orders (id)
);
INSERT INTO "work_order_entries" VALUES(1,1,2,NULL,8,10.0,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
CREATE TABLE work_order_entry_attachments (
	id INTEGER NOT NULL, 
	entry_id INTEGER NOT NULL, 
	file_path VARCHAR(255) NOT NULL, 
	description VARCHAR(255), 
	doc_type VARCHAR(50), 
	uploaded_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(entry_id) REFERENCES work_order_entries (id)
);
CREATE TABLE work_orders (
	id INTEGER NOT NULL, 
	project_id INTEGER NOT NULL, 
	sequential_number VARCHAR(10) NOT NULL, 
	work_order_number INTEGER, 
	description VARCHAR(255) NOT NULL, 
	subcontractor_id INTEGER, 
	type VARCHAR(16) NOT NULL, 
	status VARCHAR(11), 
	reason VARCHAR(255), 
	estimated_cost FLOAT, 
	cumulative_actual_cost FLOAT, 
	activity_code_id INTEGER, 
	start_date DATE, 
	expected_completion_date DATE, 
	requested_date DATE, 
	approved_date DATE, 
	completed_date DATE, 
	activity_code VARCHAR(50), 
	created_at DATETIME, 
	updated_at DATETIME, progress_percentage FLOAT, 
	PRIMARY KEY (id), 
	FOREIGN KEY(activity_code_id) REFERENCES activity_codes (id), 
	FOREIGN KEY(project_id) REFERENCES projects (id), 
	FOREIGN KEY(subcontractor_id) REFERENCES subcontractors (id), 
	FOREIGN KEY(work_order_number) REFERENCES work_orders (id), 
	UNIQUE (activity_code), 
	UNIQUE (sequential_number)
);
INSERT INTO "work_orders" VALUES(1,3,'80001',NULL,'Deplacement des roulottes de chantier',NULL,'forfaitaire','debuter',NULL,5000.0,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
CREATE TABLE "workers" (
	id INTEGER NOT NULL, 
	name VARCHAR(255) NOT NULL, 
	genre VARCHAR(6), 
	worker_id VARCHAR(50) NOT NULL, 
	project_id INTEGER, 
	code_postal VARCHAR(10), 
	num_cell VARCHAR(15), 
	courriel VARCHAR(255), 
	certifications JSON, 
	experience_years INTEGER, 
	password_hash VARCHAR(255), 
	last_login DATETIME, 
	login_attempts INTEGER, 
	metier VARCHAR(100), 
	convention VARCHAR(100), 
	taux_horaire FLOAT, 
	taux_over FLOAT, 
	"Gite_couvert" FLOAT, 
	transp_1 FLOAT, 
	transp_2 FLOAT, 
	equip_asso VARCHAR(255), 
	departement VARCHAR(100), 
	role VARCHAR(14), 
	is_active BOOLEAN NOT NULL, 
	created_at DATETIME, 
	updated_at DATETIME, 
	updated_by VARCHAR(255), 
	PRIMARY KEY (id), 
	CONSTRAINT fk_worker_project FOREIGN KEY(project_id) REFERENCES projects (id), 
	UNIQUE (courriel), 
	UNIQUE (worker_id)
);
INSERT INTO "workers" VALUES(1,'',NULL,'',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'',NULL,NULL,NULL);
INSERT INTO "workers" VALUES(2,'Joe Lapelle','male','1234',NULL,NULL,'514-892-6501','p.patrice@nationalinc.ca','CCQ',30,NULL,NULL,NULL,'operateur','Civil annexe B-1',75.0,150.0,200.0,75.0,90.0,'BU-06','Genie civil','employe','true','2025-01-06',NULL,NULL);
INSERT INTO "workers" VALUES(3,'Serge le chargeur','male','4567',NULL,NULL,'514-892-6501','p.patrice2nationalinc.ca',NULL,15,NULL,NULL,NULL,'operateur','genie civil annexe b1',75.0,150.0,200.0,75.0,90.0,'L-25','genie civil','employee','true','2025-01-06',NULL,NULL);
CREATE INDEX ix_projects_category ON projects (category);
CREATE INDEX ix_projects_end_date ON projects (end_date);
CREATE UNIQUE INDEX ix_projects_project_number ON projects (project_number);
CREATE INDEX ix_projects_start_date ON projects (start_date);
CREATE INDEX ix_projects_status ON projects (status);
CREATE UNIQUE INDEX ix_activity_codes_code ON activity_codes (code);
CREATE INDEX ix_entries_equipment_date_of_report ON entries_equipment (date_of_report);
CREATE INDEX ix_entries_workers_date_of_report ON entries_workers (date_of_report);
CREATE INDEX ix_payment_items_item_name ON payment_items (item_name);
CREATE UNIQUE INDEX ix_payment_items_payment_code ON payment_items (payment_code);
COMMIT;
